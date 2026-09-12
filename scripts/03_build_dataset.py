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
    pop = pd.read_csv(args.popolazione)

    comuni["comune_key"] = comuni["comune"].map(canonical_municipality)

    # Le fonti demografiche possono contenere anche etichette e codici del Comune.
    # Nel merge teniamo solo la chiave canonica e i denominatori necessari, così
    # non creiamo colonne comune_x/comune_y o codice_istat_x/codice_istat_y.
    pop_keep = [c for c in ["comune_key", "pop_totale", "pop_15_29", "pop_data_riferimento"] if c in pop.columns]
    required_pop = {"comune_key", "pop_totale", "pop_15_29"}
    missing_pop = required_pop - set(pop_keep)
    if missing_pop:
        raise SystemExit("Colonne demografiche mancanti: " + ", ".join(sorted(missing_pop)))
    pop = pop[pop_keep].copy()

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
