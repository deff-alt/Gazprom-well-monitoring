import os
import tempfile
DB_FILE = tempfile.mktemp(suffix="_registry_test.db")
os.environ["DB_PATH"] = DB_FILE
from fastapi.testclient import TestClient
from app import main as service

def test_registry_idempotency_and_problem_details():
    with TestClient(service.app) as client:
        payload = {"well_number": "TEST-LAB4-001", "locality_id": 1, "type": "Добывающая", "status": "active", "depth": 2500}
        headers = {"Idempotency-Key": "registry-test-001"}
        first = client.post("/api/v1/wells", json=payload, headers=headers)
        replay = client.post("/api/v1/wells", json=payload, headers=headers)
        conflict = client.post("/api/v1/wells", json={**payload, "depth": 2600}, headers=headers)
        invalid = client.post("/api/v1/wells", json={**payload, "depth": -1}, headers={"Idempotency-Key": "registry-test-002"})
        assert first.status_code == 201
        assert replay.status_code == 201 and replay.json()["id"] == first.json()["id"]
        assert conflict.status_code == 409
        assert invalid.status_code == 422
        for response in (conflict, invalid):
            assert response.headers["content-type"].startswith("application/problem+json")
            assert response.json()["status"] == response.status_code
