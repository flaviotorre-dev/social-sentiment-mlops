# social-sentiment-mlops

Servizio didattico di sentiment analysis con FastAPI e il modello
`cardiffnlp/twitter-roberta-base-sentiment-latest`.

## API

- `GET /health`: verifica che l'API risponda.
- `POST /predict`: riceve `{"text": "..."}` e restituisce `{"label", "score"}`.
  Il testo deve contenere da 1 a 512 caratteri.
- `GET /metrics`: metriche Prometheus.

Esempio:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text":"I love this product"}'
```

## Sviluppo e test

È richiesto Python 3.14, come in CI e nell'immagine Docker.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest
ruff check .
ruff format --check .
```

Per avviare solo l'API localmente:

```bash
uvicorn app.main:app --reload
```

## Docker e CI/CD

Build e avvio dell'immagine:

```bash
docker build -t social-sentiment-mlops .
docker run --rm -p 8000:8000 social-sentiment-mlops
```

La build scarica il modello nell'immagine, che è quindi pesante, ma non richiede
una connessione a Hugging Face all'avvio. La GitHub Action esegue lint, controllo
formattazione e test; solo un push su `main`, dopo il successo dei test, costruisce
e pubblica l'immagine su [GHCR](https://github.com/flaviotorre-dev/social-sentiment-mlops/pkgs/container/social-sentiment-mlops)
con tag `latest` e tag basato sullo SHA.

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

Imposta una password locale in `GRAFANA_ADMIN_PASSWORD`, poi dalla radice del
progetto esegui:

```bash
export GRAFANA_ADMIN_PASSWORD='<password-locale>'
docker compose up --build
```

- API: <http://localhost:8000> (`/health`, `/predict`, `/metrics`)
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000> (utente `admin`, password impostata nell'ambiente)

Prometheus raccoglie le metriche dall'API ogni 15 secondi. Grafana carica
automaticamente il datasource e la dashboard predisposti in `monitoring/`.
L'alert è consultabile nella sezione **Alerts** di Prometheus; questa configurazione
non invia notifiche esterne.

## DAG Airflow

`airflow/dags/retraining_dag.py` definisce un DAG settimanale dimostrativo:
`collect_data >> evaluate_model >> decide >> (retrain | skip)`. I task passano il
conteggio dei dati e l'accuracy via XCom. Se l'accuracy scende sotto 0,75 viene
scelto `retrain`; altrimenti `skip`. Raccolta, valutazione e retraining sono stub:
non scaricano dati, non valutano un modello reale e non avviano un addestramento.
Il progetto non include uno stack Airflow.

## Documento di review

[Apri il notebook in Google Colab](https://colab.research.google.com/github/flaviotorre-dev/social-sentiment-mlops/blob/main/notebooks/review.ipynb).
