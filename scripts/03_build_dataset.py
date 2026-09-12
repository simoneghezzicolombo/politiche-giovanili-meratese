"""Unisce bilanci e demografia e calcola gli indicatori pubblici."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import canonical_municipality, ensure_parent  # noqa: E402


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    result = num / den.replace({0: pd.NA})
    return pd.to_numeric(result, errors="coerce")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comuni", default="config/comuni_merate.csv")
    parser.add_argument("--bilanci", default="data/interim/openbdap_2024_comuni.csv")
    parser.add_argument("--popolazione", default="data/interim/istat_pop_2024.csv")
    parser.add_argument("--output", default="data/processed/meratese_2024.csv")
    args = parser.parse_args()

    comuni = pd.read_csv(args.comuni)
    bilanci = pd.read_csv(args.bilanci)
    pop = pd.read_csv(args.popolazione, dtype={"codice_comune": "string"})

    # Tutti i Comuni dell'Ambito sono in provincia di Lecco. Nei codici Istat
    # comunali la provincia di Lecco ha prefisso 097: filtrarlo impedisce che
    # eventuali omonimie nazionali producano join duplicati per denominazione.
    if "codice_comune" in pop.columns:
        pop["codice_comune"] = pop["codice_comune"].astype("string").str.zfill(6)
        pop = pop[pop["codice_comune"].str.startswith("097", na=False)].copy()

    comuni["comune_key"] = comuni["comune"].map(canonical_municipality)
    if pop["comune_key"].duplicated().any():
        dup = pop.loc[pop["comune_key"].duplicated(keep=False), "comune_key"].unique().tolist()
        raise SystemExit(f"Chiavi demografiche duplicate in provincia di Lecco: {dup[:20]}")

    df = comuni.merge(bilanci, on="comune_key", how="left").merge(pop, on="comune_key", how="left")

    df["eur_m0602_per_abitante"] = safe_div(df["m0602_corrente_impegni"], df["pop_totale"])
    df["eur_m0602_per_giovane_15_29"] = safe_div(df["m0602_corrente_impegni"], df["pop_15_29"])
    df["pct_spesa_corrente_m0602"] = safe_div(
        df["m0602_corrente_impegni"], df["spesa_corrente_totale_impegni"]
    ) * 100

    df["dato_bilancio_mancante"] = df["spesa_corrente_totale_impegni"].isna()
    df["dato_popolazione_mancante"] = df["pop_totale"].isna()
    df["m0602_zero"] = df["m0602_corrente_impegni"].eq(0) & df["spesa_corrente_totale_impegni"].notna()

    keep = [
        "comune", "provincia", "ambito", "anno", "pop_totale", "pop_15_29",
        "m0602_corrente_impegni", "m0602_capitale_impegni", "spesa_corrente_totale_impegni",
        "eur_m0602_per_abitante", "eur_m0602_per_giovane_15_29", "pct_spesa_corrente_m0602",
        "m0602_zero", "dato_bilancio_mancante", "dato_popolazione_mancante",
    ]
    path = ensure_parent(args.output)
    df[keep].sort_values("eur_m0602_per_giovane_15_29", ascending=False, na_position="last").to_csv(path, index=False)

    missing = df[df["dato_bilancio_mancante"] | df["dato_popolazione_mancante"]]["comune"].tolist()
    print(f"Dataset finale: {path} ({len(df)} Comuni)")
    if missing:
        print("ATTENZIONE, dati mancanti per: " + ", ".join(missing))


if __name__ == "__main__":
    main()
