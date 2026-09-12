"""Ricostruisce gli indicatori di socialità degli adolescenti lombardi (2013-2024).

La pipeline replica la selezione del do-file originale per il 2013-2022 e la
estende ai microdati AVQ 2023 e 2024.

Campione:
- Lombardia (REGMf = 030)
- ETAMi = 005 o 006, cioè 14-17 anni
- esclusione dei missing su AMICI, AMICI2, VOLON, ATGRA e RELAM, nello stesso
  ordine del do-file originale

La serie pubblica principale aggrega AMICI=1 (tutti i giorni) e AMICI=2 (più
volte a settimana), poi applica la stessa media mobile usata nel lavoro
originale: 3 lag + valore corrente + 1 lead, normalizzata sui valori disponibili.

Nota: il do-file originale chiamava alcune elaborazioni "ponderate", ma non
applicava COEFIN. Questa pipeline conserva volutamente quella logica per la
comparabilità con la serie storica già prodotta.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import zipfile

import matplotlib.pyplot as plt
import pandas as pd


def _numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors="coerce")
    return df


def load_original_series(socialita_zip: Path) -> pd.DataFrame:
    with zipfile.ZipFile(socialita_zip) as zf:
        raw = zf.read("SOCIALITA/socialitaFINALE.dta")
    df = pd.read_stata(io.BytesIO(raw), convert_categoricals=False)
    cols = ["anno", "amici", "amici2", "volon", "atgra", "relam"]
    df = df[cols].copy()
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_avq_year(path: Path, year: int) -> pd.DataFrame:
    member = f"MICRODATI/AVQ_Microdati_{year}.txt"
    usecols = ["ANNO", "ETAMi", "REGMf", "AMICI", "AMICI2", "VOLON", "ATGRA", "RELAM"]
    with zipfile.ZipFile(path) as zf, zf.open(member) as fh:
        df = pd.read_csv(fh, sep="\t", usecols=usecols, dtype=str)
    df = _numeric(df, usecols)
    df = df[(df["REGMf"] == 30) & (df["ETAMi"].isin([5, 6]))].copy()
    return df.rename(columns={
        "ANNO": "anno", "AMICI": "amici", "AMICI2": "amici2",
        "VOLON": "volon", "ATGRA": "atgra", "RELAM": "relam",
    })[["anno", "amici", "amici2", "volon", "atgra", "relam"]]


def smooth_original(series: pd.Series) -> pd.Series:
    """Equivalente concettuale di tssmooth ma, window(3 1 1)."""
    out: dict[int, float] = {}
    for year in series.index:
        years = [year - 3, year - 2, year - 1, year, year + 1]
        values = [float(series.loc[y]) for y in years if y in series.index]
        out[int(year)] = sum(values) / len(values)
    return pd.Series(out)


def build_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Replica esattamente la sequenza di drop del do-file originale.
    for col in ["amici", "amici2", "volon", "atgra", "relam"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=[col])

    df["anno"] = pd.to_numeric(df["anno"], errors="coerce").astype(int)
    for col in ["amici", "amici2", "volon", "atgra", "relam"]:
        df[col] = df[col].astype(int)

    years = sorted(df["anno"].unique())
    out = pd.DataFrame(index=years)
    out.index.name = "anno"
    out["pct_almeno_piu_volta_sett"] = (
        df.assign(ind=df["amici"].isin([1, 2]).astype(int))
        .groupby("anno")["ind"].mean().mul(100)
    )
    out["pct_ha_amici_su_cui_contare"] = (
        df.assign(ind=df["amici2"].eq(2).astype(int))
        .groupby("anno")["ind"].mean().mul(100)
    )
    out["pct_molto_soddisfatti_relazioni_amicali"] = (
        df.assign(ind=df["relam"].eq(1).astype(int))
        .groupby("anno")["ind"].mean().mul(100)
    )
    out["n_finale"] = df.groupby("anno").size()
    out["sm_almeno_piu_volta_sett"] = smooth_original(out["pct_almeno_piu_volta_sett"])
    out["sm_ha_amici_su_cui_contare"] = smooth_original(out["pct_ha_amici_su_cui_contare"])
    out["sm_molto_soddisfatti_relazioni_amicali"] = smooth_original(
        out["pct_molto_soddisfatti_relazioni_amicali"]
    )
    return out.reset_index()


def fmt_it(value: float) -> str:
    return f"{value:.1f}".replace(".", ",") + "%"


def plot_socialita(ind: pd.DataFrame, output_png: Path, output_svg: Path) -> None:
    x = ind["anno"].astype(int)
    y = ind["sm_almeno_piu_volta_sett"].astype(float)
    key = {yr: float(ind.loc[ind["anno"] == yr, "sm_almeno_piu_volta_sett"].iloc[0]) for yr in [2013, 2020, 2024]}
    delta = key[2024] - key[2013]

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
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=260, bbox_inches="tight")
    fig.savefig(output_svg, bbox_inches="tight")
    plt.close(fig)


def plot_rete(ind: pd.DataFrame, output_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(ind["anno"], ind["sm_ha_amici_su_cui_contare"], linewidth=3, marker="o", label="Ha amici su cui contare")
    ax.plot(ind["anno"], ind["sm_molto_soddisfatti_relazioni_amicali"], linewidth=3, marker="o",
            label="Molto soddisfatti delle relazioni con gli amici")
    ax.set_title("Adolescenti lombardi 14-17 anni\nQualità e supporto della rete amicale", fontsize=17, pad=16)
    ax.set_xlabel("Anno", fontsize=12)
    ax.set_ylabel("Percentuale (%)", fontsize=12)
    ax.set_xticks(ind["anno"].tolist())
    ax.grid(True, alpha=.25)
    ax.legend(frameon=False)
    fig.text(.01, .01,
             "Fonte: elaborazione su microdati Istat AVQ, Lombardia, 14-17 anni. Serie smussate con media mobile coerente con la procedura usata.",
             fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socialita-zip", type=Path, required=True, help="Archivio SOCIALITA.zip con socialitaFINALE.dta")
    parser.add_argument("--avq-2023", type=Path, required=True, help="Archivio Istat AVQ_2023_IT.zip")
    parser.add_argument("--avq-2024", type=Path, required=True, help="Archivio Istat AVQ_2024_IT.zip")
    parser.add_argument("--output-dir", type=Path, default=Path("analisi/socialita"))
    args = parser.parse_args()

    old = load_original_series(args.socialita_zip)
    new = pd.concat([load_avq_year(args.avq_2023, 2023), load_avq_year(args.avq_2024, 2024)], ignore_index=True)
    indicators = build_indicators(pd.concat([old, new], ignore_index=True))

    data_dir = args.output_dir / "data"
    figures_dir = args.output_dir / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "indicatori_socialita_lombardia_14_17_2013_2024.csv"
    indicators.round(2).to_csv(csv_path, index=False)
    plot_socialita(
        indicators,
        figures_dir / "socialita_frequente_lombardia_2013_2024.png",
        figures_dir / "socialita_frequente_lombardia_2013_2024.svg",
    )
    plot_rete(indicators, figures_dir / "qualita_rete_amicale_lombardia_2013_2024.png")
    print(f"Dati: {csv_path}")
    print(f"Figure: {figures_dir}")


if __name__ == "__main__":
    main()
