import sys
from unittest.mock import MagicMock

# Mock joblib so predict_api doesn't crash on import
import joblib
mock_model = MagicMock()
joblib.load = MagicMock(return_value={
    "model": mock_model,
    "bin_edges": []
})

from fastapi.testclient import TestClient
from backend.src.another_backend_api import app as another_app
from backend.src.predict_api import app as predict_app

client_another = TestClient(another_app)
client_predict = TestClient(predict_app)

def test_another_read_root():
    response = client_another.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Crowd Predictor Running"}

def test_another_health_check():
    response = client_another.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_predict_health_check():
    response = client_predict.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_predict_read_root():
    response = client_predict.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MakanMap Crowdedness API is running"}
