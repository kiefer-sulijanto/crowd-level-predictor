from fastapi import FastAPI
import mlflow.pyfunc
import pandas as pd
import os

app = FastAPI()

# Load model from MLflow Registry
model_name = "crowd_predictor"  # add actual name
model_version = "production"  # add actual version
model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")


@app.post("/predict")
async def predict(data: dict):
    # Convert incoming JSON to DataFrame for the model
    df = pd.DataFrame([data])
    prediction = model.predict(df)
    return {"crowd_level_score": float(prediction[0])}
