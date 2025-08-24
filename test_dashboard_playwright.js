const { chromium } = require('playwright');

(async () => {
  console.log('🚀 ダッシュボードアクセステスト開始...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100 
  });
  
  const page = await browser.newPage();
  
  // コンソールエラーを記録
  const consoleMessages = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleMessages.push(msg.text());
    }
  });
  
  // ネットワークエラーを記録
  const failedRequests = [];
  page.on('requestfailed', request => {
    failedRequests.push({
      url: request.url(),
      failure: request.failure()
    });
  });
  
  try {
    // 1. ログインページにアクセス
    console.log('1️⃣ ログインページへアクセス...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    
    // 2. ログイン実行
    console.log('2️⃣ ログイン実行中...');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // 3. ダッシュボードへの遷移を待つ
    console.log('3️⃣ ダッシュボードへの遷移を待機中...');
    await page.waitForTimeout(2000);
    
    // 4. 現在のURLを確認
    const currentUrl = page.url();
    console.log('   現在のURL:', currentUrl);
    
    // 5. ページコンテンツを確認
    console.log('\n4️⃣ ページ内容を確認中...');
    const pageTitle = await page.title();
    console.log('   ページタイトル:', pageTitle);
    
    // エラーメッセージの確認
    const errorText = await page.locator('text=/404|not found|見つかりません/i').first();
    if (await errorText.count() > 0) {
      console.log('   ❌ エラーメッセージ検出:', await errorText.textContent());
    } else {
      console.log('   ✅ エラーメッセージなし');
    }
    
    // ダッシュボード要素の確認
    const dashboardTitle = await page.locator('h1:has-text("ダッシュボード"), text=/dashboard/i').first();
    if (await dashboardTitle.count() > 0) {
      console.log('   ✅ ダッシュボードタイトル検出');
    } else {
      console.log('   ⚠️ ダッシュボードタイトルが見つかりません');
    }
    
    // 6. コンソールエラーの確認
    if (consoleMessages.length > 0) {
      console.log('\n5️⃣ コンソールエラー:');
      consoleMessages.forEach(msg => console.log('   ❌', msg));
    } else {
      console.log('\n5️⃣ コンソールエラー: なし');
    }
    
    // 7. ネットワークエラーの確認
    if (failedRequests.length > 0) {
      console.log('\n6️⃣ 失敗したリクエスト:');
      failedRequests.forEach(req => {
        console.log('   ❌', req.url);
        console.log('      理由:', req.failure?.errorText);
      });
    } else {
      console.log('\n6️⃣ ネットワークエラー: なし');
    }
    
    // 8. スクリーンショット保存
    await page.screenshot({ path: 'dashboard_access_test.png', fullPage: true });
    console.log('\n📸 スクリーンショット保存: dashboard_access_test.png');
    
    // 9. ソースコードを取得
    const htmlContent = await page.content();
    console.log('\n7️⃣ HTMLコンテンツ長:', htmlContent.length, '文字');
    
    // bodyの内容を確認
    const bodyText = await page.locator('body').textContent();
    console.log('   ページ本文の最初の200文字:');
    console.log('   ', bodyText.substring(0, 200).replace(/\n/g, ' '));
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ テスト完了');
  }
})();