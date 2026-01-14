"""
Playwright Browser Tools
Browser automation utilities for the AI testing agent
"""

import asyncio
import subprocess
import sys
import time
import socket
import os
import signal
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Global variable to track server process
_server_process = None


def is_port_in_use(port: int = 5000) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('localhost', port))
            return True
        except (ConnectionRefusedError, OSError):
            return False


def start_flask_server():
    """Start the Flask server if not already running"""
    global _server_process
    
    if is_port_in_use(5000):
        print("✅ Flask server already running on port 5000")
        return True
    
    print("🚀 Starting Flask server...")
    
    # Get the directory where the app.py is located
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(agent_dir)
    app_path = os.path.join(project_dir, "app.py")
    
    try:
        # Start Flask server as a subprocess
        _server_process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )
        
        # Wait for server to start
        max_wait = 10  # seconds
        for i in range(max_wait * 2):
            if is_port_in_use(5000):
                print("✅ Flask server started successfully!")
                return True
            time.sleep(0.5)
        
        print("❌ Failed to start Flask server within timeout")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        return False


def stop_flask_server():
    """Stop the Flask server if we started it"""
    global _server_process
    
    if _server_process is not None:
        print("\n🛑 Stopping Flask server...")
        try:
            if sys.platform == 'win32':
                _server_process.terminate()
            else:
                os.kill(_server_process.pid, signal.SIGTERM)
            _server_process.wait(timeout=5)
            print("✅ Flask server stopped")
        except Exception as e:
            print(f"⚠️ Could not stop server gracefully: {e}")
            _server_process.kill()
        _server_process = None


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
    
    # Ensure Flask server is running
    if not start_flask_server():
        print("❌ Cannot proceed without Flask server. Please run 'python app.py' first.")
        return
    
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
    try:
        asyncio.run(test_browser_tools())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    finally:
        stop_flask_server()
