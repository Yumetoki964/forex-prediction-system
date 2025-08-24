from playwright.sync_api import sync_playwright
import json

def test_login_with_network():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture network responses
        responses = []
        def handle_response(response):
            if '/api/auth/login' in response.url:
                responses.append({
                    'url': response.url,
                    'status': response.status,
                    'ok': response.ok
                })
        
        page.on("response", handle_response)
        
        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        
        try:
            print("Opening application...")
            page.goto("http://localhost:5173")
            page.wait_for_timeout(2000)
            
            # Fill and submit login form
            print("Filling login form...")
            page.fill('input[type="text"]', 'admin')
            page.fill('input[type="password"]', 'password')
            
            # Click login
            print("Clicking login button...")
            page.click('button[type="submit"]')
            
            # Wait for network activity
            page.wait_for_timeout(3000)
            
            # Print network responses
            print("\nNetwork responses:")
            for r in responses:
                print(f"  {r['url']}: {r['status']} ({'OK' if r['ok'] else 'FAILED'})")
            
            # Print console logs
            print("\nConsole logs:")
            for log in console_logs[-10:]:  # Last 10 logs
                print(f"  {log}")
            
            # Check final state
            current_url = page.url
            print(f"\nFinal URL: {current_url}")
            
            # Check for error messages
            try:
                error_element = page.query_selector('.MuiAlert-message')
                if error_element:
                    print(f"Error message: {error_element.text_content()}")
            except:
                pass
            
            # Get localStorage to check auth state
            auth_state = page.evaluate("() => localStorage.getItem('auth')")
            if auth_state:
                print(f"Auth state in localStorage: {auth_state}")
                
        finally:
            browser.close()

if __name__ == "__main__":
    test_login_with_network()