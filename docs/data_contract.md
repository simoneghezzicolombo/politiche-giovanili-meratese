# Contratto dei dati

La pipeline produce un record per Comune e anno.

## Variabili principali

- `m0602_corrente_impegni`: impegni 2024 del Programma 06.02, Titolo 1.
- `m0602_capitale_impegni`: impegni 2024 del Programma 06.02, Titolo 2.
- `spesa_corrente_totale_impegni`: impegni complessivi del Titolo 1.
- `pop_totale`: popolazione residente al 1° gennaio 2024.
- `pop_15_29`: residenti di età 15-29 anni al 1° gennaio 2024.
- `eur_m0602_per_giovane_15_29`: indicatore principale.
- `eur_m0602_per_abitante`: indicatore secondario.
- `pct_spesa_corrente_m0602`: quota percentuale della spesa corrente.

## Regole

1. Non si mescolano impegni, pagamenti e stanziamenti.
2. Corrente e conto capitale restano separati.
3. Un valore M06-P02 pari a zero non viene interpretato come assenza di politiche giovanili.
4. I casi nulli o nel quartile inferiore entrano nell'audit documentale.
5. Ogni dato pubblicato deve avere una fonte primaria registrata in `metadata/source_log.csv`.
