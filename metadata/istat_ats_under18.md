# Fonte Istat ATS per il benchmark under 18

- Dataset: **Utenti e spesa - Ambiti territoriali sociali (ATS)**
- Dataflow: `47_940_DF_DCIS_SPESESERSOC1_5`
- Area: `FAM - Famiglia e minori`
- Anni acquisiti: 2021, 2022, 2023
- Indicatore di spesa utilizzato: `EXPMUN - Spesa dei comuni (euro)`
- Denominatore: popolazione target 0-17 dell'area Famiglia e minori
- Data acquisizione dei file usati in questa analisi: 12 settembre 2026

Il CSV in `data/raw/istat_ats/` è un'estrazione compatta degli export originali da IstatData per i sei territori usati nel confronto: Lombardia, Bellano, Carate Brianza, Lecco, Isola Bergamasca e Merate. Conserva tutte le righe necessarie per ricostruire numeratore e denominatore dell'indicatore.

Vedi `docs/benchmark_istat_under18.md` per le scelte analitiche.
