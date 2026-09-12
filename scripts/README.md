# Pipeline

## 01_openbdap.py
Legge CSV/XLSX/ZIP ufficiali OpenBDAP/RGS, individua le colonne rilevanti e produce per Comune:

- impegni M06-P02 Titolo 1;
- impegni M06-P02 Titolo 2;
- impegni complessivi Titolo 1.

Se trova una colonna di macroaggregato, usa le righe di dettaglio valorizzate per ridurre il rischio di doppio conteggio dei subtotali.

## 02_istat_population.py
Legge il file Istat della popolazione residente per singola età e produce:

- popolazione totale;
- popolazione 15-29 anni.

## 03_build_dataset.py
Seleziona i 24 Comuni e calcola:

- €/abitante;
- €/residente 15-29;
- M06-P02 come % della spesa corrente.

Dati mancanti e valori zero restano distinti.

## 04_benchmark.py
Calcola mediana, quartili, media e quota di zeri per classe demografica sui Comuni lombardi.

## 05_audit_low_values.py
Seleziona automaticamente gli zero e il quartile inferiore per l’audit documentale.

## 06_figures.py
Produce il grafico orizzontale principale ordinato per €/residente 15-29.
