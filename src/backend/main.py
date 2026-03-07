from fastapi import FastAPI

app = FastAPI(title="Crowd Level Predictor API")


@app.get("/")
async def root():
    return {"message": "Welcome to the Crowd Level Predictor API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
