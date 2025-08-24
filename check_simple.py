#!/usr/bin/env python3
"""
シンプルHTMLのアプリケーションをPlaywrightで確認
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
            print("🚀 シンプル版アプリケーションの確認を開始します...")
            
            # シンプルHTMLにアクセス
            print("\n📱 アプリケーションにアクセス中...")
            await page.goto("http://localhost:5173/simple.html", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # スクリーンショットを撮影
            screenshot_path = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_simple.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ スクリーンショットを保存: {screenshot_path}")
            
            # デモアカウントでログイン
            print("\n🔐 デモアカウントでログイン中...")
            await page.fill('#username', 'admin')
            await page.fill('#password', 'password')
            await page.click('button[type="submit"]')
            
            # ログイン結果を待つ
            await page.wait_for_timeout(3000)
            
            # ダッシュボードのスクリーンショット
            dashboard_screenshot = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_dashboard.png"
            await page.screenshot(path=dashboard_screenshot, full_page=True)
            print(f"✅ ダッシュボードのスクリーンショットを保存: {dashboard_screenshot}")
            
            print("\n✨ 動作確認完了!")
            print("\n📱 アプリケーションURL: http://localhost:5173/simple.html")
            print("🖥️  APIドキュメント: http://localhost:8174/docs")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_application())