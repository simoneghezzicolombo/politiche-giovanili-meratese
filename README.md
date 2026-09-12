# Politiche giovanili nel Meratese

Analisi comparativa delle politiche giovanili nei 24 Comuni dell'Ambito territoriale di Merate, in provincia di Lecco.

## La domanda

Quanto spendono i Comuni per le politiche giovanili?

La risposta più corretta non è un singolo numero. I bilanci comunali permettono però di costruire un indicatore semplice, replicabile e comprensibile: la spesa registrata nel **Programma 02 "Giovani" della Missione 06 "Politiche giovanili, sport e tempo libero"**.

Questo progetto usa quella voce come **indicatore contabile principale**, senza presentarla come se rappresentasse automaticamente tutta la spesa comunale destinata ai giovani.

## Cosa confronteremo

Per ciascuno dei 24 Comuni:

- impegni di competenza del rendiconto nel Programma 06.02;
- euro per residente;
- euro per giovane, quando è disponibile un denominatore demografico omogeneo;
- andamento annuale e media pluriennale;
- eventuali interventi rivolti ai giovani contabilizzati in altre missioni o programmi, documentati separatamente.

L'output pubblico deve essere leggibile anche da chi non conosce la contabilità degli enti locali.

## Regola di comunicazione

La formulazione consigliata è:

> **Quanto spendono i Comuni nella voce di bilancio "Giovani"?**

Non:

> Quanto spendono davvero per i giovani?

La seconda frase sarebbe troppo forte, perché una parte delle politiche che incidono sulla vita dei giovani può essere contabilizzata altrove, per esempio in istruzione, sociale, cultura, sport, trasporti, casa o interventi trasversali.

## Ambito territoriale

L'Ambito territoriale di Merate comprende 24 Comuni:

Airuno, Barzago, Barzanò, Brivio, Calco, Casatenovo, Cassago Brianza, Cernusco Lombardone, Cremella, Imbersago, La Valletta Brianza, Lomagna, Merate, Missaglia, Montevecchia, Monticello Brianza, Olgiate Molgora, Osnago, Paderno d'Adda, Robbiate, Santa Maria Hoè, Sirtori, Verderio e Viganò.

L'elenco è verificato sulle fonti istituzionali dell'Ambito e di ATS Brianza.

## Struttura del repository

```text
data/
  metadata/       elenco dei 24 Comuni
  input/          dati normalizzati da compilare o importare
  output/         tabelle generate dagli script
docs/
  metodologia.md  scelte metodologiche e limiti
  fonti.md        fonti ufficiali e criteri di verifica
scripts/
  01_indicatori.py
  02_grafico.py
```

## Avvio rapido

1. Inserire i dati annuali in `data/input/spesa_programma_giovani.csv`.
2. Inserire le popolazioni in `data/input/popolazione.csv`.
3. Eseguire:

```bash
python scripts/01_indicatori.py
python scripts/02_grafico.py
```

Gli output vengono salvati in `data/output/`.

## Stato

**v0.2, struttura metodologica iniziale.**

Il repository non contiene ancora risultati empirici completi. La priorità della v0.2 è fissare un metodo trasparente prima di costruire classifiche o visualizzazioni.

## Fonti principali

- OpenBDAP, Ragioneria Generale dello Stato: https://openbdap.rgs.mef.gov.it/it/FET/Analizza
- Inquadramento dei bilanci armonizzati: https://openbdap.rgs.mef.gov.it/it/Home/IlBilancioDegliEntiTerritoriali
- ATS Brianza, Comuni e aree distrettuali: https://www.ats-brianza.it/search-results/148-servizi-ai-cittadini/3451-comuni-e-aree-distrettuali
- ISTAT, dati demografici: https://demo.istat.it/
