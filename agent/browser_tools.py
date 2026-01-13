"""
Playwright Browser Tools
Browser automation utilities for the AI testing agent
"""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class BrowserManager:
    """Manages browser instances and provides automation utilities"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def initialize(self, headless: bool = False):
        """Initialize the browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self
    
    async def close(self):
        """Close the browser and cleanup resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        await self.page.goto(url)
        return {
            "action": "navigate",
            "url": url,
            "success": True,
            "title": await self.page.title()
        }
    
    async def click(self, selector: str) -> Dict[str, Any]:
        """Click on an element"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        await self.page.click(selector)
        return {
            "action": "click",
            "selector": selector,
            "success": True
        }
    
    async def fill(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill in a form field"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        await self.page.fill(selector, value)
        return {
            "action": "fill",
            "selector": selector,
            "value": value,
            "success": True
        }
    
    async def get_text(self, selector: str) -> str:
        """Get text content of an element"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content()
        return ""
    
    async def verify_element_exists(self, selector: str) -> Dict[str, Any]:
        """Verify if an element exists on the page"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        element = await self.page.query_selector(selector)
        return {
            "action": "verify",
            "selector": selector,
            "exists": element is not None,
            "success": True
        }
    
    async def verify_text_content(self, selector: str, expected_text: str) -> Dict[str, Any]:
        """Verify if an element contains expected text"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        actual_text = await self.get_text(selector)
        contains_text = expected_text.lower() in actual_text.lower() if actual_text else False
        
        return {
            "action": "verify_text",
            "selector": selector,
            "expected": expected_text,
            "actual": actual_text,
            "match": contains_text,
            "success": True
        }
    
    async def screenshot(self, path: str = "screenshot.png") -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        await self.page.screenshot(path=path)
        return {
            "action": "screenshot",
            "path": path,
            "success": True
        }
    
    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """Wait for an element to appear"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return {
                "action": "wait",
                "selector": selector,
                "success": True
            }
        except Exception as e:
            return {
                "action": "wait",
                "selector": selector,
                "success": False,
                "error": str(e)
            }
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }


# Helper function to run async browser operations
def run_browser_action(coro):
    """Run an async browser action synchronously"""
    return asyncio.get_event_loop().run_until_complete(coro)


# Example usage and testing
async def test_browser_tools():
    """Test the browser tools with the local Flask server"""
    print("Testing Browser Tools...")
    
    manager = BrowserManager()
    await manager.initialize(headless=False)
    
    try:
        # Navigate to the login page
        result = await manager.navigate("http://localhost:5000")
        print(f"Navigate: {result}")
        
        # Fill in the login form
        await manager.fill("#username", "testuser")
        await manager.fill("#password", "testpass")
        print("Filled login form")
        
        # Click the login button
        await manager.click("#loginBtn")
        print("Clicked login button")
        
        # Wait a moment for the response
        await asyncio.sleep(2)
        
        # Get page info
        info = await manager.get_page_info()
        print(f"Current page: {info}")
        
        # Take a screenshot
        await manager.screenshot("test_screenshot.png")
        print("Screenshot saved")
        
    finally:
        await manager.close()
        print("Browser closed")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_browser_tools())
