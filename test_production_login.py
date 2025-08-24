from playwright.sync_api import sync_playwright
import time

def test_production_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # コンソールログをキャプチャ
        page.on("console", lambda msg: print(f"Console [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"Page error: {exc}"))
        
        # ネットワークレスポンスをキャプチャ
        def handle_response(response):
            if 'api' in response.url:
                print(f"API Response: {response.url} -> {response.status}")
        
        page.on("response", handle_response)
        
        try:
            print("本番環境にアクセス中...")
            page.goto("http://localhost:3000")
            
            # ページロード待機
            page.wait_for_timeout(3000)
            
            print("\n現在のURL:", page.url)
            
            # ログインフォームの確認
            if page.is_visible('input[type="text"]'):
                print("ログインフォームが表示されています")
                
                # 認証情報を入力
                print("認証情報を入力中...")
                page.fill('input[type="text"]', 'admin')
                page.fill('input[type="password"]', 'password')
                
                # ログインボタンをクリック
                print("ログインボタンをクリック...")
                page.click('button[type="submit"]')
                
                # レスポンス待機
                page.wait_for_timeout(3000)
                
                # 最終URL確認
                final_url = page.url
                print(f"\n最終URL: {final_url}")
                
                # エラーメッセージの確認
                if page.is_visible('.MuiAlert-message'):
                    error_element = page.query_selector('.MuiAlert-message')
                    if error_element:
                        print(f"エラーメッセージ: {error_element.text_content()}")
                
                # スクリーンショット保存
                page.screenshot(path="production_login_result.png")
                print("スクリーンショットを保存しました: production_login_result.png")
                
        finally:
            browser.close()

if __name__ == "__main__":
    test_production_login()