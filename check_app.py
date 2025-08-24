#!/usr/bin/env python3
"""
Playwrightを使用してアプリケーションの動作確認とスクリーンショット取得
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def check_application():
    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='ja-JP'
        )
        page = await context.new_page()
        
        try:
            print("🚀 アプリケーションの確認を開始します...")
            
            # フロントエンドにアクセス
            print("\n📱 フロントエンドにアクセス中...")
            await page.goto("http://localhost:5173", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # スクリーンショットを撮影
            screenshot_path = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_frontend.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ フロントエンドのスクリーンショットを保存: {screenshot_path}")
            
            # ページのタイトルとコンテンツを確認
            title = await page.title()
            print(f"📄 ページタイトル: {title}")
            
            # ページのテキストコンテンツを取得
            content = await page.text_content("body")
            if content:
                # 最初の200文字を表示
                print(f"📝 ページコンテンツ（最初の200文字）:\n{content[:200]}...")
            
            # エラーがないか確認
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            # APIドキュメントにアクセス
            print("\n🖥️  APIドキュメントにアクセス中...")
            await page.goto("http://localhost:8174/docs", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # APIドキュメントのスクリーンショット
            api_screenshot_path = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_api.png"
            await page.screenshot(path=api_screenshot_path, full_page=True)
            print(f"✅ APIドキュメントのスクリーンショットを保存: {api_screenshot_path}")
            
            # エラーチェック
            if console_errors:
                print("\n⚠️ コンソールエラー:")
                for error in console_errors[:5]:
                    print(f"  - {error}")
            else:
                print("\n✅ コンソールエラーはありません")
            
            print("\n✨ 動作確認完了!")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            # エラー時のスクリーンショット
            error_screenshot = "/Users/yumetokicross/Desktop/forex-prediction-system/screenshot_error.png"
            await page.screenshot(path=error_screenshot)
            print(f"📸 エラー時のスクリーンショット: {error_screenshot}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_application())