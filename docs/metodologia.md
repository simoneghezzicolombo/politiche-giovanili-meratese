# Metodologia

## 1. Obiettivo

Costruire un confronto semplice, trasparente e replicabile tra i 24 Comuni dell'Ambito territoriale di Merate, evitando di attribuire ai dati di bilancio un significato più ampio di quello che possono sostenere.

L'indicatore principale misura la spesa contabilizzata nel **Programma 02 "Giovani" della Missione 06 "Politiche giovanili, sport e tempo libero"**.

## 2. Perché il confronto è possibile

Dal 2016 gli enti territoriali adottano schemi di bilancio armonizzati. Missioni e programmi sono livelli comuni di classificazione della spesa, quindi la stessa voce può essere confrontata tra Comuni.

Per il rendiconto, la grandezza principale usata in questo progetto è l'**impegno di competenza**. Gli impegni descrivono obbligazioni giuridicamente perfezionate imputate all'esercizio e sono più adatti di un semplice stanziamento a rappresentare la spesa effettivamente assunta dall'ente nell'anno.

## 3. Che cosa misura davvero 06.02

Il Programma 06.02 è utile perché identifica una voce di bilancio esplicitamente dedicata ai giovani.

Non coincide però necessariamente con la totalità delle politiche giovanili. Un Comune può realizzare interventi rivolti ai giovani anche attraverso:

- istruzione e diritto allo studio;
- servizi sociali e contrasto alla povertà;
- cultura e biblioteche;
- sport;
- trasporto pubblico e mobilità;
- politiche abitative;
- sicurezza e prevenzione;
- formazione, lavoro e orientamento;
- progetti finanziati in forma associata o tramite altri enti.

Per questo motivo il dato 06.02 viene chiamato nel progetto **spesa contabilizzata nel Programma Giovani**, non **spesa totale per i giovani**.

## 4. Indicatore principale

Per ogni Comune e anno:

```text
spesa_06_02 = impegni di competenza della Missione 06, Programma 02
```

Vengono poi calcolati:

```text
euro_per_residente = spesa_06_02 / popolazione_totale
euro_per_giovane = spesa_06_02 / popolazione_giovane
```

L'indicatore per giovane viene prodotto solo se il denominatore è disponibile con la stessa definizione e lo stesso riferimento temporale per tutti i Comuni.

## 5. Fascia d'età

La v0.2 non impone una definizione sostantiva unica di "giovane" ai fini del bilancio, perché il Programma 06.02 non è vincolato a una singola fascia anagrafica.

Per le normalizzazioni demografiche il repository prevede una colonna configurabile. La fascia consigliata per una prima lettura territoriale è **15-34 anni**, ma ogni output deve dichiarare esplicitamente la fascia utilizzata.

La comparazione principale resta comunque disponibile anche in euro per residente, che non richiede una definizione convenzionale di gioventù.

## 6. Periodo temporale

Le politiche giovanili dei piccoli Comuni possono essere molto discontinue. Un progetto finanziato una tantum può far apparire enorme un anno e quasi nullo quello successivo.

Per questo vengono mostrati:

1. il valore di ogni singolo anno;
2. la media degli ultimi tre rendiconti completi disponibili;
3. la serie storica, quando disponibile.

Alla data della v0.2, OpenBDAP pubblica anche il Rendiconto 2025 dei Comuni. La finestra di default proposta è quindi **2023-2025**, senza impedire analisi più lunghe.

## 7. Zero non significa necessariamente "nessuna politica giovanile"

Un valore pari a zero nel Programma 06.02 può significare cose diverse:

- assenza di spesa esplicitamente classificata nel programma;
- attività rivolte ai giovani contabilizzate in altri programmi;
- servizi gestiti in forma associata;
- trasferimenti o progetti che richiedono una lettura più approfondita;
- differenze nelle pratiche di classificazione contabile.

Per questo le visualizzazioni devono evitare formule accusatorie come "Comune che non spende per i giovani".

## 8. Secondo livello: interventi fuori dal 06.02

Il repository prevede un file separato, `data/input/interventi_extra_0602.csv`, per documentare interventi chiaramente rivolti ai giovani ma contabilizzati altrove.

Questi importi **non vengono sommati automaticamente** all'indicatore principale. Prima di costruire un indicatore allargato serve una regola di inclusione uniforme per tutti i Comuni.

Il secondo livello serve soprattutto a rispondere alla domanda:

> Il Programma 06.02 racconta bene la politica giovanile di questo Comune oppure ne fotografa solo una parte?

## 9. Lettura consigliata per il pubblico

Per evitare una classifica fuorviante, l'ordine di lettura dovrebbe essere:

1. valore medio pluriennale pro capite;
2. valore assoluto;
3. andamento nel tempo;
4. nota sulla copertura del 06.02;
5. eventuali interventi extra documentati.

La visualizzazione principale deve avere un sottotitolo che ricordi che si tratta della voce contabile Programma Giovani.

## 10. Controlli di qualità

Ogni osservazione deve avere, quando possibile:

- Comune;
- anno;
- tipo di documento;
- grandezza contabile;
- importo;
- URL della fonte;
- data di acquisizione;
- eventuale nota;
- flag di verifica.

I valori anomali o nulli devono essere verificati sul documento dell'ente prima della pubblicazione.

## 11. Cosa non fare

Non:

- sommare voci di missioni diverse senza criteri comuni;
- confrontare preventivi di un Comune con rendiconti di un altro;
- usare stanziamenti per alcuni enti e impegni per altri;
- interpretare automaticamente uno zero come assenza di politiche;
- chiamare il 06.02 "tutta la spesa per i giovani";
- costruire un ranking definitivo prima di verificare casi anomali.

## 12. Principio guida

**Meglio un indicatore più stretto ma confrontabile, accompagnato da una spiegazione chiara dei suoi limiti, che un numero apparentemente completo costruito con criteri diversi Comune per Comune.**
