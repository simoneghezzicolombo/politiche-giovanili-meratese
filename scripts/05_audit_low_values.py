"""Genera la coda di controllo per valori M06-P02 nulli o molto bassi."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import ensure_parent  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/meratese_2024.csv")
    parser.add_argument("--output", default="metadata/audit_queue_2024.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    metric = "eur_m0602_per_giovane_15_29"
    nonmissing = df[metric].dropna()
    threshold = nonmissing.quantile(.25) if len(nonmissing) else 0
    valid = df["spesa_corrente_totale_impegni"].notna() & df[metric].notna()
    flagged = df[valid & (df["m0602_corrente_impegni"].eq(0) | (df[metric] <= threshold))].copy()

    flagged["motivo_audit"] = flagged.apply(
        lambda r: "M06-P02 = 0" if r["m0602_corrente_impegni"] == 0
        else "quartile inferiore €/giovane",
        axis=1,
    )
    for col in [
        "alternative_youth_policy_found", "mission_or_program", "project_or_service",
        "amount_if_known", "source_url", "confidence", "notes"
    ]:
        flagged[col] = ""

    cols = [
        "comune", "anno", "motivo_audit", "m0602_corrente_impegni", metric,
        "alternative_youth_policy_found", "mission_or_program", "project_or_service",
        "amount_if_known", "source_url", "confidence", "notes"
    ]
    path = ensure_parent(args.output)
    flagged[cols].to_csv(path, index=False)
    print(f"Coda audit: {len(flagged)} Comuni in {path}")


if __name__ == "__main__":
    main()
