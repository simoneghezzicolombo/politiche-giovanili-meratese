"""Rigenera le figure pubbliche della socialità dal CSV versionato."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def fmt_it(value: float) -> str:
    return f"{value:.1f}".replace(".", ",") + "%"


def render_main(df: pd.DataFrame, figures: Path) -> None:
    x = df["anno"].astype(int)
    y = df["sm_almeno_piu_volta_sett"].astype(float)
    key = {yr: float(df.loc[df["anno"] == yr, "sm_almeno_piu_volta_sett"].iloc[0]) for yr in [2013, 2020, 2024]}
    delta = key[2024] - key[2013]

    mpl.rcParams["svg.fonttype"] = "none"
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.plot(x, y, linewidth=4)
    ax.plot([2013, 2020, 2024], [key[2013], key[2020], key[2024]], linestyle="", marker="o", markersize=8)
    ax.set_xlim(2012.7, 2024.6)
    ax.set_ylim(56, 79.6)
    ax.set_xticks(x.tolist())
    ax.grid(True, axis="y", alpha=.20)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("In Lombardia la socialità frequente degli adolescenti è in calo", fontsize=22, y=.96)
    ax.set_title(
        "Quota di 14-17enni che incontra gli amici tutti i giorni o più di una volta a settimana, 2013-2024",
        fontsize=12.5, loc="left", pad=14,
    )
    ax.set_ylabel("Percentuale (%)", fontsize=13)
    ax.set_xlabel("")

    ax.annotate(fmt_it(key[2013]), xy=(2013, key[2013]), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=11.5)
    ax.annotate(fmt_it(key[2020]), xy=(2020, key[2020]), xytext=(0, -20), textcoords="offset points", ha="center", fontsize=11.5)
    ax.annotate(fmt_it(key[2024]), xy=(2024, key[2024]), xytext=(10, 0), textcoords="offset points", va="center", fontsize=11.5)
    ax.text(.985, .93, f"2013 → 2024: {delta:.1f}".replace(".", ",") + " punti", transform=ax.transAxes,
            ha="right", va="top", fontsize=12)

    fig.text(.01, .012,
             "Fonte: elaborazione su microdati Istat AVQ, Lombardia, 14-17 anni. Serie smussata con media mobile coerente con la procedura usata.",
             fontsize=9.5)
    fig.tight_layout(rect=(0, .05, 1, .92))
    figures.mkdir(parents=True, exist_ok=True)
    fig.savefig(figures / "socialita_frequente_lombardia_2013_2024.png", dpi=260, bbox_inches="tight")
    fig.savefig(figures / "socialita_frequente_lombardia_2013_2024.svg", bbox_inches="tight")
    plt.close(fig)


def render_network(df: pd.DataFrame, figures: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df["anno"], df["sm_ha_amici_su_cui_contare"], linewidth=3, marker="o", label="Ha amici su cui contare")
    ax.plot(df["anno"], df["sm_molto_soddisfatti_relazioni_amicali"], linewidth=3, marker="o",
            label="Molto soddisfatti delle relazioni con gli amici")
    ax.set_title("Adolescenti lombardi 14-17 anni\nQualità e supporto della rete amicale", fontsize=17, pad=16)
    ax.set_xlabel("Anno", fontsize=12)
    ax.set_ylabel("Percentuale (%)", fontsize=12)
    ax.set_xticks(df["anno"].tolist())
    ax.grid(True, alpha=.25)
    ax.legend(frameon=False)
    fig.text(.01, .01,
             "Fonte: elaborazione su microdati Istat AVQ, Lombardia, 14-17 anni. Serie smussate con media mobile coerente con la procedura usata.",
             fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    figures.mkdir(parents=True, exist_ok=True)
    fig.savefig(figures / "qualita_rete_amicale_lombardia_2013_2024.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=Path("analisi/socialita/data/indicatori_socialita_lombardia_14_17_2013_2024.csv"))
    parser.add_argument("--figures", type=Path, default=Path("analisi/socialita/figures"))
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    render_main(df, args.figures)
    render_network(df, args.figures)
    print(f"Figure rigenerate in {args.figures}")


if __name__ == "__main__":
    main()
