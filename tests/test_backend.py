import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_health_check_no_model():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    # Test assumes no model is loaded initially
    assert data["model_loaded"] is False


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the MakanMap Crowdedness API"}


def test_predict_no_model():
    # If the model is not loaded, calling predict should return a 503 error
    payload = {
        "location_id": "1",
        "location_freq": 100,
        "temperature": 30.0,
        "humidity": 60.0,
        "weather": "clear",
        "is_public_holiday": 0,
        "bins_ahead": 1,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "Model not loaded. Ensure the model.pkl file is available."
    )


def test_predict_invalid_weather():
    # Model doesn't need to be loaded to test validation
    payload = {
        "location_id": "1",
        "location_freq": 100,
        "temperature": 30.0,
        "humidity": 60.0,
        "weather": "invalid_weather",
        "is_public_holiday": 0,
        "bins_ahead": 1,
    }
    response = client.post("/predict", json=payload)
    assert (
        response.status_code == 422
    )  # FastAPI validation error for pydantic constraints, or 400 if our internal validation catches it first, let's assume valid weather is checked downstream


# For a complete test suite we'd need a mock model to test the actual prediction logic,
# but these tests cover the API endpoints and error handling mechanisms.
