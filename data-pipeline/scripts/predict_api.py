from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta

# ── App setup ──────────────────────────────────────────────────────────────
app = FastAPI(title="MakanMap Crowdedness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model once at startup ─────────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")

try:
    artifact  = joblib.load(MODEL_PATH)
    model     = artifact["model"]
    bin_edges = artifact["bin_edges"]
    print(f"Model loaded from {MODEL_PATH}")
except FileNotFoundError:
    raise RuntimeError(f"Model file not found at '{MODEL_PATH}'. Train and save the model first.")

WEATHER_MAP = {"rainy": 0, "cloudy": 1, "night_clear": 2, "clear": 3}

# ── Request / Response schemas ─────────────────────────────────────────────
class PredictionRequest(BaseModel):
    location_id: str
    temperature: float
    humidity: float
    weather: str                # "rainy" | "cloudy" | "night_clear" | "clear"
    is_public_holiday: int = 0
    bins_ahead: int = 6         # 30-min slots to forecast (default 6 = 3hrs)

class BinPrediction(BaseModel):
    time_bin: str
    crowdedness_score: float    # 0.0 – 1.0
    crowd_label: str            # Low / Medium / High

class PredictionResponse(BaseModel):
    location_id: str
    predictions: list[BinPrediction]

# ── Helper: build feature rows for future time bins ────────────────────────
def build_future_rows(request: PredictionRequest) -> pd.DataFrame:
    now = datetime.now().replace(second=0, microsecond=0)
    minutes = (now.minute // 30 + 1) * 30
    start = now.replace(minute=0) + timedelta(minutes=minutes)

    rows = []
    for i in range(request.bins_ahead):
        ts = start + timedelta(minutes=30 * i)
        rows.append({
            "time_bin":          ts,
            "day_of_week":       ts.weekday(),
            "hour_of_day":       ts.hour,
            "is_weekend":        int(ts.weekday() >= 5),
            "is_public_holiday": request.is_public_holiday,
            "temperature":       request.temperature,
            "humidity":          request.humidity,
            "weather":           request.weather,
        })
    return pd.DataFrame(rows)

# ── Helper: map model output to 0–1 score + label ─────────────────────────
def score_and_label(predictions: np.ndarray) -> list[tuple[float, str]]:
    label_map = {0: "Low", 1: "Medium", 2: "High"}
    results = []
    for pred in predictions:
        results.append((round(float(pred) / 2.0, 2), label_map.get(int(pred), "Unknown")))
    return results

# ── Endpoint ───────────────────────────────────────────────────────────────
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Example request:
        {
            "location_id": "13",
            "temperature": 29.5,
            "humidity": 78.0,
            "weather": "cloudy",
            "is_public_holiday": 0,
            "bins_ahead": 6
        }

    Example response:
        {
            "location_id": "13",
            "predictions": [
                { "time_bin": "2026-03-13T14:00:00", "crowdedness_score": 0.5, "crowd_label": "Medium" },
                { "time_bin": "2026-03-13T14:30:00", "crowdedness_score": 1.0, "crowd_label": "High" },
                ...
            ]
        }
    """
    df_future = build_future_rows(request)

    feature_cols = ["day_of_week", "hour_of_day", "is_weekend",
                    "is_public_holiday", "temperature", "humidity", "weather"]
    X = df_future[feature_cols]

    raw_preds = model.predict(X)
    scored = score_and_label(raw_preds)

    predictions = [
        BinPrediction(
            time_bin=df_future["time_bin"].iloc[i].isoformat(),
            crowdedness_score=scored[i][0],
            crowd_label=scored[i][1],
        )
        for i in range(len(scored))
    ]

    return PredictionResponse(location_id=request.location_id, predictions=predictions)

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}
