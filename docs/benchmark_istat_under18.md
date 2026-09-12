# Benchmark Istat sulle opportunità per under 18

## Scopo

Questo indicatore nasce come complemento al benchmark di bilancio M06-P02 del repository.
Non tenta di misurare **tutte le politiche giovanili**. Isola invece un insieme omogeneo
di spese sociali comunali che descrivono opportunità di socialità, tempo libero e prime
forme di autonomia per la popolazione minorenne.

Per la comunicazione pubblica si può parlare di **opportunità per ragazze e ragazzi**.
Nel testo metodologico va sempre specificato che il denominatore è la popolazione
**0-17 anni**.

## Fonte

IstatData / EsploraDati, dataflow:

`IT1,47_940_DF_DCIS_SPESESERSOC1_5,1.0`

**Utenti e spesa - Ambiti territoriali sociali (ATS)**, area di utenza
`FAM - Famiglia e minori`, anni 2021-2023.

URL di partenza:
https://esploradati.istat.it/databrowser/#/it/dw/categories/IT1,Z0800SSW,1.0/SSW_SOCSE/DCIS_SPESESERSOC1/IT1,47_940_DF_DCIS_SPESESERSOC1_5,1.0

## Numeratore

Si usa esclusivamente `EXPMUN - Spesa dei comuni (euro)`, cioè la spesa pubblica
dei Comuni singoli o associati, al netto della compartecipazione degli utenti e del
Servizio sanitario nazionale.

Il paniere somma sei voci:

| Codice | Voce Istat |
|---|---|
| `RICSOC` | Attività ricreative, sociali, culturali |
| `AGGRC` | Centri di aggregazione / sociali |
| `SUMDAYC` | Centri diurni estivi |
| `WSRESID` | Centri estivi o invernali (con pernottamento) |
| `EMPLOY` | Sostegno all'inserimento lavorativo |
| `CONTEMP` | Contributi per l'inserimento lavorativo |

Sono escluse volutamente le voci prevalentemente assistenziali o legate alla presa in
carico di fragilità, come sostegno socio-educativo scolastico e domiciliare, affidamento,
adozione, residenzialità e contributi economici generici.

## Denominatore

Per l'area `Famiglia e minori`, Istat usa come popolazione target i residenti 0-17 anni.

Nei file ATS esportati la popolazione target non è fornita direttamente. Viene ricostruita
come:

`Spesa dei comuni - Famiglia e minori, tutte le voci / EXPTPOP della stessa area`

dove `EXPTPOP` è il rapporto Istat "Spesa dei comuni sulla popolazione di riferimento".

Poiché Istat pubblica `EXPTPOP` arrotondato all'euro, il denominatore ricostruito e quindi
il valore composito presentano una piccola approssimazione. Il controllo sul Meratese con
la popolazione POSAS 0-17 dà uno scarto dell'ordine dell'1%, non sufficiente a modificare
l'interpretazione del confronto.

## Formula

`Indicatore = somma EXPMUN delle 6 voci / popolazione target 0-17`

Unità: euro per residente 0-17.

## Risultato 2023

| Territorio | €/residente 0-17 |
|---|---:|
| Bellano | 25,4 |
| Caratese | 16,5 |
| Lombardia | 16,4 |
| Lecchese | 12,8 |
| Isola Bergamasca | 10,6 |
| Meratese | 8,3 |

Il Meratese è circa al **51% della media lombarda** nel 2023.

Il controllo temporale mostra inoltre che, nel gruppo selezionato, il Meratese presenta
il valore più basso in tutti e tre gli anni 2021, 2022 e 2023. Questo rafforza la lettura
del dato 2023 come differenza persistente e non come singola anomalia annuale.

## Come comunicarlo

Formulazione consigliata:

> Nel 2023 il Meratese ha registrato circa 8 euro di spesa comunale per residente under 18
> nelle attività sociali, ricreative e di autonomia considerate, circa la metà della media
> lombarda.

Da evitare:

> Il Meratese spende 8 euro per le politiche giovanili.

La seconda frase sarebbe metodologicamente eccessiva: l'indicatore non comprende l'intero
universo delle politiche giovanili, che può essere finanziato anche attraverso cultura,
sport, istruzione, trasporti, lavoro e altri capitoli.

## Riproducibilità

Eseguire:

```bash
python scripts/07_istat_under18_benchmark.py
```

Input:
- `data/raw/istat_ats/istat_ats_selected_2021_2023.csv`

Il file è un'estrazione compatta dei tre export IstatData originali e conserva tutte
le righe necessarie per riprodurre numeratore e denominatore del benchmark.

Output:
- `data/processed/istat_under18_opportunities_2021_2023.csv`
- `data/processed/istat_under18_opportunities_components_2021_2023.csv`
- `outputs/benchmark_opportunita_under18_2023.png`
- `outputs/benchmark_opportunita_under18_2023.svg`
