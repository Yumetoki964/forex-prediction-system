#!/usr/bin/env python3
"""
完全版Reactアプリケーションの動作確認
"""
import asyncio
from playwright.async_api import async_playwright

async def check_application():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='ja-JP'
        )
        page = await context.new_page()
        
        try:
            print("🚀 完全版アプリケーションの確認を開始します...")
            
            # Reactアプリケーションにアクセス
            print("\n📱 完全版アプリケーションにアクセス中...")
            await page.goto("http://localhost:5173", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # ログイン画面のスクリーンショット
            screenshot_path = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_complete_login.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ ログイン画面のスクリーンショットを保存: {screenshot_path}")
            
            # ログインを試行
            print("\n🔐 管理者アカウントでログイン中...")
            # ユーザー名とパスワードを入力
            username_field = page.locator('input[type="text"], input[name="username"], input#username').first
            password_field = page.locator('input[type="password"], input[name="password"], input#password').first
            
            if await username_field.count() > 0:
                await username_field.fill('admin')
                await password_field.fill('password')
                
                # ログインボタンをクリック
                login_button = page.locator('button[type="submit"], button:has-text("ログイン"), button:has-text("Login")')
                await login_button.click()
                
                # ダッシュボード表示を待つ
                await page.wait_for_timeout(3000)
                
                # ダッシュボードのスクリーンショット
                dashboard_screenshot = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_complete_dashboard.png"
                await page.screenshot(path=dashboard_screenshot, full_page=True)
                print(f"✅ ダッシュボードのスクリーンショットを保存: {dashboard_screenshot}")
            else:
                print("⚠️ ログインフォームが見つかりませんでした")
            
            print("\n✨ 動作確認完了!")
            print("\n📱 完全版アプリケーション: http://localhost:5173")
            print("🖥️  APIドキュメント: http://localhost:8174/docs")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            error_screenshot = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_error.png"
            await page.screenshot(path=error_screenshot)
            print(f"📸 エラー時のスクリーンショット: {error_screenshot}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_application())