from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from app.model import load_model, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = load_model()  # una sola volta, all'avvio
    yield


app = FastAPI(title="Sentiment Service", lifespan=lifespan)


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
