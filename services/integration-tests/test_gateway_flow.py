"""Интеграционная проверка работающего стенда ЛР4 через API Gateway."""
import os
import uuid
import httpx

BASE = os.getenv("LAB4_GATEWAY_URL", "http://localhost:8090").rstrip("/")

def test_gateway_to_registry_telemetry_ml_and_saga():
    token = uuid.uuid4().hex[:12]
    with httpx.Client(base_url=BASE, timeout=20.0, trust_env=False) as client:
        for path in ("/health/registry", "/health/telemetry", "/health/ml", "/health/alert"):
            response = client.get(path)
            assert response.status_code == 200, (path, response.text)

        wells = client.get("/api/v1/wells")
        assert wells.status_code == 200, wells.text
        assert wells.json(), "В реестре должна существовать хотя бы одна скважина"
        well_id = wells.json()[0]["id"]

        measurement = {"well_id": well_id, "pressure": 22.5, "temperature": 75.0, "flow_rate": 125.5, "vibration": 9.0}
        key = f"it-telemetry-{token}"
        first = client.post("/api/v1/telemetry", json=measurement, headers={"Idempotency-Key": key})
        replay = client.post("/api/v1/telemetry", json=measurement, headers={"Idempotency-Key": key})
        conflict = client.post("/api/v1/telemetry", json={**measurement, "vibration": 2.0}, headers={"Idempotency-Key": key})
        assert first.status_code == 201, first.text
        assert replay.status_code == 201 and replay.json()["id"] == first.json()["id"]
        assert replay.json()["replayed"] is True
        assert conflict.status_code == 409
        assert conflict.headers["content-type"].startswith("application/problem+json")

        diagnosis = client.post("/api/v1/predict", json={"measurement_id": first.json()["id"]})
        assert diagnosis.status_code == 200, diagnosis.text
        assert diagnosis.json()["anomaly"] is True

        saga = client.post("/api/v1/workflows/diagnose", json=measurement, headers={"Idempotency-Key": f"it-saga-{token}"})
        assert saga.status_code == 200, saga.text
        assert saga.json()["status"] == "completed"

        invalid = client.post("/api/v1/predict", json={"measurement_id": 0})
        assert invalid.status_code == 422
        assert invalid.headers["content-type"].startswith("application/problem+json")
