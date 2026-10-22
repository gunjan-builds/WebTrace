import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.agents.tester import BrowserTester

app = FastAPI(title="AI QA Browser Tester API", version="1.0")

class TestRequest(BaseModel):
    url: str = "https://example.com"

def run_tester_sync(url: str):
    """Playwright ko clean synchronous/event-loop isolated environment mein chalane ke liye"""
    async def _run():
        tester = BrowserTester()
        await tester.start()
        await tester.navigate_to(url)
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
    return {"message": "Browser Tester API is running successfully! 🚀"}

@app.post("/run-browser-test")
async def run_browser_test(request: TestRequest):
    try:
        # Isse Playwright FastAPI ke event loop ko block nahi karega
        result = await asyncio.to_thread(run_tester_sync, request.url)
        
        return {
            "status": "success",
            "message": "Test executed successfully via API!",
            "target_url": request.url,
            "assertions_passed": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))