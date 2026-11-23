import pytest

from app.model import LABELS, load_model, predict


@pytest.fixture(scope="module")
def classifier():
    return load_model()


@pytest.mark.parametrize(
    "text",
    [
        "I absolutely love this, it is fantastic",
        "What a wonderful day, I am so happy",
        "Great service, highly recommended",
    ],
)
def test_clearly_positive(classifier, text):
    assert predict(classifier, text)["label"] == "positive"


@pytest.mark.parametrize(
    "text",
    [
        "This is the worst experience ever, I hate it",
        "Terrible product, a complete waste of money",
        "I am so disappointed and angry",
    ],
)
def test_clearly_negative(classifier, text):
    assert predict(classifier, text)["label"] == "negative"


def test_label_is_one_of_three_classes(classifier):
    result = predict(classifier, "The meeting is at 3 pm")
    assert result["label"] in LABELS
