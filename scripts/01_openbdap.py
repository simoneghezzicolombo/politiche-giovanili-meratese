"""Estrae M06-P02 e spesa corrente dal rendiconto OpenBDAP/RGS.

Per gli ZIP regionali FET lo script legge intenzionalmente il prospetto
`Rendiconto SDB Spese`, che contiene una riga per ente, missione, programma e
titolo. Non concatena gli altri prospetti dello ZIP, perché hanno schemi e
livelli di aggregazione diversi e produrrebbero doppi conteggi.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import sys
import zipfile

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    canonical_municipality,
    ensure_parent,
    find_column,
    norm_code,
    norm_text,
    read_table,
)

YEAR = 2024
MISSION = "06"
PROGRAM = "02"

ALIASES = {
    "comune": [
        "denominazione soggetto", "denominazione ente", "ente", "comune",
        "denominazione comune", "nome ente",
    ],
    "tipo_ente": [
        "descrizione tipologia soggetto", "tipo ente", "tipologia ente",
        "comparto", "tipo amministrazione",
    ],
    "anno": ["esercizio finanziario", "anno", "esercizio", "anno esercizio"],
    "missione": [
        "codice missione arconet", "codice missione", "cod missione",
        "missione codice", "missione",
    ],
    "programma": [
        "codice programma arconet", "codice programma", "cod programma",
        "programma codice", "programma",
    ],
    "titolo": [
        "codice titolo spese arconet", "codice titolo", "cod titolo",
        "titolo codice", "titolo",
    ],
    "impegni": [
        "impegni", "impegni riepilogo", "impegni esercizio",
        "impegni competenza", "impegni di competenza",
    ],
}


def numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").fillna(0.0)
    text = series.astype(str).str.strip()
    has_comma = text.str.contains(",", regex=False).any()
    if has_comma:
        text = text.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    text = text.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce").fillna(0.0)


def _read_csv_bytes(data: bytes) -> pd.DataFrame:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=encoding)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"{encoding}: {exc}")
    raise ValueError("Impossibile leggere il CSV FET. " + " | ".join(errors))


def select_fet_spese_member(names: list[str]) -> str:
    """Trova il prospetto analitico `Rendiconto SDB Spese_<REGIONE>.csv`."""
    candidates: list[str] = []
    for name in names:
        if not name.lower().endswith(".csv"):
            continue
        base = Path(name).name
        normal = norm_text(base)
        if "rendiconto sdb spese" not in normal:
            continue
        forbidden = (
            "riepilogo", "allegato", "quadro generale", "voce di riepilogo",
            "correnti per macroaggregato", "conto capitale per macroaggregato",
            "rimborso di prestiti", "servizi conto terzi",
        )
        if any(token in normal for token in forbidden):
            continue
        if re.search(r"\brendiconto sdb spese\b", normal):
            candidates.append(name)

    if len(candidates) != 1:
        shown = "\n".join(sorted(candidates)[:20]) or "(nessuno)"
        raise ValueError(
            "Impossibile identificare univocamente il prospetto FET `Rendiconto SDB Spese`. "
            f"Candidati: {len(candidates)}\n{shown}"
        )
    return candidates[0]


def read_spese_table(source: str | Path) -> tuple[pd.DataFrame, str]:
    source_str = str(source)
    if source_str.lower().endswith(".zip"):
        with zipfile.ZipFile(source) as archive:
            member = select_fet_spese_member(archive.namelist())
            return _read_csv_bytes(archive.read(member)), member
    return read_table(source), Path(source_str).name


def detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    cols: dict[str, str | None] = {}
    for key, aliases in ALIASES.items():
        cols[key] = find_column(
            df.columns,
            aliases,
            required=key in {"comune", "missione", "programma", "titolo", "impegni"},
        )
    return cols


def prepare(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str | None]]:
    cols = detect_columns(df)

    if cols.get("anno"):
        years = df[cols["anno"]].map(norm_code)
        if (years == str(YEAR)).any():
            df = df.loc[years == str(YEAR)].copy()

    if cols.get("tipo_ente"):
        tipo = df[cols["tipo_ente"]].map(norm_text)
        # Gli ZIP FET regionali includono anche Unioni di Comuni e Comunità
        # montane. Se la categoria esatta "Comune" è presente, usiamo solo
        # quella e non un generico contains("comun").
        exact_mask = tipo.eq("comune")
        if exact_mask.any():
            df = df.loc[exact_mask].copy()
        else:
            fallback_mask = tipo.str.contains(r"\bcomune\b", regex=True, na=False)
            if fallback_mask.any():
                df = df.loc[fallback_mask].copy()

    df["_comune_key"] = df[cols["comune"]].map(canonical_municipality)
    df["_comune_label"] = df[cols["comune"]].astype(str).str.strip()
    df["_missione"] = df[cols["missione"]].map(lambda x: norm_code(x, 2))
    df["_programma"] = df[cols["programma"]].map(lambda x: norm_code(x, 2))
    df["_titolo"] = df[cols["titolo"]].map(lambda x: norm_code(x, 2))
    df["_impegni"] = numeric(df[cols["impegni"]])

    keys = ["_comune_key", "_missione", "_programma", "_titolo"]
    duplicated = df.duplicated(keys, keep=False)
    if duplicated.any():
        sample = df.loc[duplicated, keys].drop_duplicates().head(10).to_dict("records")
        raise ValueError(
            "Il prospetto `Spese` contiene più righe per ente/missione/programma/titolo; "
            f"schema da riesaminare. Esempi: {sample}"
        )

    return df, cols


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    m0602 = df[(df["_missione"] == MISSION) & (df["_programma"] == PROGRAM)].copy()

    current = (
        m0602[m0602["_titolo"] == "01"].groupby("_comune_key", as_index=False)["_impegni"].sum()
        .rename(columns={"_impegni": "m0602_corrente_impegni"})
    )
    capital = (
        m0602[m0602["_titolo"] == "02"].groupby("_comune_key", as_index=False)["_impegni"].sum()
        .rename(columns={"_impegni": "m0602_capitale_impegni"})
    )
    total_current = (
        df[df["_titolo"] == "01"].groupby("_comune_key", as_index=False)["_impegni"].sum()
        .rename(columns={"_impegni": "spesa_corrente_totale_impegni"})
    )
    labels = df.groupby("_comune_key", as_index=False)["_comune_label"].first()

    out = labels.merge(total_current, on="_comune_key", how="left")
    out = out.merge(current, on="_comune_key", how="left").merge(capital, on="_comune_key", how="left")
    for col in ["m0602_corrente_impegni", "m0602_capitale_impegni"]:
        out[col] = out[col].fillna(0.0)
    out = out.rename(columns={"_comune_key": "comune_key", "_comune_label": "comune_fonte"})
    out["anno"] = YEAR
    return out[[
        "comune_key", "comune_fonte", "anno", "m0602_corrente_impegni",
        "m0602_capitale_impegni", "spesa_corrente_totale_impegni",
    ]].sort_values("comune_key")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV/XLSX/ZIP ufficiale OpenBDAP/RGS")
    parser.add_argument("--output", default="data/interim/openbdap_2024_comuni.csv")
    parser.add_argument("--columns-report", default="data/interim/openbdap_2024_columns.txt")
    args = parser.parse_args()

    try:
        raw, member = read_spese_table(args.input)
        prepared, cols = prepare(raw)
    except (KeyError, ValueError) as exc:
        report = ensure_parent(args.columns_report)
        columns = list(raw.columns) if "raw" in locals() else []
        report.write_text("\n".join(map(str, columns)), encoding="utf-8")
        raise SystemExit(f"Schema OpenBDAP non riconosciuto: {exc}\nColonne salvate in {report}")

    out = aggregate(prepared)
    if len(out) < 1000:
        raise SystemExit(
            f"Controllo di sicurezza fallito: trovati solo {len(out)} Comuni nel prospetto."
        )

    path = ensure_parent(args.output)
    out.to_csv(path, index=False)
    print(f"Prospetto usato: {member}")
    print(f"Salvati {len(out):,} Comuni in {path}")
    print("Colonne riconosciute:")
    for key, value in cols.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
