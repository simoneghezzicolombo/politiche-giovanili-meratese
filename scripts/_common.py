from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


def norm_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("’", "'").replace("`", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", " ", text).strip().lower()
    return re.sub(r"\s+", " ", text)


def norm_code(value: object, width: int | None = None) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    if not digits:
        return norm_text(text)
    return digits.zfill(width) if width else digits


def find_column(columns: Iterable[str], aliases: Iterable[str], required: bool = True) -> str | None:
    norm_to_original = {norm_text(c): c for c in columns}
    alias_norm = [norm_text(a) for a in aliases]

    for alias in alias_norm:
        if alias in norm_to_original:
            return norm_to_original[alias]

    for alias in alias_norm:
        candidates = [orig for n, orig in norm_to_original.items() if alias and alias in n]
        if len(candidates) == 1:
            return candidates[0]

    if required:
        raise KeyError(
            "Colonna non trovata. Cercavo uno di: "
            + ", ".join(aliases)
            + ". Colonne disponibili: "
            + ", ".join(map(str, columns))
        )
    return None


def _read_csv_bytes(data: bytes) -> pd.DataFrame:
    errors = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=encoding)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"{encoding}: {exc}")
    raise ValueError("Impossibile leggere il CSV. " + " | ".join(errors))


def _read_single(name: str, data: bytes) -> pd.DataFrame:
    lower = name.lower()
    if lower.endswith((".csv", ".txt")):
        return _read_csv_bytes(data)
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(data))
    raise ValueError(f"Formato non supportato: {name}")


def read_table(source: str | Path) -> pd.DataFrame:
    """Legge CSV/XLSX o ZIP contenente tabelle e concatena i file compatibili."""
    source_str = str(source)
    if re.match(r"^https?://", source_str):
        response = requests.get(source_str, timeout=90)
        response.raise_for_status()
        data = response.content
        name = source_str.split("?")[0].rstrip("/").split("/")[-1] or "download"
    else:
        path = Path(source)
        data = path.read_bytes()
        name = path.name

    if name.lower().endswith(".zip") or data[:4] == b"PK\x03\x04":
        frames = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.namelist():
                if member.lower().endswith((".csv", ".txt", ".xlsx", ".xls")) and not member.startswith("__MACOSX"):
                    try:
                        frame = _read_single(member, archive.read(member))
                        frame["__source_file"] = member
                        frames.append(frame)
                    except Exception:
                        continue
        if not frames:
            raise ValueError("Lo ZIP non contiene CSV/XLSX leggibili.")
        return pd.concat(frames, ignore_index=True, sort=False)

    return _read_single(name, data)


def canonical_municipality(value: object) -> str:
    text = norm_text(value)
    # prefissi frequenti nei file amministrativi
    text = re.sub(r"^(comune di|comune|citta di)\s+", "", text).strip()
    return text


def ensure_parent(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
