<<<<<<< HEAD
import os
from playwright.async_api import async_playwright
from backend.agents.visual_auditor import VisualAuditor
from backend.agents.screenshot_highlighter import highlight_screenshot
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
            # --- Akanksha ka Visual Auditor Integration ---
            try:
                auditor = VisualAuditor()
                issues = await auditor.audit_page(self.page)
                if issues:
                    highlight_screenshot(file_path, issues)
                    print(f"🔍 Visual Auditor: {len(issues)} issues detected and highlighted!")
            except Exception as e:
                print(f"⚠️ Visual Auditor warning: {e}")
            # ---------------------------------------------
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
=======

from pathlib import Path
from playwright.async_api import async_playwright


class BrowserRunner:
    async def run(self, plan):
        results = []
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                for index, step in enumerate(plan.steps, start=1):
                    action = step.action
                    target = step.target
                    expected = step.expected
                    value = getattr(step, "value", None)

                    try:
                        if action == "navigate":
                            await page.goto(target, wait_until="domcontentloaded")
                            message = f"Opened {page.url}"

                        elif action == "click":
                            await page.locator(target).first.click(timeout=10000)
                            message = f"Clicked {target}"

                        elif action == "fill":
                            await page.locator(target).first.fill(
                                value or "", timeout=10000
                            )
                            message = f"Filled {target}"

                        elif action == "verify":
                            if target == "text":
                                found = await page.get_by_text(
                                    expected, exact=False
                                ).count() > 0
                                if not found:
                                    raise AssertionError(
                                        f"Text not found: {expected}"
                                    )
                                message = f"Text found: {expected}"

                            elif target == "url":
                                if expected not in page.url:
                                    raise AssertionError(
                                        f"Expected URL to contain {expected}; "
                                        f"actual URL: {page.url}"
                                    )
                                message = f"URL verified: {page.url}"

                            else:
                                raise ValueError(
                                    f"Unsupported verification target: {target}"
                                )
                        else:
                            raise ValueError(f"Unsupported action: {action}")

                        status = "passed"

                    except Exception as exc:
                        status = "failed"
                        message = str(exc)

                    screenshot_path = screenshot_dir / f"step_{index}.png"
                    try:
                        await page.screenshot(path=str(screenshot_path))
                    except Exception:
                        pass

                    results.append({
                        "name": f"Step {index}: {action}",
                        "status": status,
                        "message": message,
                    })

            finally:
                await browser.close()

        return results
>>>>>>> origin/orchestrator-ai
