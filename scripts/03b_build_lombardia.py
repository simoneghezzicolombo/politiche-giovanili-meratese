"""Costruisce il dataset 2024 di tutti i Comuni lombardi per il benchmark."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import ensure_parent  # noqa: E402

# Prefissi provinciali Istat dei Comuni lombardi.
LOMBARDIA_PROVINCE_CODES = {
    "012",  # Varese
    "013",  # Como
    "014",  # Sondrio
    "015",  # Milano
    "016",  # Bergamo
    "017",  # Brescia
    "018",  # Pavia
    "019",  # Cremona
    "020",  # Mantova
    "097",  # Lecco
    "098",  # Lodi
    "108",  # Monza e Brianza
}


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    return pd.to_numeric(num / den.replace({0: pd.NA}), errors="coerce")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bilanci", default="data/interim/openbdap_2024_comuni.csv")
    parser.add_argument("--popolazione", default="data/interim/istat_pop_2024.csv")
    parser.add_argument("--output", default="data/processed/lombardia_2024.csv")
    args = parser.parse_args()

    bilanci = pd.read_csv(args.bilanci)
    pop = pd.read_csv(args.popolazione, dtype={"codice_comune": "string"})

    if "codice_comune" not in pop.columns:
        raise SystemExit("Il file Istat deve contenere `codice_comune` per costruire il benchmark lombardo.")

    pop["codice_comune"] = pop["codice_comune"].astype("string").str.zfill(6)
    pop["provincia_istat"] = pop["codice_comune"].str[:3]
    pop = pop[pop["provincia_istat"].isin(LOMBARDIA_PROVINCE_CODES)].copy()

    if pop["comune_key"].duplicated().any():
        dup = pop.loc[pop["comune_key"].duplicated(keep=False), ["codice_comune", "comune_key"]]
        raise SystemExit(
            "Denominazioni comunali duplicate dentro la Lombardia, join nominale non sicuro: "
            + dup.head(20).to_dict("records").__repr__()
        )

    df = bilanci.merge(
        pop[["codice_comune", "comune_key", "pop_totale", "pop_15_29", "pop_data_riferimento"]],
        on="comune_key",
        how="left",
        validate="one_to_one",
    )

    df["eur_m0602_per_abitante"] = safe_div(df["m0602_corrente_impegni"], df["pop_totale"])
    df["eur_m0602_per_giovane_15_29"] = safe_div(df["m0602_corrente_impegni"], df["pop_15_29"])
    df["pct_spesa_corrente_m0602"] = safe_div(
        df["m0602_corrente_impegni"], df["spesa_corrente_totale_impegni"]
    ) * 100
    df["m0602_zero"] = df["m0602_corrente_impegni"].eq(0)
    df["dato_popolazione_mancante"] = df["pop_totale"].isna()

    matched = int(df["pop_totale"].notna().sum())
    if not 1450 <= len(df) <= 1550:
        raise SystemExit(f"Numero inatteso di enti comunali OpenBDAP per la Lombardia: {len(df)}")
    if matched < 1450:
        missing = df.loc[df["pop_totale"].isna(), "comune_fonte"].head(30).tolist()
        raise SystemExit(f"Troppi Comuni senza match Istat: {matched}/{len(df)}. Esempi: {missing}")

    keep = [
        "codice_comune", "comune_key", "comune_fonte", "anno",
        "pop_totale", "pop_15_29", "m0602_corrente_impegni", "m0602_capitale_impegni",
        "spesa_corrente_totale_impegni", "eur_m0602_per_abitante",
        "eur_m0602_per_giovane_15_29", "pct_spesa_corrente_m0602", "m0602_zero",
        "dato_popolazione_mancante",
    ]
    path = ensure_parent(args.output)
    df[keep].sort_values("codice_comune", na_position="last").to_csv(path, index=False)
    print(f"Dataset Lombardia: {path} ({len(df)} enti; {matched} con popolazione Istat)")
    print(f"Comuni M06-P02 corrente = 0: {int(df['m0602_zero'].sum())} ({df['m0602_zero'].mean()*100:.1f}%)")


if __name__ == "__main__":
    main()
