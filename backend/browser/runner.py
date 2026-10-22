import os
from playwright.async_api import async_playwright

class BrowserRunner:
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.playwright = None
        self.browser = None
        self.page = None
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def start_browser(self, headless: bool = False):
        """Browser initialize aur launch karne ke liye"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=headless)
            self.page = await self.browser.new_page()
            print("🚀 Browser successfully open ho gaya hai via runner!")
        return self.page

    async def capture_screenshot(self, step_name: str) -> str:
        """Visual Auditor ke liye screenshot capture karna"""
        if self.page:
            file_path = os.path.join(self.screenshot_dir, f"{step_name}.png")
            await self.page.screenshot(path=file_path, full_page=True)
            print(f"📸 Screenshot saved: {file_path}")
            return file_path
        return ""

    async def close_browser(self):
        """Browser session close karne ke liye"""
        if self.browser:
            await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.browser = None
            self.page = None
            print("🛑 Browser close ho gaya via runner.")