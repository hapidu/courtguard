"""
Integration tests hitting the actual FastAPI app (in-process, no real server
needed) using FastAPI's TestClient. Covers authentication and the combined
scoring endpoint end-to-end.

Run with (from the backend folder, venv activated):
    pytest tests/ -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["COURTGUARD_API_KEY"] = "test-key-for-pytest"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADERS = {"x-api-key": "test-key-for-pytest"}


def test_health_check_does_not_need_api_key():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_history_rejects_missing_api_key():
    response = client.get("/history")
    assert response.status_code in (401, 422)  # 422 if header is just missing entirely


def test_history_rejects_wrong_api_key():
    response = client.get("/history", headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401


def test_history_accepts_correct_api_key():
    response = client.get("/history", headers=HEADERS)
    assert response.status_code == 200
    assert "analyses" in response.json()


def test_combined_scoring_endpoint_high_risk_scenario():
    payload = {
        "video": {"verdict": "fake", "confidence_score": 95},
        "image": {"verdict": "fake", "confidence_score": 90},
        "audio": {"verdict": "fake", "confidence_score": 85},
    }
    response = client.post("/analyze/combined", headers=HEADERS, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "high risk"
    assert data["overall_risk_score"] > 70


def test_combined_scoring_endpoint_low_risk_scenario():
    payload = {
        "video": {"verdict": "real", "confidence_score": 95},
        "image": {"verdict": "real", "confidence_score": 90},
        "audio": {"verdict": "real", "confidence_score": 85},
    }
    response = client.post("/analyze/combined", headers=HEADERS, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "low risk"
    assert data["overall_risk_score"] < 40