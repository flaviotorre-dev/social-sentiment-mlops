from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from app.model import load_model, predict

from prometheus_client import Counter, make_asgi_app

REQUESTS = Counter("http_requests_total", "Richieste HTTP", ["path", "status"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = load_model()  # una sola volta, all'avvio
    yield


app = FastAPI(title="Sentiment Service", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/metrics"):
        REQUESTS.labels(request.url.path, str(response.status_code)).inc()
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
    return predict(request.app.state.classifier, body.text)
