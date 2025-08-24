from playwright.sync_api import sync_playwright

def capture_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            # Login
            page.goto("http://localhost:5173")
            page.wait_for_timeout(2000)
            
            # Fill login form
            page.fill('input[type="text"]', 'admin')
            page.fill('input[type="password"]', 'password')
            page.click('button[type="submit"]')
            
            # Wait for dashboard
            page.wait_for_timeout(5000)
            
            # Take screenshot
            page.screenshot(path="screenshot_dashboard_complete.png", full_page=True)
            print("Dashboard screenshot saved as screenshot_dashboard_complete.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    capture_dashboard()