import asyncio
from backend.browser.runner import BrowserRunner

class BrowserTester:
    def __init__(self):
        # Runner instance ko import karke use kar rahe hain
        self.runner = BrowserRunner()
        self.page = None

    async def start(self):
        """Tester agent initialization"""
        self.page = await self.runner.start_browser(headless=False)

    async def navigate_to(self, url: str):
        """Kisi bhi URL par navigate karne ke liye"""
        if not self.page:
            await self.start()
        print(f"🌐 Navigating to: {url}")
        await self.page.goto(url)
        title = await self.page.title()
        print(f"📄 Page Title: {title}")

    async def execute_action(self, action_type: str, selector: str, value: str = None):
        """Page ke elements par actions perform karna (click, type, etc.)"""
        try:
            print(f"⚡ Executing [{action_type}] on selector: '{selector}'")
            element = self.page.locator(selector).first
            await element.wait_for(state="visible", timeout=5000)

            if action_type == "click":
                await element.click()
            elif action_type == "type" or action_type == "fill":
                await element.fill(value or "")
            elif action_type == "scroll":
                await element.scroll_into_view_if_needed()
            else:
                print(f"❌ Unknown action type: {action_type}")
                return False

            print(f"✅ Action [{action_type}] successfully ho gaya!")
            return True

        except Exception as e:
            print(f"⚠️ Action failed: {str(e)}. Triggering Controlled Recovery...")
            return await self.controlled_recovery(action_type, selector)

    async def verify_assertion(self, assertion_type: str, expected_value: str, selector: str = None):
        """Expected outcomes verify karne ke liye"""
        try:
            passed = False
            if assertion_type == "text_visible":
                content = await self.page.content()
                passed = expected_value in content
            elif assertion_type == "url_contains":
                passed = expected_value in self.page.url
            elif assertion_type == "element_visible" and selector:
                passed = await self.page.locator(selector).first.is_visible()

            if passed:
                print(f"✔️ Assertion Passed: [{assertion_type}] -> '{expected_value}'")
            else:
                print(f"❌ Assertion Failed: [{assertion_type}] -> '{expected_value}' not found")
            
            return passed
        except Exception as e:
            print(f"⚠️ Assertion error: {str(e)}")
            return False

    async def controlled_recovery(self, action_type: str, selector: str) -> bool:
        """Fail hone par recovery mechanism"""
        try:
            print("🔄 Recovery mode active: Waiting and retrying with force...")
            await asyncio.sleep(2)
            element = self.page.locator(selector).first
            if action_type == "click":
                await element.click(force=True)
                print("✨ Recovery Successful via Force Click!")
                return True
        except Exception as rec_error:
            print(f"❌ Recovery Failed: {str(rec_error)}")

        await self.runner.capture_screenshot(f"FAIL_{action_type}")
        return False

    async def close(self):
        """Browser session close karna"""
        await self.runner.close_browser()

# Test flow
if __name__ == "__main__":
    async def run_test():
        tester = BrowserTester()
        await tester.start()
        
        await tester.navigate_to("https://example.com")
        
        # Screenshot capture (error fixed here)
        await tester.runner.capture_screenshot("step1_home_page")
        
        await tester.verify_assertion("text_visible", "Example Domain")
        await tester.execute_action("click", "a")
        
        await tester.runner.capture_screenshot("step2_after_click")
        await tester.verify_assertion("url_contains", "iana.org")
        
        await asyncio.sleep(2)
        await tester.close()

    asyncio.run(run_test())