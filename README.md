# Politiche giovanili nei Comuni dell’Ambito di Merate

Analisi comparativa della spesa comunale **esplicitamente classificata come Missione 06, Programma 02 “Giovani”** nei 24 Comuni dell’Ambito territoriale di Merate.

L’obiettivo è produrre un confronto comprensibile anche fuori dagli ambienti tecnici, senza attribuire a M06-P02 un significato più ampio di quello che la classificazione contabile consente.

## La domanda in una frase

**Quanto contabilizzano i Comuni del Meratese nel programma di bilancio dedicato ai giovani, per ogni residente tra 15 e 29 anni?**

## Indicatore principale

**Euro di spesa corrente M06-P02 impegnati nel 2024 per residente 15-29 anni.**

Indicatori di supporto:

- euro M06-P02 corrente per abitante;
- M06-P02 corrente come percentuale della spesa corrente comunale;
- investimenti M06-P02 in conto capitale, mostrati separatamente;
- confronto con Comuni lombardi della stessa classe demografica.

## Cosa NON significa il dato

M06-P02 **non rappresenta necessariamente tutta la spesa destinata ai giovani**. Progetti per adolescenti e giovani possono essere contabilizzati in istruzione, servizi sociali, cultura, sport, lavoro oppure essere gestiti in forma associata tramite l’Ambito territoriale.

Per questo un valore pari a zero non viene mai tradotto automaticamente in “nessuna politica giovanile”. I valori nulli o molto bassi vengono sottoposti a un audit documentale separato.

## Anno e misura

- Rendiconto della gestione: **2024**
- Misura: **impegni di competenza**
- Spesa corrente: **Titolo 1**
- Investimenti: **Titolo 2**, tenuti separati
- Popolazione: residenti al **1° gennaio 2024**
- Fascia giovane: **15-29 anni**

## Fonti primarie

- [RGS / OpenBDAP, Finanza degli Enti Territoriali](https://openbdap.rgs.mef.gov.it/it/FET/Analizza)
- [Istat, Demografia in cifre, popolazione residente per sesso ed età](https://demo.istat.it/app/?i=POS)
- Rendiconti, DUP, PEG e Amministrazione Trasparente dei singoli Comuni per gli approfondimenti
- Retesalute / Ufficio di Piano dell’Ambito di Merate per la gestione associata

OpenBDAP specifica che l’area Finanza degli Enti Territoriali utilizza documenti di bilancio approvati in via definitiva e trasmessi alla RGS. Istat rende disponibili file CSV della popolazione residente comunale per singola età.

## Pipeline

```text
OpenBDAP/RGS 2024 ─┐
                   ├─> dataset comunale ─> indicatori ─> audit ─> grafici
Istat 1/1/2024 ────┘
```

Gli script **non dipendono dall’interfaccia web** dei due portali. Accettano i file ufficiali CSV/XLSX/ZIP scaricati dalle rispettive aree dati, così l’analisi resta replicabile anche se cambia la UI.

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

1. Scaricare il rendiconto armonizzato 2024 da OpenBDAP e salvarlo in `data/raw/`.
2. Scaricare da Istat la popolazione residente per singola età al 1° gennaio 2024 e salvarla in `data/raw/`.
3. Eseguire:

```bash
python scripts/01_openbdap.py --input data/raw/NOME_FILE_OPENBDAP.zip
python scripts/02_istat_population.py --year 2024  # scarica automaticamente POSAS_2024_it_Comuni.zip
python scripts/03_build_dataset.py
python scripts/05_audit_low_values.py
python scripts/06_figures.py
```

Oppure, con `make`:

```bash
make openbdap OPENBDAP=data/raw/NOME_FILE_OPENBDAP.zip
make istat ISTAT=data/raw/NOME_FILE_ISTAT.zip  # oppure eseguire direttamente lo script senza --input
make dataset
```

Gli script sono intenzionalmente **fail-fast**: se lo schema del file ufficiale non è riconosciuto, si fermano e mostrano le colonne disponibili invece di produrre valori incerti.

## Struttura

- `config/`: elenco dei 24 Comuni
- `data/raw/`: fonti originali non modificate
- `data/interim/`: estrazioni normalizzate
- `data/processed/`: dataset finale
- `metadata/`: registro delle fonti e audit dei casi anomali
- `scripts/`: pipeline riproducibile
- `docs/`: metodologia e contratto dei dati
- `outputs/`: tabelle e grafici destinati alla comunicazione

## Output pubblico

Il grafico principale risponde a una sola domanda: **quanti euro vengono esplicitamente contabilizzati nel Programma “Giovani” per ogni residente 15-29enne?**

Nota standard da accompagnare al grafico:

> Il dato riguarda la spesa corrente contabilizzata nel Programma 06.02 “Giovani” e non necessariamente tutte le attività comunali rivolte ai giovani. I valori molto bassi o nulli sono verificati separatamente.

La complessità metodologica resta nel repository. L’output pubblico deve restare leggibile.

## Benchmark complementare Istat: opportunità per under 18

Accanto al benchmark contabile M06-P02, il repository include ora un secondo indicatore, costruito sui dati Istat **Interventi e servizi sociali dei Comuni - Ambiti territoriali sociali (ATS)**.

La domanda è diversa: **quanto spendono i territori, per residente 0-17, in un paniere omogeneo di opportunità sociali, ricreative e di autonomia?**

Il paniere comprende attività ricreative/sociali/culturali, centri di aggregazione, centri estivi e interventi di sostegno o contributo all'inserimento lavorativo.

Nel 2023 il **Meratese registra circa 8,3 euro per residente 0-17**, contro circa **16,4 euro della Lombardia**.

Questo indicatore **non viene definito "spesa per politiche giovanili"**: è un proxy più circoscritto, costruito per confrontare una dimensione particolarmente pertinente al tema degli spazi, della socialità e delle opportunità per ragazze e ragazzi.

Dettagli, fonti e limiti: [`docs/benchmark_istat_under18.md`](docs/benchmark_istat_under18.md).

Per rigenerare dati e grafico:

```bash
python scripts/07_istat_under18_benchmark.py
```

## Stato del progetto

- [x] disegno metodologico
- [x] struttura riproducibile del repository
- [x] parser flessibile per file OpenBDAP/RGS
- [x] parser per popolazione Istat per singola età
- [x] calcolo degli indicatori
- [x] generazione automatica della coda di audit
- [x] primo grafico pubblico
- [x] benchmark ATS Istat su opportunità sociali, ricreative e di autonomia 0-17
- [ ] acquisizione del file OpenBDAP 2024 definitivo
- [ ] acquisizione del file Istat 1/1/2024
- [ ] validazione dei 24 Comuni
- [ ] benchmark Lombardia M06-P02
- [ ] audit documentale dei valori bassi/nulli
