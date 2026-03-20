from fastapi.testclient import TestClient
from backend.src.another_backend_api import app as another_app

client_another = TestClient(another_app)

def test_another_read_root():
    response = client_another.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Crowd Predictor Running"}

def test_another_health_check():
    response = client_another.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
