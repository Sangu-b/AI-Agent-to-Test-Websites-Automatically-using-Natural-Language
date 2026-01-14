"""
Playwright Login Demo - Test Script
Demonstrates automated login testing using Playwright with the Flask test website
"""

import asyncio
import sys
import subprocess
import time
import socket
import os
import signal
from playwright.async_api import async_playwright, expect

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
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    try:
        # Start Flask server as a subprocess
        _server_process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=script_dir,
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


class LoginTestSuite:
    """Test suite for the login functionality"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.test_results = []
    
    async def setup(self, headless: bool = False):
        """Initialize the browser for testing"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        print(" Browser initialized successfully")
    
    async def teardown(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Browser closed successfully")
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"   → {message}")
    
    async def test_page_loads(self):
        """Test 1: Verify the login page loads correctly"""
        test_name = "Login Page Loads"
        try:
            await self.page.goto(self.base_url)
            title = await self.page.title()
            
            # Verify page title
            assert "Login" in title, f"Expected 'Login' in title, got: {title}"
            
            # Verify key elements exist
            username_input = await self.page.query_selector("#username")
            password_input = await self.page.query_selector("#password")
            login_button = await self.page.query_selector("#loginBtn")
            
            assert username_input is not None, "Username input not found"
            assert password_input is not None, "Password input not found"
            assert login_button is not None, "Login button not found"
            
            self.log_result(test_name, True, f"Page title: {title}")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_empty_form_submission(self):
        """Test 2: Verify form validation for empty fields"""
        test_name = "Empty Form Validation"
        try:
            await self.page.goto(self.base_url)
            
            # Clear any existing values
            await self.page.fill("#username", "")
            await self.page.fill("#password", "")
            
            # The HTML5 required attribute should prevent submission
            # Check that the fields have the required attribute
            username_required = await self.page.get_attribute("#username", "required")
            password_required = await self.page.get_attribute("#password", "required")
            
            assert username_required is not None, "Username field should be required"
            assert password_required is not None, "Password field should be required"
            
            self.log_result(test_name, True, "Form fields have required validation")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_invalid_credentials(self):
        """Test 3: Verify login fails with invalid credentials"""
        test_name = "Invalid Credentials Rejected"
        try:
            await self.page.goto(self.base_url)
            
            # Fill in invalid credentials
            await self.page.fill("#username", "wronguser")
            await self.page.fill("#password", "wrongpass")
            
            # Click the login button
            await self.page.click("#loginBtn")
            
            # Wait for the error message to appear
            await self.page.wait_for_selector("#message.error", timeout=5000)
            
            # Verify error message is displayed
            message_element = await self.page.query_selector("#message")
            message_text = await message_element.text_content()
            
            assert "Invalid" in message_text or "invalid" in message_text.lower(), \
                f"Expected error message about invalid credentials, got: {message_text}"
            
            self.log_result(test_name, True, f"Error message: {message_text}")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_valid_login(self):
        """Test 4: Verify login succeeds with valid credentials"""
        test_name = "Valid Login Succeeds"
        try:
            await self.page.goto(self.base_url)
            
            # Fill in valid credentials
            await self.page.fill("#username", "testuser")
            await self.page.fill("#password", "testpass")
            
            # Click the login button
            await self.page.click("#loginBtn")
            
            # Wait for success message
            await self.page.wait_for_selector("#message.success", timeout=5000)
            
            # Verify success message
            message_element = await self.page.query_selector("#message")
            message_text = await message_element.text_content()
            
            assert "successful" in message_text.lower() or "success" in message_text.lower(), \
                f"Expected success message, got: {message_text}"
            
            self.log_result(test_name, True, f"Success message: {message_text}")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_redirect_to_dashboard(self):
        """Test 5: Verify redirect to dashboard after successful login"""
        test_name = "Redirect to Dashboard"
        try:
            await self.page.goto(self.base_url)
            
            # Fill in valid credentials
            await self.page.fill("#username", "testuser")
            await self.page.fill("#password", "testpass")
            
            # Click the login button
            await self.page.click("#loginBtn")
            
            # Wait for navigation to dashboard
            await self.page.wait_for_url("**/dashboard", timeout=5000)
            
            # Verify we're on the dashboard
            current_url = self.page.url
            title = await self.page.title()
            
            assert "dashboard" in current_url.lower(), \
                f"Expected redirect to dashboard, but URL is: {current_url}"
            
            # Verify dashboard content
            welcome_message = await self.page.query_selector("#welcomeMessage")
            assert welcome_message is not None, "Welcome message not found on dashboard"
            
            self.log_result(test_name, True, f"Redirected to: {current_url}")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_dashboard_logout(self):
        """Test 6: Verify logout functionality from dashboard"""
        test_name = "Dashboard Logout"
        try:
            # First, login
            await self.page.goto(self.base_url)
            await self.page.fill("#username", "testuser")
            await self.page.fill("#password", "testpass")
            await self.page.click("#loginBtn")
            
            # Wait for dashboard
            await self.page.wait_for_url("**/dashboard", timeout=5000)
            
            # Click logout button
            await self.page.click(".logout-btn")
            
            # Verify we're back at login page
            await self.page.wait_for_url(f"{self.base_url}/", timeout=5000)
            
            # Verify login form is visible
            login_form = await self.page.query_selector("#loginForm")
            assert login_form is not None, "Login form not found after logout"
            
            self.log_result(test_name, True, "Successfully logged out and returned to login page")
        except AssertionError as e:
            self.log_result(test_name, False, str(e))
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    async def test_screenshot_capture(self):
        """Test 7: Verify screenshot functionality"""
        test_name = "Screenshot Capture"
        try:
            await self.page.goto(self.base_url)
            
            # Take screenshots at different states
            await self.page.screenshot(path="screenshots/01_login_page.png")
            
            # Fill credentials
            await self.page.fill("#username", "testuser")
            await self.page.fill("#password", "testpass")
            await self.page.screenshot(path="screenshots/02_filled_form.png")
            
            # After login
            await self.page.click("#loginBtn")
            await self.page.wait_for_url("**/dashboard", timeout=5000)
            await self.page.screenshot(path="screenshots/03_dashboard.png")
            
            self.log_result(test_name, True, "Screenshots saved to screenshots/ folder")
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = len(self.test_results) - passed
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
        
        print("-" * 60)
        print(f"Total: {len(self.test_results)} | Passed: {passed} | Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results))*100:.1f}%")
        print("=" * 60)
        
        return failed == 0


async def run_all_tests(headless: bool = False):
    """Run all login tests"""
    print("=" * 60)
    print("PLAYWRIGHT LOGIN DEMO - Automated Test Suite")
    print("=" * 60)
    print()
    
    # Ensure Flask server is running
    if not start_flask_server():
        print("❌ Cannot proceed without Flask server. Please run 'python app.py' first.")
        return False
    
    test_suite = LoginTestSuite()
    
    try:
        await test_suite.setup(headless=headless)
        
        print("\n📋 Running Tests...\n")
        
        # Run all tests
        await test_suite.test_page_loads()
        await test_suite.test_empty_form_submission()
        await test_suite.test_invalid_credentials()
        await test_suite.test_valid_login()
        await test_suite.test_redirect_to_dashboard()
        await test_suite.test_dashboard_logout()
        await test_suite.test_screenshot_capture()
        
        # Print summary
        all_passed = test_suite.print_summary()
        
        return all_passed
        
    finally:
        await test_suite.teardown()


async def run_quick_demo():
    """Run a quick demo of the login flow"""
    print("=" * 60)
    print("PLAYWRIGHT LOGIN DEMO - Quick Demo")
    print("=" * 60)
    print()
    
    # Ensure Flask server is running
    if not start_flask_server():
        print("❌ Cannot proceed without Flask server. Please run 'python app.py' first.")
        return
    
    async with async_playwright() as p:
        # Launch browser (visible)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 Navigating to login page...")
        await page.goto("http://localhost:5000")
        await asyncio.sleep(1)
        
        print("📝 Filling in credentials...")
        await page.fill("#username", "testuser")
        await asyncio.sleep(0.5)
        await page.fill("#password", "testpass")
        await asyncio.sleep(0.5)
        
        print("🔐 Clicking login button...")
        await page.click("#loginBtn")
        
        print("⏳ Waiting for dashboard...")
        await page.wait_for_url("**/dashboard", timeout=5000)
        
        print("✅ Successfully logged in!")
        title = await page.title()
        print(f"   Current page: {title}")
        
        # Keep browser open for viewing
        print("\n👀 Browser will stay open for 5 seconds...")
        await asyncio.sleep(5)
        
        await browser.close()
        print("\n Demo completed!")


if __name__ == "__main__":
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)
    
    try:
        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--demo":
                asyncio.run(run_quick_demo())
            elif sys.argv[1] == "--headless":
                asyncio.run(run_all_tests(headless=True))
            else:
                print("Usage: python test_login.py [--demo|--headless]")
                print("  --demo     Run a quick visual demo")
                print("  --headless Run all tests in headless mode")
                print("  (no args)  Run all tests with visible browser")
        else:
            asyncio.run(run_all_tests(headless=False))
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    finally:
        stop_flask_server()
