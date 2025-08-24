from playwright.sync_api import sync_playwright
import time

def test_login_with_console():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging
        page = browser.new_page()
        
        # Log console messages
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"Page error: {exc}"))
        
        try:
            print("Opening application...")
            page.goto("http://localhost:5173")
            
            # Wait for page to load
            page.wait_for_timeout(2000)
            
            print("Current URL:", page.url)
            
            # Check if on login page
            if page.is_visible('input[type="text"]'):
                print("Login form found, filling credentials...")
                
                # Fill credentials
                page.fill('input[type="text"]', 'admin')
                page.fill('input[type="password"]', 'password')
                
                # Open devtools network tab to see API calls
                print("Clicking login button...")
                
                # Click login and wait
                page.click('button[type="submit"]')
                
                # Wait longer for navigation
                page.wait_for_timeout(5000)
                
                # Check final URL
                final_url = page.url
                print(f"Final URL: {final_url}")
                
                # Check page content
                if "/dashboard" in final_url:
                    print("✅ Successfully navigated to dashboard!")
                elif page.is_visible('input[type="text"]'):
                    print("❌ Still on login page")
                    # Check for error messages
                    error_elements = page.query_selector_all('.MuiAlert-message')
                    for elem in error_elements:
                        print(f"Error message: {elem.text_content()}")
                else:
                    print("⚠️ Unknown state")
                    
            # Keep browser open for manual inspection
            print("\nBrowser will close in 10 seconds... Press Ctrl+C to keep it open")
            time.sleep(10)
                
        except KeyboardInterrupt:
            print("\nKeeping browser open...")
            input("Press Enter to close...")
        finally:
            browser.close()

if __name__ == "__main__":
    test_login_with_console()