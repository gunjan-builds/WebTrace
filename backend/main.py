
from fastapi import FastAPI

app = FastAPI(title="WebTrace API")


@app.get("/")
def home():
    return {"message": "Welcome to WebTrace"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "WebTrace backend"
    }
