# MakanMap — Crowdedness Level Predictor

> An industry collaboration project with **[Aires Applied Technology](https://airesatech.com)**, a Singapore-based deep-tech startup.

A real-time crowdedness forecasting system that predicts venue crowd levels across 30-minute time bins. Built with a Gradient Boosting ML model, a FastAPI backend, and a React dashboard — fully containerised and deployable via Docker.

---

## Overview

MakanMap helps venues and users plan around crowd density by predicting crowdedness scores (0–1) and labelling them as **Low**, **Medium**, or **High**. The system takes contextual inputs (weather, time, location frequency, public holidays) and forecasts crowd levels for the next N time slots within operating hours (6am–10pm).

Key capabilities:
- Real-time multi-location crowd monitoring
- Selectable time windows: **30 minutes**, **1 hour**, or **3 hours**
- Forward-looking crowd outlook (up to 12 × 30-min bins)
- Scenario analysis — compare "what-if" conditions against the baseline
- Peak crowd time and trend direction insights
- Automated data pipeline via Apache Airflow

---

## Architecture

```
Raw Event Data
     │
     ▼
Airflow DAG ──► Step 1: Data Cleaning
                         │
                         ▼
                Step 2: Feature Engineering (build_features.py)
                         │
                         ▼
                    Supabase (PostgreSQL)
                         │
                         ▼
              ML Training (Gradient Boosting Regressor)
                    ┌────┴────┐
                    │  Model  │  (.pkl — tracked with MLflow)
                    └────┬────┘
                         │
                    FastAPI Backend  ◄── /predict  /health
                         │
                    React Frontend
                  (Dashboard + Charts)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | Gradient Boosting Regressor (scikit-learn), XGBoost |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | React 19, Vite, Recharts, Chart.js |
| Data Pipeline | Apache Airflow |
| ML Tracking | MLflow |
| Database | Supabase (PostgreSQL) |
| Containerisation | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## Project Structure

```
Crowd-Level-Predictor-DSA-Industry-Project-/
├── backend/
│   ├── src/
│   │   ├── predict_api.py          # Main FastAPI app & /predict endpoint
│   │   └── another_backend_api.py  # Secondary API routes
│   └── tests/
│       └── test_backend.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # Main dashboard with scenario analysis
│   │   │   ├── ControlCard.jsx     # Location & time window selector
│   │   │   ├── TrendChart.jsx      # Recharts line chart
│   │   │   ├── TrendCard.jsx
│   │   │   ├── ContextBadges.jsx   # Contextual metadata display
│   │   │   └── TimeWindowSelector.jsx
│   │   ├── services/
│   │   │   └── predictService.js   # API calls to backend
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── ml/
│   ├── ml pipeline_crowdscore_regression.ipynb
│   ├── ml pipeline testing.ipynb
│   └── models/
│       └── Gradient_Boosting_Regressor.pkl
├── data-pipeline/
│   ├── scripts/
│   │   ├── clean_data.py
│   │   ├── build_features.py
│   │   ├── data_cleaning_script.ipynb
│   │   └── anomaly_features.ipynb
│   └── data/
│       ├── event_level_data_dirty.csv
│       ├── event_level_data_clean.csv
│       └── restored_clean_data.csv
├── airflow/
│   └── dags/
│       └── data_cleaning_dag.py    # Airflow DAG: clean → feature engineer
├── EDA/
│   └── EDA_Crowd_Prediction.ipynb
├── Documentation and Slides/
│   ├── MakanMap_Technical_Report.pdf
│   └── MakanMap_Presentation.pdf
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## API Reference

### `POST /predict`

Returns crowdedness predictions for the next N 30-minute bins within operating hours.

**Request body:**
```json
{
  "location_id": "13",
  "location_freq": 10213,
  "temperature": 29.5,
  "humidity": 78.0,
  "weather": "cloudy",
  "is_public_holiday": 0,
  "bins_ahead": 6
}
```

| Field | Type | Description |
|---|---|---|
| `location_id` | string | Venue identifier |
| `location_freq` | int | Historical visit frequency for that location |
| `temperature` | float | Degrees Celsius (-20 to 40) |
| `humidity` | float | Percentage (0–100) |
| `weather` | string | `clear`, `cloudy`, `night_clear`, or `rainy` |
| `is_public_holiday` | int | `0` or `1` |
| `bins_ahead` | int | Number of 30-min bins to forecast (1–12, default 6) |

**Response:**
```json
{
  "location_id": "13",
  "predictions": [
    {
      "time_bin": "2026-03-13T14:00:00",
      "time_block": "Afternoon",
      "day_name": "Friday",
      "crowdedness_score": 0.52,
      "crowd_label": "Medium"
    }
  ]
}
```

### `GET /health`
Returns model load status.

---

## Crowdedness Score Logic

The raw model output is post-processed into a 0–1 score with adjustments:

| Adjustment | Value |
|---|---|
| Base model output (×3 scale) | Variable |
| Location frequency boost | `location_freq / 20000` |
| Afternoon bonus | +0.10 |
| Weekend bonus | +0.15 |

**Labels:**
- `Low` — score < 0.33
- `Medium` — 0.33 ≤ score < 0.66
- `High` — score ≥ 0.66

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.13+
- Node.js 18+

### 1. Clone the repository
```bash
git clone https://github.com/kiefer-sulijanto/Crowd-Level-Predictor-DSA-Industry-Project-.git
cd Crowd-Level-Predictor-DSA-Industry-Project-
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_KEY, MLFLOW_TRACKING_URI
```

### 3. Run with Docker Compose
```bash
docker compose up --build
```

This starts four services:

| Service | Port | Description |
|---|---|---|
| Backend API | `8000` | FastAPI prediction server |
| Frontend | `5173` | React dashboard |
| MLflow UI | `5000` | ML experiment tracking |
| Airflow | `8080` | Pipeline scheduler |

### 4. Run locally (without Docker)

**Backend:**
```bash
pip install -r requirements.txt
MODEL_PATH=ml/models/Gradient_Boosting_Regressor.pkl uvicorn backend.src.predict_api:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Data Pipeline (Airflow)

The Airflow DAG `crowd_level_predictor_pipeline` runs two sequential tasks:

1. **`step_1_clean_raw_data`** — Fixes unit mismatches, special characters, and nulls in raw event data
2. **`step_2_build_ml_features`** — Engineers cyclical time features, holiday flags, and location metadata; writes to Supabase `features` table

Trigger the DAG manually via the Airflow UI at `localhost:8080` or via CLI:
```bash
airflow dags trigger crowd_level_predictor_pipeline
```

---

## ML Model

- **Algorithm:** Gradient Boosting Regressor (scikit-learn)
- **Input features:** `temperature`, `humidity`, `is_weekend`, `is_public_holiday`, `location_freq`, `weather`, `location_id`, `time_block`, `day_name`
- **Target:** Continuous crowdedness score (regression)
- **Serialised model:** `ml/models/Gradient_Boosting_Regressor.pkl`
- **Experiment tracking:** MLflow

---

## CI/CD

GitHub Actions pipeline on push/PR to `main`:

1. **Lint** — `flake8` for syntax errors and undefined names
2. **Test** — `pytest backend/tests/`
3. **Docker Build** — validates the image builds cleanly

---

## Scenario Analysis

The dashboard supports "what-if" analysis. Users can manually override input features to simulate different conditions and compare the result against the baseline prediction:

```
day_of_week=2
hour_of_day=14
is_weekend=0
is_public_holiday=1
temperature=24.8
humidity=93.5
weather=rainy
```

The scenario chart shows baseline vs. scenario side by side with a delta impact score.

---

## Acknowledgements

Built as part of the **DSA Academy Industry Project** in collaboration with **Aires Applied Technology**, Singapore.
