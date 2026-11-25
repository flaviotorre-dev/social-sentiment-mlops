# social-sentiment-mlops

Servizio didattico di sentiment analysis con FastAPI e il modello
`cardiffnlp/twitter-roberta-base-sentiment-latest`.

## Segnali monitorati

- **Volume richieste**: richieste HTTP al secondo, distinte per endpoint.
- **Latenza**: distribuzione dei tempi di risposta; dashboard con p95.
- **Errori**: richieste con status HTTP 4xx o 5xx.
- **Classi predette**: conteggio delle predizioni positive, neutral e negative.
- **Lunghezza dei testi**: distribuzione dei caratteri ricevuti (limite API: 512).

L'alert didattico scatta quando la quota di predizioni negative supera il 60% nei
15 minuti precedenti e la condizione permane per 5 minuti. La soglia evidenzia un
possibile cambiamento anomalo nella distribuzione degli output; andrebbe tarata sui
dati e sul traffico attesi in un servizio reale.

## Avvio del servizio e monitoraggio

Imposta `GRAFANA_ADMIN_PASSWORD` nell'ambiente, poi dalla radice del progetto esegui:

```bash
docker compose up --build
```

- API: <http://localhost:8000> (`/health`, `/predict`, `/metrics`)
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000> (utente `admin`)

Prometheus raccoglie le metriche dall'API ogni 15 secondi. Grafana carica
automaticamente il datasource e la dashboard predisposti in `monitoring/`.
L'alert è consultabile nella sezione **Alerts** di Prometheus; questa configurazione
non invia notifiche esterne.
