import os
import tempfile

DB_FILE = tempfile.mktemp(suffix="_telemetry_test.db")
os.environ["DB_PATH"] = DB_FILE

from fastapi.testclient import TestClient
from app import main as service


class FakeResponse:
    status_code = 200
    def raise_for_status(self):
        return None


class FakeAsyncClient:
    def __init__(self, *args, **kwargs): pass
    async def __aenter__(self): return self
    async def __aexit__(self, *args): return False
    async def get(self, *args, **kwargs): return FakeResponse()
    async def delete(self, *args, **kwargs): return FakeResponse()


def test_telemetry_idempotency_and_problem_details(monkeypatch):
    service.DB = DB_FILE
    monkeypatch.setattr(service.httpx, "AsyncClient", FakeAsyncClient)
    published = []
    async def fake_publish(key, payload): published.append((key, payload))
    monkeypatch.setattr(service, "publish", fake_publish)

    with TestClient(service.app) as client:
        payload = {"well_id": 1, "pressure": 22.5, "temperature": 75, "flow_rate": 125.5, "vibration": 3.2}
        headers = {"Idempotency-Key": "telemetry-test-001"}
        first = client.post("/api/v1/telemetry", json=payload, headers=headers)
        replay = client.post("/api/v1/telemetry", json=payload, headers=headers)
        conflict = client.post("/api/v1/telemetry", json={**payload, "vibration": 4.1}, headers=headers)
        invalid = client.post("/api/v1/telemetry", json={**payload, "pressure": -1}, headers={"Idempotency-Key": "telemetry-test-002"})

        assert first.status_code == 201
        assert replay.status_code == 201 and replay.json()["replayed"] is True
        assert replay.json()["id"] == first.json()["id"]
        assert conflict.status_code == 409
        assert conflict.headers["content-type"].startswith("application/problem+json")
        assert invalid.status_code == 422
        assert invalid.json()["status"] == 422
        assert len(published) == 1
