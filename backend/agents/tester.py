
from pathlib import Path
from playwright.async_api import async_playwright


class BrowserTester:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.runner = self

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        Path("screenshots").mkdir(exist_ok=True)

    async def navigate_to(self, url):
        await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )
        print(f"Navigated to: {self.page.url}")

    async def execute_action(self, action, target, value=None):
        try:
            locator = self.page.locator(target).first

            if action == "click":
                await locator.click(timeout=10000)
            elif action == "fill":
                await locator.fill(value or "", timeout=10000)
            else:
                return False

            return True

        except Exception as exc:
            print(f"Action failed ({action}, {target}): {exc}")
            return False

    async def verify_assertion(self, assertion, expected):
        try:
            if assertion == "url_contains":
                return expected in self.page.url

            if assertion == "text_visible":
                page_text = await self.page.locator("body").inner_text()
                print("PAGE TEXT:", repr(page_text))
                print("EXPECTED TEXT:", repr(expected))
                return expected.lower() in page_text.lower()

            return False

        except Exception as exc:
            print(f"Verification failed: {exc}")
            return False

    async def capture_screenshot(self, name):
        screenshot_path = Path("screenshots") / f"{name}.png"
        await self.page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    async def close(self):
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
