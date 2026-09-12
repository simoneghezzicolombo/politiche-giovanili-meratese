"""Costruisce il dataset 2024 dei Comuni lombardi per il benchmark.

L'universo dei Comuni correnti è definito dal POSAS Istat al 1° gennaio 2024.
I dati contabili OpenBDAP vengono poi agganciati per denominazione normalizzata.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import ensure_parent  # noqa: E402

LOMBARDIA_PROVINCE_CODES = {
    "012", "013", "014", "015", "016", "017", "018", "019", "020",
    "097", "098", "108",
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
    lombardia = pop[pop["provincia_istat"].isin(LOMBARDIA_PROVINCE_CODES)].copy()

    if not 1450 <= len(lombardia) <= 1550:
        raise SystemExit(f"Numero inatteso di Comuni Istat in Lombardia: {len(lombardia)}")
    if lombardia["comune_key"].duplicated().any():
        dup = lombardia.loc[
            lombardia["comune_key"].duplicated(keep=False), ["codice_comune", "comune_key"]
        ]
        raise SystemExit(
            "Denominazioni comunali duplicate dentro la Lombardia, join nominale non sicuro: "
            + repr(dup.head(20).to_dict("records"))
        )

    # Istat definisce l'universo. In questo modo eventuali enti storici o record
    # amministrativi extra presenti nel file OpenBDAP non entrano nel benchmark.
    df = lombardia[[
        "codice_comune", "comune_key", "pop_totale", "pop_15_29", "pop_data_riferimento"
    ]].merge(bilanci, on="comune_key", how="left", validate="one_to_one")

    df["anno"] = 2024
    df["eur_m0602_per_abitante"] = safe_div(df["m0602_corrente_impegni"], df["pop_totale"])
    df["eur_m0602_per_giovane_15_29"] = safe_div(df["m0602_corrente_impegni"], df["pop_15_29"])
    df["pct_spesa_corrente_m0602"] = safe_div(
        df["m0602_corrente_impegni"], df["spesa_corrente_totale_impegni"]
    ) * 100
    df["dato_bilancio_mancante"] = df["spesa_corrente_totale_impegni"].isna()
    df["m0602_zero"] = (
        df["m0602_corrente_impegni"].eq(0)
        & df["spesa_corrente_totale_impegni"].notna()
    )

    matched = int((~df["dato_bilancio_mancante"]).sum())
    if matched < 1400:
        missing = df.loc[df["dato_bilancio_mancante"], "comune_key"].head(30).tolist()
        raise SystemExit(
            f"Troppi Comuni Istat senza bilancio OpenBDAP: {matched}/{len(df)}. Esempi: {missing}"
        )

    keep = [
        "codice_comune", "comune_key", "comune_fonte", "anno",
        "pop_totale", "pop_15_29", "m0602_corrente_impegni", "m0602_capitale_impegni",
        "spesa_corrente_totale_impegni", "eur_m0602_per_abitante",
        "eur_m0602_per_giovane_15_29", "pct_spesa_corrente_m0602", "m0602_zero",
        "dato_bilancio_mancante",
    ]
    path = ensure_parent(args.output)
    df[keep].sort_values("codice_comune").to_csv(path, index=False)

    valid = df[~df["dato_bilancio_mancante"]]
    zero_n = int(valid["m0602_zero"].sum())
    zero_pct = zero_n / len(valid) * 100 if len(valid) else float("nan")
    print(f"Dataset Lombardia: {path} ({len(df)} Comuni Istat; {matched} con bilancio OpenBDAP)")
    print(f"Comuni con bilancio e M06-P02 corrente = 0: {zero_n}/{len(valid)} ({zero_pct:.1f}%)")


if __name__ == "__main__":
    main()
