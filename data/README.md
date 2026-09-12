# Dati

## `metadata/`

Contiene l'elenco dei 24 Comuni dell'Ambito territoriale di Merate e la distinzione territoriale Meratese/Casatese usata solo come metadato descrittivo.

## `input/spesa_programma_giovani.csv`

Una riga per Comune e anno.

Campi:

- `comune`
- `anno`
- `impegni_competenza_euro`
- `fonte_url`
- `data_acquisizione`
- `verificato`
- `note`

Il campo monetario principale deve riferirsi sempre agli **impegni di competenza** del Programma 06.02 nel rendiconto.

## `input/popolazione.csv`

Una riga per Comune e anno.

La colonna `popolazione_giovane` è facoltativa. Se valorizzata, `fascia_giovane` deve essere identica per tutti i Comuni confrontati nello stesso output.

## `input/interventi_extra_0602.csv`

Registro separato degli interventi rivolti ai giovani ma contabilizzati fuori dal Programma 06.02.

Questi valori non vengono sommati automaticamente alla misura principale.

## `output/`

Generato dagli script. Non modificare manualmente i file derivati.
