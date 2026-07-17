"""
Trains a simple text classifier that flags social-engineering / phishing text.

This uses TF-IDF + Logistic Regression, which is a completely standard,
explainable approach for a final-year project (you can cite Jurafsky & Martin,
2020, for the NLP pipeline, and scikit-learn's docs for the model itself).

IMPORTANT: the CSV bundled here (sample_data/phishing_sample.csv) is a TINY
starter dataset just so the app works out of the box. For your real results
chapter, replace it with a proper dataset, e.g. the Kaggle "SMS Spam Collection
Dataset" (referenced in your own literature review) or a phishing-email dataset,
and rerun this script.

Run with:
    cd backend
    source venv/bin/activate
    python -m app.ml.train_text_model
"""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
import joblib

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "sample_data", "phishing_sample.csv")
MODEL_PATH = os.path.join(HERE, "phishing_model.pkl")


def train():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna()

    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    print("Evaluation on held-out test data:")
    print(classification_report(y_test, preds))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
