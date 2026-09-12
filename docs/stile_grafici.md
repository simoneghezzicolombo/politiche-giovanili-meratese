# Stile grafico del progetto

I grafici pubblici del progetto usano una identità visiva propria, pensata per giornali locali, social e documenti istituzionali. Il riferimento non è copiare una testata, ma adottare alcune buone pratiche del data journalism: un messaggio per grafico, gerarchia chiara, etichette dirette e fonti sempre visibili.

## Principi

1. **Titolo immediato**: deve essere comprensibile senza leggere la metodologia.
2. **Sottotitolo preciso**: specifica popolazione, unità e anno.
3. **Una sola informazione principale**: niente decorazioni o legende se non servono.
4. **Evidenziazione selettiva**: il blu identifica il dato su cui vogliamo portare l'attenzione; il verde identifica un benchmark istituzionale come la Lombardia; gli altri confronti restano neutri.
5. **Valori direttamente sul grafico** quando aiutano la lettura.
6. **Fonte e nota metodologica brevi ma sempre presenti**.
7. **Stesso formato, font e spaziatura** tra grafici destinati alla stessa lettera o dossier.

## Palette

- testo: `#17212B`
- testo secondario: `#66707A`
- griglia: `#E2E7EB`
- accento: `#2F6BFF`
- accento scuro: `#174EA6`
- benchmark: `#287A6B`
- confronti neutri: `#D8DEE4`

La palette è stata scelta per essere leggibile anche con poco spazio e per evitare il multicolore quando non aggiunge informazione.

## Implementazione

Lo stile condiviso è definito in `visuals/chart_style.py` e viene usato sia dai grafici sulla socialità sia dal benchmark sulla spesa comunale. Le figure principali hanno lo stesso rapporto d'aspetto, la stessa gerarchia tipografica e lo stesso sistema di fonte/note.
