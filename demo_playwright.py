"""
Playwright Login Demo - Simple Script
A simple standalone script demonstrating Playwright browser automation for login testing
This script works without OpenAI API - just pure Playwright automation
"""

import asyncio
import subprocess
import sys
import time
import socket
import os
import signal
from playwright.async_api import async_playwright

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


async def demo_login_flow():
    """Demonstrate the complete login flow using Playwright"""
    
    print("=" * 60)
    print("PLAYWRIGHT LOGIN DEMO")
    print("=" * 60)
    print()
    
    # Ensure Flask server is running
    if not start_flask_server():
        print("❌ Cannot proceed without Flask server. Please run 'python app.py' first.")
        return
    
    async with async_playwright() as p:
        # Launch browser (visible mode for demo)
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to login page
            print("\nStep 1: Navigating to login page...")
            await page.goto("http://localhost:5000")
            await asyncio.sleep(1)
            
            title = await page.title()
            print(f"   ✓ Page loaded: {title}")
            
            # Step 2: Verify login form elements exist
            print("\n Step 2: Verifying form elements...")
            
            username_input = await page.query_selector("#username")
            password_input = await page.query_selector("#password")
            login_button = await page.query_selector("#loginBtn")
            
            print(f"   ✓ Username field: {'Found' if username_input else 'Not found'}")
            print(f"   ✓ Password field: {'Found' if password_input else 'Not found'}")
            print(f"   ✓ Login button: {'Found' if login_button else 'Not found'}")
            
            # Step 3: Test invalid login
            print("\n Step 3: Testing invalid credentials...")
            await page.fill("#username", "wronguser")
            await page.fill("#password", "wrongpass")
            await asyncio.sleep(0.5)
            
            await page.click("#loginBtn")
            await asyncio.sleep(1)
            
            # Check for error message
            error_visible = await page.is_visible("#message.error")
            if error_visible:
                error_text = await page.text_content("#message")
                print(f"   ✓ Error message displayed: {error_text}")
            
            # Step 4: Clear and test valid login
            print("\n Step 4: Testing valid credentials...")
            await page.fill("#username", "")
            await page.fill("#password", "")
            await asyncio.sleep(0.3)
            
            await page.fill("#username", "testuser")
            await asyncio.sleep(0.3)
            await page.fill("#password", "testpass")
            await asyncio.sleep(0.3)
            
            print("   ✓ Credentials entered: testuser / testpass")
            
            # Step 5: Submit login
            print("\n Step 5: Clicking login button...")
            await page.click("#loginBtn")
            
            # Wait for success message
            await page.wait_for_selector("#message.success", timeout=5000)
            success_text = await page.text_content("#message")
            print(f"   ✓ Success message: {success_text}")
            
            # Step 6: Wait for redirect to dashboard
            print("\n Step 6: Waiting for dashboard redirect...")
            await page.wait_for_url("**/dashboard", timeout=5000)
            
            dashboard_title = await page.title()
            current_url = page.url
            print(f"   ✓ Redirected to: {current_url}")
            print(f"   ✓ Page title: {dashboard_title}")
            
            # Step 7: Verify dashboard content
            print("\n Step 7: Verifying dashboard content...")
            
            welcome_message = await page.query_selector("#welcomeMessage")
            if welcome_message:
                welcome_text = await welcome_message.text_content()
                print(f"   ✓ Welcome message: {welcome_text}")
            
            # Get stats
            stat_cards = await page.query_selector_all(".stat-card h3")
            print("   ✓ Dashboard statistics found:")
            for i, card in enumerate(stat_cards):
                stat_value = await card.text_content()
                print(f"      - Stat {i+1}: {stat_value}")
            
            # Step 8: Take a screenshot
            print("\n Step 8: Taking screenshot...")
            await page.screenshot(path="demo_screenshot.png")
            print("   ✓ Screenshot saved as 'demo_screenshot.png'")
            
            # Step 9: Test logout
            print("\n Step 9: Testing logout...")
            logout_btn = await page.query_selector(".logout-btn")
            if logout_btn:
                await logout_btn.click()
                await page.wait_for_url("**/", timeout=5000)
                print("   ✓ Successfully logged out")
                print(f"   ✓ Returned to: {page.url}")
            
            print("\n" + "=" * 60)
            print(" DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            # Keep browser open briefly to see results
            print("\n Keeping browser open for 3 seconds...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n Error during demo: {str(e)}")
            raise
        finally:
            await browser.close()
            print("\n Browser closed.")


async def quick_login_test():
    """Quick automated login test - headless mode"""
    
    print("Running quick login test (headless)...")
    
    # Ensure Flask server is running
    if not start_flask_server():
        print(" Cannot proceed without Flask server. Please run 'python app.py' first.")
        return False
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate and login
            await page.goto("http://localhost:5000")
            await page.fill("#username", "testuser")
            await page.fill("#password", "testpass")
            await page.click("#loginBtn")
            
            # Wait for redirect
            await page.wait_for_url("**/dashboard", timeout=5000)
            
            # Verify we're on dashboard
            title = await page.title()
            assert "Dashboard" in title, f"Expected Dashboard, got {title}"
            
            print(" Quick login test PASSED!")
            return True
            
        except Exception as e:
            print(f" Quick login test FAILED: {str(e)}")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            asyncio.run(quick_login_test())
        else:
            asyncio.run(demo_login_flow())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    finally:
        stop_flask_server()
