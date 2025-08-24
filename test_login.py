from playwright.sync_api import sync_playwright
import time

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Opening application...")
            page.goto("http://localhost:5173")
            
            # Wait for page to load
            page.wait_for_timeout(2000)
            
            # Take screenshot of current state
            page.screenshot(path="screenshot_complete_login.png")
            print("Screenshot saved as screenshot_complete_login.png")
            
            # Try to fill login form if visible
            try:
                # Wait for username field
                page.wait_for_selector('input[type="text"]', timeout=3000)
                
                # Fill credentials
                print("Filling login form...")
                page.fill('input[type="text"]', 'admin')
                page.fill('input[type="password"]', 'password')
                
                # Click login button
                page.click('button[type="submit"]')
                
                # Wait for response
                page.wait_for_timeout(3000)
                
                # Take screenshot after login
                page.screenshot(path="screenshot_complete_dashboard.png")
                print("Screenshot saved as screenshot_complete_dashboard.png")
                
                # Check current URL
                current_url = page.url
                print(f"Current URL: {current_url}")
                
                if "dashboard" in current_url or not page.is_visible('input[type="text"]'):
                    print("✅ Login successful!")
                else:
                    print("⚠️ Still on login page")
                    
            except Exception as e:
                print(f"Could not find login form: {e}")
                # Page might be loading or showing error
                page.screenshot(path="screenshot_error.png")
                print("Error screenshot saved")
                
        finally:
            browser.close()

if __name__ == "__main__":
    test_login()