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
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams['svg.fonttype'] = 'none'

ROOT = Path(__file__).resolve().parents[1]
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

COLORS = {
    "Lombardia": "#08A045",
    "Bellano": "#79B977",
    "Caratese": "#E8A27A",
    "Lecchese": "#49A7D8",
    "Isola Bergamasca": "#9A8FC9",
    "Meratese": "#E7A7A7",
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
    order = [
        "Lombardia",
        "Bellano",
        "Caratese",
        "Lecchese",
        "Isola Bergamasca",
        "Meratese",
    ]
    p = panel[panel["year"] == 2023].set_index("territory").loc[order].reset_index()

    fig, ax = plt.subplots(figsize=(12.5, 7.4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y = np.arange(len(p))
    bars = ax.barh(
        y,
        p["composite_eur_per_0_17"],
        color=[COLORS[t] for t in p["territory"]],
        height=0.42,
    )
    ax.invert_yaxis()

    ax.set_title(
        "Quanto si investe per ragazze e ragazzi?",
        fontsize=21,
        fontweight="bold",
        family="serif",
        pad=18,
    )
    fig.text(
        0.5,
        0.895,
        "Spesa comunale per opportunità sociali, ricreative e di autonomia · € per residente 0–17 · 2023",
        ha="center",
        fontsize=11.5,
        family="serif",
    )

    ax.set_xlim(0, 30)
    ax.set_xticks(np.arange(0, 31, 5))
    ax.set_yticks(y)
    ax.set_yticklabels(p["territory"], fontsize=13.5, family="serif")
    ax.tick_params(axis="x", labelsize=11)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color="#D8D8D8", linewidth=1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for bar, value in zip(bars, p["composite_eur_per_0_17"]):
        x = value * 0.5 if value >= 11 else value - 0.45
        ha = "center" if value >= 11 else "right"
        ax.text(
            x,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f} €",
            va="center",
            ha=ha,
            fontsize=12.5,
            fontweight="bold",
            family="serif",
            color="black",
        )

    for tick in ax.get_yticklabels():
        if tick.get_text() == "Meratese":
            tick.set_fontweight("bold")

    fig.text(
        0.07,
        0.052,
        "Fonte: elaborazione su dati Istat",
        ha="left",
        fontsize=10.5,
        style="italic",
        family="serif",
        color="#5F5F5F",
    )
    fig.text(
        0.5,
        0.018,
        "Indicatore composito: attività ricreative, sociali e culturali; centri di aggregazione; "
        "centri estivi; sostegno e contributi all’inserimento lavorativo.",
        ha="center",
        fontsize=9.2,
        color="#777777",
    )

    plt.subplots_adjust(left=0.23, right=0.96, top=0.82, bottom=0.14)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUTS / "benchmark_opportunita_under18_2023.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUTS / "benchmark_opportunita_under18_2023.svg", bbox_inches="tight")
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
