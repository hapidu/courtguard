import os
import joblib
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "..", "ml", "phishing_model.pkl")

_model = None


def get_model():
    """Loads the model once and reuses it (lazy loading)."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "phishing_model.pkl not found. Run "
                "'python -m app.ml.train_text_model' from the backend folder first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


class TextRequest(BaseModel):
    text: str


@router.post("")
def analyze_text(request: TextRequest):
    model = get_model()

    prediction = model.predict([request.text])[0]
    probabilities = model.predict_proba([request.text])[0]
    classes = list(model.classes_)
    confidence = float(max(probabilities))

    is_phishing = prediction == "phishing"

    return {
        "verdict": "suspicious" if is_phishing else "legitimate",
        "confidence_score": round(confidence * 100, 2),
        "details": {
            "predicted_label": prediction,
            "class_probabilities": {
                cls: round(float(prob) * 100, 2)
                for cls, prob in zip(classes, probabilities)
            },
        },
    }
