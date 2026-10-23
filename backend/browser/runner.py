
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
