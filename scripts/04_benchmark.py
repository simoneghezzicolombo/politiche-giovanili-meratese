"""Calcola benchmark lombardi per classe demografica su un dataset comunale già costruito."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import ensure_parent  # noqa: E402

BINS = [0, 4999, 9999, 19999, 49999, 99999, float("inf")]
LABELS = ["<5mila", "5-9.999", "10-19.999", "20-49.999", "50-99.999", "100mila+"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Dataset di tutti i Comuni lombardi con gli indicatori finali")
    parser.add_argument("--output", default="outputs/tables/benchmark_lombardia_2024.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df = df[df["pop_totale"].notna()].copy()
    df["classe_demografica"] = pd.cut(df["pop_totale"], bins=BINS, labels=LABELS, include_lowest=True)

    metric = "eur_m0602_per_giovane_15_29"
    # Il benchmark della metrica usa solo Comuni per cui il bilancio è
    # effettivamente disponibile. Gli zeri reali restano inclusi come zero.
    metric_df = df[df[metric].notna()].copy()
    grouped = metric_df.groupby("classe_demografica", observed=True)[metric]
    out = grouped.agg(
        n="count", media="mean", mediana="median",
        p25=lambda s: s.quantile(.25), p75=lambda s: s.quantile(.75),
        minimo="min", massimo="max",
    ).reset_index()

    budget_df = df[df["m0602_corrente_impegni"].notna()].copy()
    budget_df["zero"] = budget_df["m0602_corrente_impegni"].eq(0)
    zeros = budget_df.groupby("classe_demografica", observed=True)["zero"].mean().mul(100).reset_index(
        name="pct_comuni_zero"
    )
    coverage = budget_df.groupby("classe_demografica", observed=True).size().reset_index(name="n_bilanci_disponibili")
    out = out.merge(zeros, on="classe_demografica", how="left").merge(
        coverage, on="classe_demografica", how="left"
    )

    path = ensure_parent(args.output)
    out.to_csv(path, index=False)
    print(f"Benchmark salvato in {path}")


if __name__ == "__main__":
    main()
