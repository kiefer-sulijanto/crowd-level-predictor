# Imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
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
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
except FileNotFoundError:
    raise RuntimeError(f"Model file not found at '{MODEL_PATH}'. Train and save the model first.")

# ── Constants ──────────────────────────────────────────────────────────────
VALID_WEATHER = {"rainy", "cloudy", "night_clear", "clear"}

DAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
}

def get_time_block(hour: int) -> str:
    """
    6–11   → Morning
    12–16  → Afternoon
    17–18  → Evening
    19–22  → Night
    """
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 16:
        return "Afternoon"
    elif 17 <= hour <= 18:
        return "Evening"
    elif 19 <= hour <= 22:
        return "Night"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Hour {hour} is outside operating hours (6am–10pm)."
        )

class PredictionRequest(BaseModel):
    location_id: str
    location_freq: int = Field(..., ge=0)

    # VALIDATION
    temperature: float = Field(..., ge=-20, le=40)
    humidity: float = Field(..., ge=0, le=100)

    weather: Literal["clear", "cloudy", "night_clear", "rainy"]

    is_public_holiday: int = Field(0, ge=0, le=1)

    # LIMITATION FOR EVERY FEATURES (buat manual input override)
    day_of_week: int | None = Field(None, ge=0, le=6)
    hour_of_day: int | None = Field(None, ge=0, le=23)
    is_weekend: int | None = Field(None, ge=0, le=1)

    bins_ahead: int = Field(6, ge=1, le=12)

class BinPrediction(BaseModel):
    time_bin: str            # ISO timestamp
    time_block: str          # Morning / Afternoon / Evening / Night
    day_name: str            # Monday … Sunday
    crowdedness_score: float # 0.0 – 1.0
    crowd_label: str         # Low / Medium / High

class PredictionResponse(BaseModel):
    location_id: str
    predictions: list[BinPrediction]

# ── Helper: build feature rows for future time bins ────────────────────────
def build_future_rows(request: PredictionRequest) -> pd.DataFrame:
    """
    Construct one feature row per 30-min bin starting from now.
    Time-derived features (day_name, time_block, is_weekend) are
    calculated from the actual future timestamp.
    Weather/temp/humidity/location_freq are carried forward from the request.
    """

    now = datetime.now().replace(second=0, microsecond=0)
    # Round up to next 30-min boundary
    minutes = (now.minute // 30 + 1) * 30
    start = now.replace(minute=0) + timedelta(minutes=minutes)

    rows = []
    for i in range(request.bins_ahead):
        ts   = start + timedelta(minutes=30 * i)
        hour = ts.hour
        dow  = ts.weekday()

        # Skip bins outside operating hours
        if not (6 <= hour <= 22):
            continue

        rows.append({
            "time_bin":          ts,
            # Numeric
            "temperature":       request.temperature,
            "humidity":          request.humidity,
            "is_weekend":        int(dow >= 5),
            "is_public_holiday": request.is_public_holiday,
            "location_freq":     request.location_freq,
            # Categorical
            "weather":           request.weather,
            "location_id":       request.location_id,
            "time_block":        get_time_block(hour),
            "day_name":          DAY_NAMES[dow],
        })

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="All forecast bins fall outside operating hours (6am–10pm). Try again later."
        )

    return pd.DataFrame(rows)

# ── Helper: map model output to 0–1 score + label ─────────────────────────
def score_and_label(predictions, df_future):
    results = []

    for i, pred in enumerate(predictions):
        row = df_future.iloc[i]

        score = float(pred) * 3

        score += row["location_freq"] / 20000 
        score += 0.1 if row["time_block"] == "Afternoon" else 0
        score += 0.15 if row["is_weekend"] else 0

        score = max(0, min(score, 1))

        if score < 0.33:
            label = "Low"
        elif score < 0.66:
            label = "Medium"
        else:
            label = "High"

        results.append((round(score, 2), label))

    return results

# ── Endpoint ───────────────────────────────────────────────────────────────
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Returns crowdedness predictions for the next N 30-minute bins
    within operating hours (6am–10pm).

    Example request:
        {
            "location_id": "13",
            "location_freq": 10213,
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
                {
                    "time_bin": "2026-03-13T14:00:00",
                    "time_block": "Afternoon",
                    "day_name": "Friday",
                    "crowdedness_score": 0.5,
                    "crowd_label": "Medium"
                },
                ...
            ]
        }
    """
    df_future = build_future_rows(request)

    # Must match exact column order the model was trained on
    num_cols = ["temperature", "humidity", "is_weekend", "is_public_holiday", "location_freq"]
    cat_cols = ["weather", "location_id", "time_block", "day_name"]
    X = df_future[num_cols + cat_cols]

    raw_preds = model.predict(X)
    scored    = score_and_label(raw_preds, df_future)

    predictions = [
        BinPrediction(
            time_bin =         df_future["time_bin"].iloc[i].isoformat(),
            time_block =       df_future["time_block"].iloc[i],
            day_name =         df_future["day_name"].iloc[i],
            crowdedness_score=scored[i][0],
            crowd_label =      scored[i][1],
        )
        for i in range(len(scored))
    ]

    return PredictionResponse(location_id=request.location_id, predictions=predictions)

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}
