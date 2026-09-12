#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "output" / "media_ultimi_3_anni.csv"
OUT = ROOT / "data" / "output" / "spesa_media_per_residente.png"


def main() -> None:
    df = pd.read_csv(SOURCE)
    df = df.dropna(subset=["media_euro_per_residente"]).copy()

    if df.empty:
        raise SystemExit(
            "Nessun dato disponibile. Compila i file in data/input e avvia prima 01_indicatori.py."
        )

    df = df.sort_values("media_euro_per_residente", ascending=True)

    height = max(6, len(df) * 0.32)
    fig, ax = plt.subplots(figsize=(9, height))
    ax.barh(df["comune"], df["media_euro_per_residente"])
    ax.set_xlabel("Euro per residente, media degli ultimi 3 anni disponibili")
    ax.set_ylabel("")
    ax.set_title('Spesa contabilizzata nel Programma 06.02 "Giovani"')
    ax.text(
        0,
        1.01,
        "L'indicatore non rappresenta necessariamente tutta la spesa comunale rivolta ai giovani.",
        transform=ax.transAxes,
        fontsize=9,
    )
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180)
    print(f"Creato: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
