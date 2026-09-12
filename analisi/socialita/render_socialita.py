"""Rigenera le figure pubbliche della socialità dal CSV versionato."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

from visuals.chart_style import (
    ACCENT,
    ACCENT_DARK,
    FIGSIZE,
    INK,
    OTHER_DARK,
    add_footer,
    add_title_block,
    apply_project_style,
    save_public_figure,
    style_axis,
)


def fmt_it(value: float) -> str:
    return f"{value:.1f}".replace(".", ",") + "%"


def render_main(df: pd.DataFrame, figures: Path) -> None:
    apply_project_style()
    x = df["anno"].astype(int)
    y = df["sm_almeno_piu_volta_sett"].astype(float)
    start = float(df.loc[df["anno"] == 2013, "sm_almeno_piu_volta_sett"].iloc[0])
    end = float(df.loc[df["anno"] == 2024, "sm_almeno_piu_volta_sett"].iloc[0])
    delta = end - start

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=.075, right=.96, top=.78, bottom=.16)
    style_axis(ax, "y")

    ax.plot(x, y, linewidth=4.2, color=ACCENT, solid_capstyle="round")
    ax.scatter([2013, 2024], [start, end], s=68, color=ACCENT_DARK, zorder=4)
    ax.set_xlim(2012.7, 2024.7)
    ax.set_ylim(54, 82)
    ax.set_xticks([2013, 2015, 2017, 2019, 2021, 2023, 2024])
    ax.set_yticks([55, 60, 65, 70, 75, 80])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value)}%"))

    add_title_block(
        fig,
        "Gli adolescenti lombardi si vedono meno spesso",
        "14–17enni che incontrano gli amici ogni giorno o più volte a settimana · 2013–2024",
        "Socialità",
    )

    ax.annotate(
        fmt_it(start), xy=(2013, start), xytext=(0, 13),
        textcoords="offset points", ha="center", fontsize=11.5,
        fontweight="bold", color=INK,
    )
    ax.annotate(
        fmt_it(end), xy=(2024, end), xytext=(9, 0),
        textcoords="offset points", va="center", fontsize=11.5,
        fontweight="bold", color=INK,
    )
    ax.text(
        2024.25, end + 4.0,
        f"{delta:.1f}".replace(".", ",") + " punti dal 2013",
        ha="right", va="center", fontsize=11.2,
        fontweight="bold", color=ACCENT_DARK,
    )

    add_footer(
        fig,
        "Fonte: elaborazione su microdati Istat, Aspetti della vita quotidiana (AVQ).",
        "Lombardia, 14–17 anni. Serie smussata con media mobile coerente con la procedura originaria.",
    )
    save_public_figure(fig, figures / "socialita_frequente_lombardia_2013_2024")
    plt.close(fig)


def render_network(df: pd.DataFrame, figures: Path) -> None:
    apply_project_style()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=.075, right=.96, top=.78, bottom=.16)
    style_axis(ax, "y")

    ax.plot(
        df["anno"], df["sm_ha_amici_su_cui_contare"],
        linewidth=3.2, color=ACCENT,
        label="Ha amici su cui contare",
    )
    ax.plot(
        df["anno"], df["sm_molto_soddisfatti_relazioni_amicali"],
        linewidth=3.2, color=OTHER_DARK,
        label="Molto soddisfatti delle relazioni amicali",
    )
    ax.set_xticks([2013, 2015, 2017, 2019, 2021, 2023, 2024])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value)}%"))

    add_title_block(
        fig,
        "La rete amicale resta importante, ma non sempre soddisfa",
        "Indicatori sulla qualità delle relazioni amicali dei 14–17enni lombardi · 2013–2024",
        "Relazioni",
    )
    ax.legend(frameon=False, loc="lower left", fontsize=10.5)
    add_footer(
        fig,
        "Fonte: elaborazione su microdati Istat, Aspetti della vita quotidiana (AVQ).",
        "Lombardia, 14–17 anni. Serie smussate con media mobile coerente con la procedura originaria.",
    )
    save_public_figure(fig, figures / "qualita_rete_amicale_lombardia_2013_2024")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "analisi/socialita/data/indicatori_socialita_lombardia_14_17_2013_2024.csv",
    )
    parser.add_argument(
        "--figures", type=Path,
        default=ROOT / "analisi/socialita/figures",
    )
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    render_main(df, args.figures)
    render_network(df, args.figures)
    print(f"Figure rigenerate in {args.figures}")


if __name__ == "__main__":
    main()
