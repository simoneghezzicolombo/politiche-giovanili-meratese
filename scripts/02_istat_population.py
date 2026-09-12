"""Costruisce popolazione totale e 15-29 dai file ufficiali demo.istat.it.

Il file POSAS comunale ufficiale contiene una riga descrittiva prima
dell'intestazione tabellare. Il codice Istat del Comune viene conservato per
evitare di fondere Comuni omonimi presenti in regioni diverse.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import sys
import zipfile

import pandas as pd
import requests

sys.path.append(str(Path(__file__).resolve().parent))
from _common import canonical_municipality, ensure_parent, find_column, norm_code, norm_text, read_table  # noqa: E402

DEFAULT_URL = "https://demo.istat.it/data/posas/POSAS_2024_it_Comuni.zip"

ALIASES = {
    "codice": ["codice comune", "codice istat comune", "codice comune istat"],
    "comune": ["comune", "denominazione comune", "nome comune", "comune descrizione"],
    "eta": ["eta", "età", "eta anni", "classe eta"],
    "sesso": ["sesso", "sex"],
    "valore": ["totale", "popolazione", "residenti", "valore", "value"],
    "anno": ["anno", "year"],
}


def parse_age(value: object) -> int | None:
    text = norm_text(value)
    if not text:
        return None
    if "100" in text and ("oltre" in text or "+" in str(value)):
        return 100
    match = re.search(r"\b(\d{1,3})\b", text)
    return int(match.group(1)) if match else None


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9\-]", "", regex=True), errors="coerce").fillna(0)


def _source_bytes(source: str | Path) -> tuple[bytes, str]:
    source_str = str(source)
    if re.match(r"^https?://", source_str):
        response = requests.get(source_str, timeout=120)
        response.raise_for_status()
        return response.content, source_str.split("?")[0].rstrip("/").split("/")[-1]
    path = Path(source)
    return path.read_bytes(), path.name


def _read_posas_csv(data: bytes) -> pd.DataFrame:
    """Legge il CSV POSAS, individuando l'intestazione dopo la riga titolo."""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue

        lines = text.splitlines()
        header_idx = None
        for i, line in enumerate(lines[:10]):
            normal = norm_text(line)
            if "codice comune" in normal and "comune" in normal and "eta" in normal:
                header_idx = i
                break
        if header_idx is None:
            continue

        try:
            return pd.read_csv(
                io.StringIO(text),
                sep=";",
                header=header_idx,
                dtype={"Codice comune": "string"},
                low_memory=False,
            )
        except Exception:
            continue

    raise ValueError("Schema CSV POSAS non riconosciuto: intestazione comunale non trovata o non leggibile.")


def read_posas_table(source: str | Path) -> pd.DataFrame:
    data, name = _source_bytes(source)
    if name.lower().endswith(".zip") or data[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = [
                m for m in archive.namelist()
                if m.lower().endswith(".csv") and not m.startswith("__MACOSX")
            ]
            if len(members) != 1:
                raise ValueError(
                    "Archivio POSAS inatteso: atteso un solo CSV, "
                    f"trovati {len(members)} ({members[:10]})."
                )
            return _read_posas_csv(archive.read(members[0]))

    if name.lower().endswith((".csv", ".txt")):
        return _read_posas_csv(data)

    return read_table(source)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_URL, help="CSV/ZIP Istat; default: POSAS 2024 Comuni ufficiale")
    parser.add_argument("--year", type=int, default=2024, help="Anno della popolazione al 1° gennaio")
    parser.add_argument("--output", default="data/interim/istat_pop_2024.csv")
    args = parser.parse_args()

    df = read_posas_table(args.input)
    codice = find_column(df.columns, ALIASES["codice"])
    comune = find_column(df.columns, ALIASES["comune"])
    eta = find_column(df.columns, ALIASES["eta"])
    sesso = find_column(df.columns, ALIASES["sesso"], required=False)
    valore = find_column(df.columns, ALIASES["valore"])
    anno = find_column(df.columns, ALIASES["anno"], required=False)

    if anno:
        years = pd.to_numeric(df[anno], errors="coerce")
        if (years == args.year).any():
            df = df.loc[years == args.year].copy()

    df["_age"] = df[eta].map(parse_age)
    df = df[df["_age"].notna()].copy()
    df["_age"] = df["_age"].astype(int)
    df["_pop"] = numeric(df[valore])
    df["codice_comune"] = df[codice].map(lambda x: norm_code(x, 6))
    df["comune_key"] = df[comune].map(canonical_municipality)

    if sesso:
        sex_norm = df[sesso].map(norm_text)
        total_mask = sex_norm.isin({"totale", "tot", "t", "total"})
        if total_mask.any():
            df = df.loc[total_mask].copy()

    id_cols = ["codice_comune", "comune_key"]
    age = df.groupby(id_cols + ["_age"], as_index=False)["_pop"].sum()

    total_rows = age[age["_age"] == 999]
    if not total_rows.empty:
        total = total_rows[id_cols + ["_pop"]].rename(columns={"_pop": "pop_totale"})
    else:
        total = (
            age[age["_age"] < 999]
            .groupby(id_cols, as_index=False)["_pop"].sum()
            .rename(columns={"_pop": "pop_totale"})
        )

    youth = (
        age[age["_age"].between(15, 29)]
        .groupby(id_cols, as_index=False)["_pop"].sum()
        .rename(columns={"_pop": "pop_15_29"})
    )
    out = total.merge(youth, on=id_cols, how="left")
    out["pop_15_29"] = out["pop_15_29"].fillna(0).astype(int)
    out["pop_totale"] = out["pop_totale"].astype(int)
    out["pop_data_riferimento"] = f"{args.year}-01-01"

    if len(out) < 7000:
        raise SystemExit(f"Controllo di sicurezza fallito: trovati solo {len(out)} comuni nel POSAS.")
    if out["codice_comune"].duplicated().any():
        raise SystemExit("Controllo di sicurezza fallito: codici Istat comunali duplicati.")
    if (out["pop_totale"] <= 0).any():
        raise SystemExit("Controllo di sicurezza fallito: popolazioni comunali non positive.")

    path = ensure_parent(args.output)
    out.sort_values("codice_comune").to_csv(path, index=False)
    print(f"Salvati {len(out):,} comuni in {path}")
    print(f"Popolazione totale nazionale nel file: {out['pop_totale'].sum():,.0f}")


if __name__ == "__main__":
    main()
