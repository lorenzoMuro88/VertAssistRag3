## Mappatura Stanze / Houseboat e Codici Keybox

Questa tabella elenca in modo univoco i codici keybox associati a ciascuna stanza o houseboat. Ogni unità è identificata con il prefisso `Hb` seguito da un numero.

| Identificativo Stanza | Tipo       | Codice Keybox |
|------------------------|------------|----------------|
| Hb 3                   | Houseboat  | `*03#`         |
| Hb 5                   | Houseboat  | `*05#`         |
| Hb 7                   | Houseboat  | `*06#`         |
| Hb 8                   | Houseboat  | `*08#`         |
| Hb 9                   | Houseboat  | `*09#`         |
| Hb 11                  | Houseboat  | `*19#`         |

### Note per l'indicizzazione automatica (RAG):

- Il campo **"Identificativo Stanza"** rappresenta univocamente una stanza o una houseboat.
- Il campo **"Codice Keybox"** contiene il codice necessario per aprire il keybox associato alla rispettiva stanza.
- Le diciture originali come "Keybox stanza Hb X" sono state normalizzate per migliorare la precisione del matching tra entità.
- Il termine "stanza" è da intendersi come sinonimo funzionale di "houseboat" nel contesto di questa mappatura.