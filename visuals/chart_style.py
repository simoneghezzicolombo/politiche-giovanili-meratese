from __future__ import annotations

from pathlib import Path
import matplotlib as mpl

# Identità visiva originale del progetto.
# I principi sono editoriali (chiarezza, gerarchia, etichette dirette),
# ma palette, spaziature e componenti sono specifici di questo repository.
INK = "#17212B"
MUTED = "#66707A"
GRID = "#E2E7EB"
BACKGROUND = "#FFFFFF"
ACCENT = "#2F6BFF"
ACCENT_DARK = "#174EA6"
BENCHMARK = "#287A6B"
OTHER = "#D8DEE4"
OTHER_DARK = "#AAB4BE"

FIGSIZE = (12.6, 7.1)


def apply_project_style() -> None:
    mpl.rcParams.update({
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": BACKGROUND,
        "savefig.facecolor": BACKGROUND,
        "font.family": "DejaVu Sans",
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "axes.titleweight": "bold",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })


def add_title_block(fig, title: str, subtitle: str, kicker: str | None = None) -> None:
    x = 0.075
    if kicker:
        fig.text(
            x, 0.952, kicker.upper(),
            ha="left", va="top", fontsize=10.5,
            fontweight="bold", color=ACCENT,
        )
    fig.text(
        x, 0.915, title,
        ha="left", va="top", fontsize=22,
        fontweight="bold", color=INK,
    )
    fig.text(
        x, 0.858, subtitle,
        ha="left", va="top", fontsize=11.5,
        color=MUTED,
    )


def add_footer(fig, source: str, note: str | None = None) -> None:
    x = 0.075
    if note:
        fig.text(
            x, 0.052, note,
            ha="left", va="bottom", fontsize=8.9,
            color=MUTED, wrap=True,
        )
    fig.text(
        x, 0.022, source,
        ha="left", va="bottom", fontsize=9.2,
        color=MUTED,
    )


def style_axis(ax, grid_axis: str = "y") -> None:
    ax.tick_params(length=0, labelsize=10.5)
    ax.set_axisbelow(True)
    if grid_axis == "y":
        ax.yaxis.grid(True, color=GRID, linewidth=0.9)
        ax.xaxis.grid(False)
    elif grid_axis == "x":
        ax.xaxis.grid(True, color=GRID, linewidth=0.9)
        ax.yaxis.grid(False)
    else:
        ax.grid(False)


def save_public_figure(fig, base_path: Path, dpi: int = 300) -> None:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(base_path.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(base_path.with_suffix(".svg"), bbox_inches="tight")
