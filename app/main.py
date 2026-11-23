import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel, Field

from app.model import load_model, predict

REQUESTS = Counter("http_requests_total", "Richieste HTTP", ["path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Latenza richieste HTTP", ["path"])
PREDICTIONS = Counter("predictions_total", "Predizioni per classe", ["label"])
TEXT_LENGTH = Histogram(
    "input_text_length_chars",
    "Lunghezza dei testi in ingresso",
    buckets=(10, 25, 50, 100, 200, 300, 512),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = load_model()  # una sola volta, all'avvio
    yield


app = FastAPI(title="Sentiment Service", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    path = request.url.path
    if not path.startswith("/metrics"):
        LATENCY.labels(path).observe(time.perf_counter() - start)
        REQUESTS.labels(path, str(response.status_code)).inc()
    return response


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=512)


class PredictResponse(BaseModel):
    label: str
    score: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(body: PredictRequest, request: Request):
    result = predict(request.app.state.classifier, body.text)
    PREDICTIONS.labels(result["label"]).inc()
    TEXT_LENGTH.observe(len(body.text))
    return result
