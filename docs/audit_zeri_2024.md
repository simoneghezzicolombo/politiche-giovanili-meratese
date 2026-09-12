# Audit dei Comuni con M06-P02 = 0 nel 2024

## Scopo

Nel dataset OpenBDAP 2024, 18 dei 24 Comuni dell'Ambito di Merate registrano zero euro di spesa corrente nella Missione 06, Programma 02 “Giovani”. Questo audit serve a verificare se lo zero contabile coincida o meno con assenza di attività comunali rivolte ai giovani.

L'audit **non ricostruisce ancora la spesa totale per i giovani** e non somma automaticamente importi contabilizzati in altre missioni o gestioni associate. Il suo scopo è più limitato: individuare falsi equivalenti tra “M06-P02 = 0” e “nessuna politica o attività rivolta ai giovani”.

## Classificazione

- **A — azione comunale 2024 documentata**: esiste una specifica iniziativa, misura o struttura attiva del Comune nel 2024.
- **B — gestione associata 2024 documentata**: esiste una specifica attività 2024 rivolta ai giovani, ma il finanziamento o la gestione passa almeno in parte dall'Ambito/Retesalute o da altra gestione associata.
- **C — programmazione 2024 documentata**: il Comune programma esplicitamente politiche giovanili, ma la fonte trovata non dimostra da sola l'effettiva realizzazione o spesa nel 2024.
- **D — nessuna azione comunale 2024 identificata**: la ricerca non ha trovato una prova sufficiente. Questa categoria non significa che il Comune non abbia svolto alcuna attività.

## Risultato sintetico

Sui 18 Comuni con M06-P02 corrente pari a zero:

- **11** presentano almeno una **azione comunale 2024 direttamente documentata**;
- **5** presentano una **attività 2024 documentata in gestione associata**;
- **1**, Imbersago, presenta una **programmazione comunale esplicita** sulle politiche giovanili, ma la fonte analizzata non basta a quantificare l'attuazione 2024;
- **1**, Viganò, non ha restituito in questa ricognizione una specifica azione comunale 2024 sufficientemente documentata.

Quindi, per **17 dei 18 zeri contabili**, è stata trovata almeno una traccia concreta di attività, gestione associata o programmazione giovanile. Questo rende metodologicamente insostenibile leggere lo zero M06-P02 come equivalente automatico a “zero politiche giovanili”.

## Evidenze comunali particolarmente chiare fuori da M06-P02

Tra i casi più netti:

- **Merate**: bando comunale 2024 “Merito e reddito” con **10.000 euro stanziati** per studenti delle scuole secondarie di secondo grado.
- **Airuno**: **1.400 euro** stanziati per cinque borse di studio consegnate nel febbraio 2024.
- **Cassago Brianza**: bando comunale approvato nel novembre 2024 per borse di studio a diplomati e laureati.
- **Missaglia**: venti studenti premiati con borse di studio comunali nel febbraio 2024.
- **Monticello Brianza**: diciannove borse di studio consegnate nel febbraio 2024.
- **Sirtori**: borse di studio comunali assegnate nel dicembre 2024.
- **Verderio**: bando comunale 2024 per borse di studio riferite all'anno scolastico 2023/2024.
- **Cernusco Lombardone**: prima cerimonia comunale di consegna della Costituzione ai neo-diciottenni nel giugno 2024.
- **La Valletta Brianza**: istituzione del Consiglio Comunale dei ragazzi e delle ragazze nel 2024.
- **Olgiate Molgora** e **Paderno d'Adda**: consulte giovani comunali con attività documentate nel 2024.

## Attenzione alla fascia 15-29

La popolazione 15-29 viene usata nel progetto come denominatore demografico uniforme per rendere confrontabile M06-P02. Non è però una definizione normativa del Programma 06.02.

Alcune evidenze dell'audit, per esempio Consigli comunali dei ragazzi o borse di studio alla scuola secondaria di primo grado, coinvolgono anche persone sotto i 15 anni. Queste evidenze sono utili per dimostrare che lo zero contabile non equivale a assenza di attività, ma **non devono essere trasformate automaticamente in spesa per la popolazione 15-29**.

## Gestione associata

I casi classificati B restano volutamente separati. Il lavoro su Ambito di Merate e Retesalute dovrà chiarire:

1. il costo complessivo dei progetti;
2. il criterio di finanziamento;
3. l'eventuale quota dei singoli Comuni;
4. il capitolo o la missione con cui le quote comunali vengono contabilizzate.

Finché questi elementi non sono disponibili, gli importi associati non vengono attribuiti ai singoli Comuni.

## Regola per l'output pubblico

La formulazione corretta è:

> Nel 2024 il Comune registra 0 euro di spesa corrente nel Programma 06.02 “Giovani”. L'audit documentale mostra tuttavia [azione/attività/programmazione], contabilizzata o gestita fuori da questa specifica voce.

Non usare:

> Il Comune non spende nulla per i giovani.

## Dataset

Il dettaglio riga per riga, con fonte, tipo di evidenza, gestione e livello di confidenza, è in `metadata/audit_zeri_2024.csv`.
