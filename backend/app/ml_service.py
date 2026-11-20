"""Базовый воспроизводимый ML-контур детекции аномалий телеметрии."""
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

FEATURES = [
    "pressure_before_choke", "temperature_before_choke", "pressure_after_choke",
    "temperature_after_choke", "bottomhole_pressure", "flow_rate_gas",
    "flow_rate_liquid", "water_cut", "vibration",
]
MODEL_PATH = Path(__file__).resolve().parent.parent / "model-artifacts" / "isolation-forest.joblib"


def train(rows):
    matrix = [[float(getattr(row, f)) if getattr(row, f) is not None else np.nan for f in FEATURES] for row in rows]
    if len(matrix) < 20: raise ValueError("Для обучения необходимо не менее 20 точек телеметрии")
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
        ("detector", IsolationForest(n_estimators=250, contamination=0.04, random_state=42)),
    ])
    model.fit(matrix)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "trained_at": datetime.now(timezone.utc).isoformat(), "samples": len(matrix)}, MODEL_PATH)
    return {"samples": len(matrix), "trained_at": datetime.now(timezone.utc).isoformat(), "model": "Isolation Forest"}


def predict(row):
    if not MODEL_PATH.exists(): raise FileNotFoundError("Модель ещё не обучена")
    bundle = joblib.load(MODEL_PATH)
    vector = [[float(getattr(row, f)) if getattr(row, f) is not None else np.nan for f in FEATURES]]
    model = bundle["model"]
    label = int(model.predict(vector)[0])
    raw = float(model.decision_function(vector)[0])
    score = max(0.0, min(1.0, 0.5 - raw))
    scaled = model[:-1].transform(vector)[0]
    available = [(FEATURES[i], abs(float(value))) for i, value in enumerate(scaled)]
    parameter = max(available, key=lambda pair: pair[1])[0] if available else "unknown"
    return {"is_anomaly": label == -1, "anomaly_score": round(score, 4), "decision_score": round(raw, 6), "parameter": parameter, "trained_at": bundle["trained_at"], "training_samples": bundle["samples"]}
