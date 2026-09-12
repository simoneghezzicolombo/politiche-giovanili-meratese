"""Costruisce popolazione totale e 15-29 dai file ufficiali demo.istat.it."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import canonical_municipality, ensure_parent, find_column, norm_text, read_table  # noqa: E402

DEFAULT_URL = "https://demo.istat.it/data/posas/POSAS_2024_it_Comuni.zip"

ALIASES = {
    "comune": [
        "territorio", "comune", "denominazione comune", "nome comune",
        "comune descrizione",
    ],
    "eta": ["eta", "età", "eta anni", "classe eta", "eta1"],
    "sesso": ["sesso", "sex", "sexistat1"],
    "stato_civile": ["stato civile", "statocivile", "statciv2"],
    "valore": ["value", "valore", "totale", "popolazione", "residenti"],
    "anno": ["time", "seleziona periodo", "anno", "year"],
    "indicatore": ["tipo di indicatore demografico", "tipo_dato15", "tipo dato15"],
}


def parse_age(value: object) -> int | None:
    text = norm_text(value)
    if not text:
        return None
    if text in {"totale", "total", "tutte le eta"}:
        return 999
    if "100" in text and ("oltre" in text or "+" in str(value) or "piu" in text):
        return 100
    match = re.search(r"\b(\d{1,3})\b", text)
    return int(match.group(1)) if match else None


def numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").fillna(0)
    text = series.astype(str).str.strip()
    # I file demografici sono conteggi interi, ma tolleriamo separatori delle migliaia.
    text = text.str.replace(".", "", regex=False).str.replace(",", "", regex=False)
    text = text.str.replace(r"[^0-9\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce").fillna(0)


def keep_total_dimension(df: pd.DataFrame, column: str | None, label: str) -> pd.DataFrame:
    """Se la dimensione espone una modalità totale, usa solo quella.

    È fondamentale per non sommare, per esempio, sia il totale per stato civile
    sia celibi/nubili + coniugati + divorziati + vedovi.
    """
    if not column:
        return df
    values = df[column].map(norm_text)
    total_mask = values.isin({"totale", "tot", "t", "total", "tutti", "tutte"})
    if total_mask.any():
        return df.loc[total_mask].copy()
    print(f"Nota: nessuna modalità totale riconosciuta per {label}; mantengo tutte le righe.")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_URL, help="CSV/ZIP Istat; default: POSAS 2024 Comuni ufficiale")
    parser.add_argument("--year", type=int, default=2024, help="Anno della popolazione al 1° gennaio")
    parser.add_argument("--output", default="data/interim/istat_pop_2024.csv")
    args = parser.parse_args()

    df = read_table(args.input)
    comune = find_column(df.columns, ALIASES["comune"])
    eta = find_column(df.columns, ALIASES["eta"])
    sesso = find_column(df.columns, ALIASES["sesso"], required=False)
    stato_civile = find_column(df.columns, ALIASES["stato_civile"], required=False)
    valore = find_column(df.columns, ALIASES["valore"])
    anno = find_column(df.columns, ALIASES["anno"], required=False)
    indicatore = find_column(df.columns, ALIASES["indicatore"], required=False)

    if anno:
        years = pd.to_numeric(df[anno], errors="coerce")
        if (years == args.year).any():
            df = df.loc[years == args.year].copy()

    # Se il file contiene più indicatori, teniamo la popolazione al 1° gennaio.
    if indicatore:
        ind = df[indicatore].map(norm_text)
        jan = ind.str.contains("popolazione", na=False) & ind.str.contains("1 gennaio", na=False)
        if jan.any():
            df = df.loc[jan].copy()

    df = keep_total_dimension(df, sesso, "sesso")
    df = keep_total_dimension(df, stato_civile, "stato civile")

    df["_age"] = df[eta].map(parse_age)
    df = df[df["_age"].notna()].copy()
    df["_age"] = df["_age"].astype(int)
    df["_pop"] = numeric(df[valore])
    df["comune_key"] = df[comune].map(canonical_municipality)

    # Dopo i filtri di dimensione deve esserci una sola osservazione per comune-età.
    duplicates = df.duplicated(["comune_key", "_age"], keep=False)
    if duplicates.any():
        sample = (
            df.loc[duplicates, [comune, eta]]
            .drop_duplicates()
            .head(10)
            .to_dict("records")
        )
        raise SystemExit(
            "ISTAT: più osservazioni per comune/età dopo i filtri; "
            f"non sommo automaticamente per evitare doppi conteggi. Esempi: {sample}"
        )

    age = df[["comune_key", "_age", "_pop"]].copy()

    # Se è presente la riga Totale (codificata qui come 999), la usiamo;
    # altrimenti sommiamo le singole età, escludendo eventuali codici speciali.
    total_rows = age[age["_age"] == 999]
    if not total_rows.empty:
        total = total_rows[["comune_key", "_pop"]].rename(columns={"_pop": "pop_totale"})
    else:
        total = (
            age[age["_age"].between(0, 120)]
            .groupby("comune_key", as_index=False)["_pop"].sum()
            .rename(columns={"_pop": "pop_totale"})
        )

    youth = (
        age[age["_age"].between(15, 29)]
        .groupby("comune_key", as_index=False)["_pop"].sum()
        .rename(columns={"_pop": "pop_15_29"})
    )
    out = total.merge(youth, on="comune_key", how="left")
    out["pop_15_29"] = out["pop_15_29"].fillna(0).astype(int)
    out["pop_totale"] = out["pop_totale"].astype(int)
    out["pop_data_riferimento"] = f"{args.year}-01-01"

    # Controlli di plausibilità: il file nazionale dei Comuni deve contenere migliaia di enti.
    if len(out) < 7000:
        raise SystemExit(f"ISTAT: trovati solo {len(out)} territori comunali; file/schema da verificare.")
    if (out["pop_15_29"] > out["pop_totale"]).any():
        raise SystemExit("ISTAT: controllo fallito, popolazione 15-29 superiore alla popolazione totale.")

    path = ensure_parent(args.output)
    out.sort_values("comune_key").to_csv(path, index=False)
    print(f"Salvati {len(out):,} comuni in {path}")
    print(f"Colonne: comune={comune!r}, eta={eta!r}, sesso={sesso!r}, stato_civile={stato_civile!r}, valore={valore!r}, anno={anno!r}")


if __name__ == "__main__":
    main()
