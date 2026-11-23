import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.model import LABELS


@pytest.fixture(scope="module")
def client():
    # il "with" esegue il lifespan, quindi il modello viene caricato una volta
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_schema(client):
    response = client.post("/predict", json={"text": "I love this product"})
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"label", "score"}
    assert isinstance(body["label"], str)
    assert 0.0 <= body["score"] <= 1.0


def test_predict_label_is_valid(client):
    response = client.post("/predict", json={"text": "It is a table"})
    assert response.json()["label"] in LABELS


def test_empty_text_is_rejected(client):
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422


def test_too_long_text_is_rejected(client):
    response = client.post("/predict", json={"text": "a" * 513})
    assert response.status_code == 422


def test_missing_field_is_rejected(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422
