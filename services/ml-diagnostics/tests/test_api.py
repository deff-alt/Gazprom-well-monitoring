import os
import tempfile
DB_FILE = tempfile.mktemp(suffix="_ml_test.db")
os.environ["DB_PATH"] = DB_FILE
from fastapi.testclient import TestClient
from app import main as service

def test_ml_validation_uses_problem_details(monkeypatch):
    service.DB = DB_FILE
    with TestClient(service.app) as client:
        invalid = client.post("/api/v1/predict", json={"measurement_id": 0})
        assert invalid.status_code == 422
        assert invalid.headers["content-type"].startswith("application/problem+json")
        assert invalid.json()["title"] == "Ошибка валидации"
        assert client.get("/health").status_code == 200
