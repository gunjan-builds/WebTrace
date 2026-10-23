import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.agents.tester import BrowserTester
from backend.schemas import TestRequest, TestCreated, TestReport
from backend.orchestrator import create_test_run
from backend.url_validator import validate_url

app = FastAPI(title="AI QA Browser Tester & WebTrace API", version="1.0")

# Temporary in-memory storage for test runs
runs = {}

def run_tester_sync(url: str):
    """Playwright ko clean synchronous/event-loop isolated environment mein chalane ke liye"""
    url_str = str(url)  # URL ko ensure karo ki wo plain string ho
    async def _run():
        tester = BrowserTester()
        await tester.start()
        await tester.navigate_to(url_str)
        await tester.runner.capture_screenshot("api_step1_home")
        
        passed = await tester.verify_assertion("text_visible", "Example Domain")
        await tester.execute_action("click", "a")
        await tester.runner.capture_screenshot("api_step2_clicked")
        
        url_matched = await tester.verify_assertion("url_contains", "iana.org")
        await tester.close()
        return passed and url_matched

    return asyncio.run(_run())


@app.get("/")
def home():
    return {"message": "Browser Tester & WebTrace API is running successfully! 🚀"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "WebTrace backend",
    }


@app.post("/run-browser-test")
async def run_browser_test(request: TestRequest):
    try:
        # Request.url ko string mein convert karke pass karo
        url_str = str(request.url)
        result = await asyncio.to_thread(run_tester_sync, url_str)
        
        return {
            "status": "success",
            "message": "Test executed successfully via API!",
            "target_url": url_str,
            "assertions_passed": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tests", response_model=TestCreated)
async def create_test(request: TestRequest):
    try:
        validate_url(str(request.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    # Non-blocking execution call
    result = await create_test_run(request) if asyncio.iscoroutinefunction(create_test_run) else create_test_run(request)
    runs[result["run_id"]] = result

    return TestCreated(
        run_id=result["run_id"],
        status=result["status"],
        message="Test plan generated and executed in background.",
    )


@app.get("/api/tests/{run_id}")
def get_test(run_id: str):
    result = runs.get(run_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    return {
        "run_id": result["run_id"],
        "status": result["status"],
        "plan": result.get("plan"),
    }


@app.get("/api/tests/{run_id}/report")
def get_test_report(run_id: str):
    result = runs.get(run_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    return result.get("report")


@app.get("/api/report/json")
def get_json_report():
    report_path = "reports/test_report.json"
    if not os.path.exists(report_path):
        report_path = "backend/reports/test_report.json"
        
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type="application/json")
    return {"error": "Report not found. Please run tests first!"}


@app.get("/api/report/summary")
def get_markdown_report():
    summary_path = "reports/SUMMARY.md"
    if not os.path.exists(summary_path):
        summary_path = "backend/reports/SUMMARY.md"
        
    if os.path.exists(summary_path):
        return FileResponse(summary_path, media_type="text/markdown")
    return {"error": "Summary not found."}