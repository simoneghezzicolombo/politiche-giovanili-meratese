#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
SPESA = ROOT / "data" / "input" / "spesa_programma_giovani.csv"
POP = ROOT / "data" / "input" / "popolazione.csv"
OUT = ROOT / "data" / "output" / "indicatori.csv"
OUT_MEDIA = ROOT / "data" / "output" / "media_ultimi_3_anni.csv"


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip().replace(",", ".")
    if not value:
        return None
    return float(value)


def read_population() -> dict[tuple[str, int], dict[str, str]]:
    with POP.open(encoding="utf-8-sig", newline="") as f:
        rows = csv.DictReader(f)
        return {(r["comune"].strip(), int(r["anno"])): r for r in rows}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pop = read_population()

    result = []
    with SPESA.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            comune = r["comune"].strip()
            anno = int(r["anno"])
            impegni = to_float(r["impegni_competenza_euro"])
            p = pop.get((comune, anno), {})
            pop_tot = to_float(p.get("popolazione_totale"))
            pop_gio = to_float(p.get("popolazione_giovane"))

            result.append(
                {
                    "comune": comune,
                    "anno": anno,
                    "impegni_competenza_euro": impegni,
                    "popolazione_totale": pop_tot,
                    "popolazione_giovane": pop_gio,
                    "fascia_giovane": p.get("fascia_giovane", ""),
                    "euro_per_residente": (
                        round(impegni / pop_tot, 2)
                        if impegni is not None and pop_tot
                        else ""
                    ),
                    "euro_per_giovane": (
                        round(impegni / pop_gio, 2)
                        if impegni is not None and pop_gio
                        else ""
                    ),
                    "verificato": r.get("verificato", ""),
                    "fonte_url": r.get("fonte_url", ""),
                    "note": r.get("note", ""),
                }
            )

    fields = [
        "comune",
        "anno",
        "impegni_competenza_euro",
        "popolazione_totale",
        "popolazione_giovane",
        "fascia_giovane",
        "euro_per_residente",
        "euro_per_giovane",
        "verificato",
        "fonte_url",
        "note",
    ]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result)

    by_comune: dict[str, list[dict]] = defaultdict(list)
    for r in result:
        by_comune[r["comune"]].append(r)

    summary = []
    for comune, rows in by_comune.items():
        rows = sorted(rows, key=lambda x: x["anno"], reverse=True)[:3]
        values_abs = [
            float(r["impegni_competenza_euro"])
            for r in rows
            if r["impegni_competenza_euro"] not in (None, "")
        ]
        values_res = [
            float(r["euro_per_residente"])
            for r in rows
            if r["euro_per_residente"] not in (None, "")
        ]
        values_gio = [
            float(r["euro_per_giovane"])
            for r in rows
            if r["euro_per_giovane"] not in (None, "")
        ]

        summary.append(
            {
                "comune": comune,
                "anni_usati": ";".join(str(r["anno"]) for r in rows),
                "n_anni": len(rows),
                "media_impegni_euro": round(mean(values_abs), 2) if values_abs else "",
                "media_euro_per_residente": round(mean(values_res), 2) if values_res else "",
                "media_euro_per_giovane": round(mean(values_gio), 2) if values_gio else "",
            }
        )

    summary.sort(
        key=lambda x: (
            x["media_euro_per_residente"] == "",
            -(x["media_euro_per_residente"] or 0),
        )
    )

    fields_summary = [
        "comune",
        "anni_usati",
        "n_anni",
        "media_impegni_euro",
        "media_euro_per_residente",
        "media_euro_per_giovane",
    ]
    with OUT_MEDIA.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_summary)
        w.writeheader()
        w.writerows(summary)

    print(f"Creato: {OUT.relative_to(ROOT)}")
    print(f"Creato: {OUT_MEDIA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
