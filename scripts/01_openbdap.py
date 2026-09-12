"""Estrae M06-P02 e spesa corrente dai dati ufficiali di rendiconto OpenBDAP/RGS.

Lo script non dipende dalla UI del portale: accetta un CSV/XLSX/ZIP ufficiale già
scaricato da OpenBDAP. È intenzionalmente severo: se non riconosce lo schema,
si ferma invece di produrre numeri potenzialmente sbagliati.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

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
    "comune": ["denominazione ente", "ente", "comune", "denominazione comune", "nome ente"],
    "tipo_ente": ["tipo ente", "tipologia ente", "comparto", "tipo amministrazione"],
    "anno": ["anno", "esercizio", "esercizio finanziario", "anno esercizio"],
    "missione": ["codice missione", "cod missione", "missione codice", "missione"],
    "programma": ["codice programma", "cod programma", "programma codice", "programma"],
    "titolo": ["codice titolo", "cod titolo", "titolo codice", "titolo"],
    "macro": ["codice macroaggregato", "cod macroaggregato", "macroaggregato codice", "macroaggregato"],
    "impegni": ["impegni", "impegni esercizio", "impegni competenza", "impegni di competenza"],
}


def numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").fillna(0.0)
    text = series.astype(str).str.strip()
    # formato italiano: 1.234,56. Se non ci sono virgole, lascia il punto decimale.
    has_comma = text.str.contains(",", regex=False).any()
    if has_comma:
        text = text.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    text = text.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce").fillna(0.0)


def detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    cols: dict[str, str | None] = {}
    for key, aliases in ALIASES.items():
        cols[key] = find_column(
            df.columns,
            aliases,
            required=key in {"comune", "missione", "programma", "titolo", "impegni"},
        )
    return cols


def filter_additive_rows(df: pd.DataFrame, cols: dict[str, str | None]) -> pd.DataFrame:
    """Riduce il rischio di doppio conteggio quando il file contiene subtotali.

    Se esiste il macroaggregato e sono presenti righe con codice valorizzato,
    usa quelle come componenti additive ed esclude le righe di totale senza codice.
    """
    macro = cols.get("macro")
    if macro:
        codes = df[macro].map(norm_code)
        if (codes != "").any():
            df = df.loc[codes != ""].copy()
    return df


def prepare(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str | None]]:
    cols = detect_columns(df)

    if cols.get("anno"):
        years = df[cols["anno"]].map(lambda x: norm_code(x))
        if (years == str(YEAR)).any():
            df = df.loc[years == str(YEAR)].copy()

    if cols.get("tipo_ente"):
        tipo = df[cols["tipo_ente"]].map(norm_text)
        comune_mask = tipo.str.contains("comun", na=False)
        if comune_mask.any():
            df = df.loc[comune_mask].copy()

    df = filter_additive_rows(df, cols)
    df["_comune_key"] = df[cols["comune"]].map(canonical_municipality)
    df["_comune_label"] = df[cols["comune"]].astype(str).str.strip()
    df["_missione"] = df[cols["missione"]].map(lambda x: norm_code(x, 2))
    df["_programma"] = df[cols["programma"]].map(lambda x: norm_code(x, 2))
    df["_titolo"] = df[cols["titolo"]].map(lambda x: norm_code(x, 2))
    df["_impegni"] = numeric(df[cols["impegni"]])
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
    for c in ["m0602_corrente_impegni", "m0602_capitale_impegni"]:
        out[c] = out[c].fillna(0.0)
    out = out.rename(columns={"_comune_key": "comune_key", "_comune_label": "comune_fonte"})
    out["anno"] = YEAR
    return out[[
        "comune_key", "comune_fonte", "anno", "m0602_corrente_impegni",
        "m0602_capitale_impegni", "spesa_corrente_totale_impegni"
    ]].sort_values("comune_key")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV/XLSX/ZIP ufficiale OpenBDAP/RGS")
    parser.add_argument("--output", default="data/interim/openbdap_2024_comuni.csv")
    parser.add_argument("--columns-report", default="data/interim/openbdap_2024_columns.txt")
    args = parser.parse_args()

    raw = read_table(args.input)
    try:
        prepared, cols = prepare(raw)
    except KeyError as exc:
        report = ensure_parent(args.columns_report)
        report.write_text("\n".join(map(str, raw.columns)), encoding="utf-8")
        raise SystemExit(f"Schema OpenBDAP non riconosciuto: {exc}\nColonne salvate in {report}")

    out = aggregate(prepared)
    path = ensure_parent(args.output)
    out.to_csv(path, index=False)
    print(f"Salvate {len(out):,} righe in {path}")
    print("Colonne riconosciute:")
    for key, value in cols.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
