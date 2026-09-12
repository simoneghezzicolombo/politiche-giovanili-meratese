# Socialità degli adolescenti lombardi, 2013-2024

Questa cartella raccoglie l'analisi sulla socialità degli adolescenti lombardi costruita sui microdati Istat dell'**Indagine Multiscopo sulle famiglie – Aspetti della vita quotidiana (AVQ)**.

## Indicatore principale

La figura principale mostra la quota di **14-17enni lombardi che incontra gli amici tutti i giorni o più di una volta a settimana**. L'indicatore aggrega le modalità `AMICI = 1` e `AMICI = 2`.

La serie è smussata con la stessa logica usata nel lavoro originario in Stata, equivalente a `tssmooth ma ..., window(3 1 1)`: tre valori precedenti, il valore corrente e un valore successivo, normalizzando sui valori disponibili agli estremi della serie.

## Perché 14-17 anni

Il grafico originario era etichettato 14-19, ma i file intermedi e il do-file effettivamente utilizzato conservano solo `ETAMi = 005` e `006`, cioè **14-15 e 16-17 anni**. La documentazione attuale corregge quindi l'etichetta a 14-17.

## Ponderazione

Il vecchio do-file descriveva alcuni grafici come "ponderati", ma **non applicava il coefficiente `COEFIN`**. Per mantenere la continuità con la serie storica già prodotta, questa cartella conserva la stessa logica non ponderata. Una futura versione potrà affiancare, senza sostituire silenziosamente la serie corrente, una stima effettivamente ponderata.

## File

- `build_socialita.py`: pipeline Python riproducibile;
- `originale/do-socialita.do`: primo do-file originale;
- `originale/do-socialita2.do`: do-file originale con i grafici;
- `data/indicatori_socialita_lombardia_14_17_2013_2024.csv`: serie annuali e smussate;
- `figures/socialita_frequente_lombardia_2013_2024.png`: figura principale per comunicazione pubblica;
- `figures/socialita_frequente_lombardia_2013_2024.svg`: versione vettoriale;
- `figures/qualita_rete_amicale_lombardia_2013_2024.png`: indicatore complementare sulla rete amicale.

## Riproduzione

I microdati grezzi non sono inclusi nel repository. Servono tre archivi locali:

1. `SOCIALITA.zip`, contenente `SOCIALITA/socialitaFINALE.dta`;
2. `AVQ_2023_IT.zip`;
3. `AVQ_2024_IT.zip`.

Esempio:

```bash
python analisi/socialita/build_socialita.py \
  --socialita-zip /percorso/SOCIALITA.zip \
  --avq-2023 /percorso/AVQ_2023_IT.zip \
  --avq-2024 /percorso/AVQ_2024_IT.zip \
  --output-dir analisi/socialita
```

Dipendenze già presenti nel progetto: `pandas` e `matplotlib`.

## Uso pubblico

Per una lettera ai giornali o un comunicato, la formulazione più prudente è:

> In Lombardia la quota di adolescenti 14-17enni che incontra gli amici tutti i giorni o più di una volta a settimana mostra una riduzione marcata nella serie 2013-2024. Il grafico è una rielaborazione dei microdati Istat AVQ e utilizza una media mobile coerente con la procedura originaria.

Il grafico non dimostra da solo le cause del cambiamento e non va presentato come misura esaustiva dell'isolamento sociale.
