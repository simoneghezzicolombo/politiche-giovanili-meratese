#!/usr/bin/env python3
"""
Costruisce il benchmark Istat ATS sulle opportunità sociali, ricreative e di
autonomia per residenti 0-17 anni e genera il grafico 2023.

Fonte IstatData:
47_940_DF_DCIS_SPESESERSOC1_5
"Utenti e spesa - Ambiti territoriali sociali (ATS)"

Indicatore:
somma della "Spesa dei comuni (euro)" per sei voci dell'area Famiglia e minori,
divisa per la popolazione target 0-17 implicita nell'indicatore Istat
"Spesa dei comuni sulla popolazione di riferimento".

Non equivale alla spesa complessiva per politiche giovanili.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from visuals.chart_style import (
    ACCENT,
    BENCHMARK,
    FIGSIZE,
    INK,
    OTHER,
    add_footer,
    add_title_block,
    apply_project_style,
    save_public_figure,
    style_axis,
)

RAW = ROOT / "data" / "raw" / "istat_ats" / "istat_ats_selected_2021_2023.csv"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

TERRITORIES = {
    "ITC4": "Lombardia",
    "T03040": "Bellano",
    "T03054": "Caratese",
    "T03041": "Lecchese",
    "T03010": "Isola Bergamasca",
    "T03042": "Meratese",
}

SERVICES = {
    "RICSOC": "Attività ricreative, sociali, culturali",
    "AGGRC": "Centri di aggregazione / sociali",
    "SUMDAYC": "Centri diurni estivi",
    "WSRESID": "Centri estivi o invernali (con pernottamento)",
    "EMPLOY": "Sostegno all'inserimento lavorativo",
    "CONTEMP": "Contributi per l'inserimento lavorativo",
}


def build_panel():
    df = pd.read_csv(RAW)
    df["Osservazione_num"] = pd.to_numeric(df["Osservazione"], errors="coerce")

    records = []
    components = []

    for year in sorted(df["TIME_PERIOD"].unique()):
        for ref_area, short_name in TERRITORIES.items():
            fam = df[
                (df["REF_AREA"] == ref_area)
                & (df["CATEG_OF_BENEFICIARIES"] == "FAM")
                & (df["TIME_PERIOD"] == year)
            ].copy()

            selected = fam[
                (fam["DATA_TYPE"] == "EXPMUN")
                & (fam["CATEGORY_OF_SERVICE"].isin(SERVICES))
            ]
            selected_expenditure = selected["Osservazione_num"].sum()

            total_family = fam[
                (fam["DATA_TYPE"] == "EXPMUN")
                & (fam["CATEGORY_OF_SERVICE"] == "ALL")
            ]["Osservazione_num"].iloc[0]

            published_ratio = fam[
                (fam["DATA_TYPE"] == "EXPTPOP")
                & (fam["CATEGORY_OF_SERVICE"] == "ALL")
            ]["Osservazione_num"].iloc[0]

            # EXPTPOP = spesa dei Comuni / popolazione target dell'area.
            # Istat pubblica il rapporto arrotondato all'euro, quindi la
            # popolazione ricostruita è leggermente approssimata.
            implied_population = total_family / published_ratio
            composite = selected_expenditure / implied_population

            records.append(
                {
                    "year": int(year),
                    "ref_area": ref_area,
                    "territory": short_name,
                    "selected_expenditure_eur": selected_expenditure,
                    "family_minors_total_expenditure_eur": total_family,
                    "istat_family_minors_eur_per_target": published_ratio,
                    "implied_population_0_17": implied_population,
                    "composite_eur_per_0_17": composite,
                }
            )

            for code, label in SERVICES.items():
                row = fam[
                    (fam["DATA_TYPE"] == "EXPMUN")
                    & (fam["CATEGORY_OF_SERVICE"] == code)
                ]
                value = row["Osservazione_num"].iloc[0] if len(row) else 0
                components.append(
                    {
                        "year": int(year),
                        "ref_area": ref_area,
                        "territory": short_name,
                        "service_code": code,
                        "service_name": label,
                        "municipal_expenditure_eur": value,
                    }
                )

    return pd.DataFrame(records), pd.DataFrame(components)


def make_chart(panel: pd.DataFrame):
    apply_project_style()
    p = (
        panel[panel["year"] == 2023]
        .sort_values("composite_eur_per_0_17", ascending=False)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=.23, right=.96, top=.78, bottom=.18)
    style_axis(ax, "x")

    colors = [
        ACCENT if territory == "Meratese"
        else BENCHMARK if territory == "Lombardia"
        else OTHER
        for territory in p["territory"]
    ]
    y = np.arange(len(p))
    bars = ax.barh(
        y,
        p["composite_eur_per_0_17"],
        color=colors,
        height=.52,
    )
    ax.invert_yaxis()
    ax.set_xlim(0, 28)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.set_xticklabels(["0 €", "5 €", "10 €", "15 €", "20 €", "25 €"])
    ax.set_yticks(y)
    ax.set_yticklabels(p["territory"], fontsize=11.5)

    for tick in ax.get_yticklabels():
        if tick.get_text() == "Meratese":
            tick.set_fontweight("bold")
            tick.set_color(ACCENT)
        elif tick.get_text() == "Lombardia":
            tick.set_fontweight("bold")
            tick.set_color(BENCHMARK)

    for bar, territory, value in zip(
        bars, p["territory"], p["composite_eur_per_0_17"]
    ):
        color = (
            ACCENT if territory == "Meratese"
            else BENCHMARK if territory == "Lombardia"
            else INK
        )
        ax.text(
            value + .35,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f} €".replace(".", ","),
            va="center",
            ha="left",
            fontsize=11.2,
            fontweight="bold" if territory in {"Meratese", "Lombardia"} else "normal",
            color=color,
        )

    add_title_block(
        fig,
        "Spesa dei Comuni per ragazze e ragazzi",
        "Opportunità sociali, ricreative e di autonomia · euro per residente 0–17 · 2023",
    )
    add_footer(
        fig,
        "Fonte: elaborazione su dati Istat, Interventi e servizi sociali dei Comuni singoli o associati.",
        "Indicatore composito: attività ricreative/sociali/culturali, centri di aggregazione, centri estivi e inserimento lavorativo.",
    )

    save_public_figure(fig, OUTPUTS / "benchmark_opportunita_under18_2023")
    plt.close(fig)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    panel, components = build_panel()

    panel.to_csv(
        PROCESSED / "istat_under18_opportunities_2021_2023.csv",
        index=False,
    )
    components.to_csv(
        PROCESSED / "istat_under18_opportunities_components_2021_2023.csv",
        index=False,
    )
    make_chart(panel)

    print(
        panel[panel["year"] == 2023][
            ["territory", "composite_eur_per_0_17"]
        ].sort_values("composite_eur_per_0_17", ascending=False).to_string(index=False)
    )


if __name__ == "__main__":
    main()
