import os
import tempfile
DB_FILE = tempfile.mktemp(suffix="_alert_test.db")
os.environ["DB_PATH"] = DB_FILE
from fastapi.testclient import TestClient
from app import main as service

def test_alert_errors_use_problem_details():
    service.DB = DB_FILE
    with TestClient(service.app) as client:
        invalid = client.patch("/api/v1/alerts/1", json={"status": "unknown"})
        missing = client.patch("/api/v1/alerts/999", json={"status": "resolved"})
        assert invalid.status_code == 422
        assert missing.status_code == 404
        for response in (invalid, missing):
            assert response.headers["content-type"].startswith("application/problem+json")
            assert response.json()["status"] == response.status_code
