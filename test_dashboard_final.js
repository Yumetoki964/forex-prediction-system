const { chromium } = require('playwright');

(async () => {
  console.log('🎯 最終動作確認テスト開始...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 200 
  });
  
  const page = await browser.newPage();
  
  try {
    // 1. ログイン
    console.log('1️⃣ ログイン中...');
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 2. ダッシュボードページ確認
    console.log('2️⃣ ダッシュボードページ確認...');
    const url = page.url();
    console.log('   現在のURL:', url);
    
    // エラーメッセージの確認
    const hasError = await page.locator('text=/404|エラー|失敗/i').count() > 0;
    const hasWarning = await page.locator('text=/一部データの取得に失敗/i').count() > 0;
    
    if (hasError) {
      console.log('   ❌ エラーメッセージが表示されています');
    } else if (hasWarning) {
      console.log('   ⚠️ 警告メッセージが表示されていますが、ページは動作しています');
    } else {
      console.log('   ✅ エラーなし');
    }
    
    // 3. 主要コンポーネントの確認
    console.log('\n3️⃣ 主要コンポーネントの表示確認...');
    
    const components = [
      { selector: 'text=/現在レート|Current Rate/i', name: '現在レート' },
      { selector: 'text=/予測|Prediction/i', name: '予測情報' },
      { selector: 'text=/シグナル|Signal/i', name: 'シグナル' },
      { selector: 'text=/リスク|Risk/i', name: 'リスク指標' }
    ];
    
    for (const comp of components) {
      const exists = await page.locator(comp.selector).count() > 0;
      console.log(`   ${comp.name}: ${exists ? '✅' : '❌'}`);
    }
    
    // 4. APIレスポンス確認
    console.log('\n4️⃣ APIレスポンス状態...');
    
    // ネットワークリクエストを監視
    const apiStatus = {};
    page.on('response', response => {
      const url = response.url();
      if (url.includes('/api/')) {
        const endpoint = url.split('/api/')[1];
        apiStatus[endpoint] = response.status();
      }
    });
    
    // ページをリロードしてAPIコールを確認
    await page.reload();
    await page.waitForTimeout(3000);
    
    console.log('   APIステータス:');
    for (const [endpoint, status] of Object.entries(apiStatus)) {
      const icon = status === 200 ? '✅' : status >= 500 ? '❌' : '⚠️';
      console.log(`     ${icon} ${endpoint}: ${status}`);
    }
    
    // 5. スクリーンショット保存
    await page.screenshot({ path: 'dashboard_final.png', fullPage: true });
    console.log('\n📸 スクリーンショット保存: dashboard_final.png');
    
    console.log('\n✅ テスト完了！');
    console.log('📌 ブラウザでダッシュボードを確認してください: http://localhost:5173');
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    await browser.close();
  }
})();