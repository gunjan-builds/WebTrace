
from fastapi import FastAPI, HTTPException

from .schemas import TestRequest, TestCreated
from .orchestrator import create_test_run

app = FastAPI(title="WebTrace API")

# Temporary in-memory storage for test runs
runs = {}


@app.get("/")
def home():
    return {"message": "Welcome to WebTrace"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "WebTrace backend",
    }


@app.post("/api/tests", response_model=TestCreated)
def create_test(request: TestRequest):
    result = create_test_run(request)

    runs[result["run_id"]] = result

    return TestCreated(
        run_id=result["run_id"],
        status=result["status"],
        message="Test plan generated. Browser execution is not connected yet.",
    )


@app.get("/api/tests/{run_id}")
def get_test(run_id: str):
    result = runs.get(run_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    return {
        "run_id": result["run_id"],
        "status": result["status"],
        "plan": result["plan"],
    }


@app.get("/api/tests/{run_id}/report")
def get_test_report(run_id: str):
    result = runs.get(run_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    return result["report"]
