import mlflow
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Global variable to store the model
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model on startup
    global model
    # Set the tracking URI (defaults to the mlflow_ui service in docker-compose)
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_ui:5000"))

    # The URI for a registered model in Production
    model_name = os.getenv("MLFLOW_MODEL_NAME", "CrowdLevelModel")
    model_uri = f"models:/{model_name}/Production"

    try:
        print(f"Attempting to load model from {model_uri}...")
        model = mlflow.pyfunc.load_model(model_uri)
        print(f"Successfully loaded model: {model_name}")
    except Exception as e:
        print(f"Warning: Could not load model from MLflow: {e}")
        print("The server will start without a model.")

    yield
    # Clean up on shutdown
    if model:
        del model


app = FastAPI(title="Crowd Level Predictor API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the Crowd Level Predictor API"}


@app.post("/predict")
async def predict(data: dict):
    if model is None:
        return {
            "error": "Model not loaded. Ensure MLflow has a model in 'Production' stage."
        }

    try:
        # Perform prediction (expects a dictionary or similar matching model requirements)
        prediction = model.predict(data)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "mlflow_tracking_uri": mlflow.get_tracking_uri(),
    }
