from transformers import pipeline

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
LABELS = {"positive", "neutral", "negative"}


def load_model():
    """Carica la pipeline HuggingFace. Da chiamare una sola volta all'avvio."""
    return pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        truncation=True,
        max_length=512,
    )


def predict(classifier, text: str) -> dict:
    result = classifier(text)[0]
    return {"label": result["label"].lower(), "score": float(result["score"])}
