"""Crea il grafico principale destinato alla comunicazione pubblica."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from _common import ensure_parent  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/meratese_2024.csv")
    parser.add_argument("--output", default="outputs/figures/euro_per_giovane_2024.png")
    args = parser.parse_args()

    df = pd.read_csv(args.input).dropna(subset=["eur_m0602_per_giovane_15_29"]).copy()
    df = df.sort_values("eur_m0602_per_giovane_15_29")

    fig_height = max(6, len(df) * .32)
    fig, ax = plt.subplots(figsize=(9, fig_height))
    ax.barh(df["comune"], df["eur_m0602_per_giovane_15_29"])
    ax.set_xlabel("Euro per residente 15-29 anni")
    ax.set_ylabel("")
    ax.set_title("Spesa corrente contabilizzata nel Programma 06.02 ‘Giovani’")
    ax.grid(axis="x", alpha=.2)

    for y, (_, row) in enumerate(df.iterrows()):
        value = row["eur_m0602_per_giovane_15_29"]
        ax.text(value, y, f"  {value:.1f} €", va="center", fontsize=8)

    fig.text(
        .01, .005,
        "Rendiconto 2024, impegni di competenza. M06-P02 non coincide necessariamente con tutta la spesa rivolta ai giovani.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, .025, 1, 1))
    path = ensure_parent(args.output)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    print(f"Grafico salvato in {path}")


if __name__ == "__main__":
    main()
