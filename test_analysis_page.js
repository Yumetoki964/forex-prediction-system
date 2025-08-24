const { chromium } = require('playwright');

(async () => {
  console.log('🎯 詳細予測分析ページのテスト開始...\n');
  
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
    
    // 2. 詳細予測分析ページへ移動
    console.log('2️⃣ 詳細予測分析ページへ移動...');
    // ダッシュボードから分析ページへのリンクをクリック
    const analysisLink = await page.locator('a[href="/analysis"], button:has-text("詳細予測分析")').first();
    if (await analysisLink.isVisible()) {
      await analysisLink.click();
      await page.waitForTimeout(2000);
    } else {
      // 直接URLへ遷移
      await page.goto('http://localhost:5173/analysis');
      await page.waitForTimeout(3000);
    }
    
    const url = page.url();
    console.log('   現在のURL:', url);
    
    // エラーメッセージの確認
    const hasError = await page.locator('text=/404|エラー|失敗/i').count() > 0;
    if (hasError) {
      console.log('   ❌ エラーメッセージが表示されています');
    } else {
      console.log('   ✅ エラーなし');
    }
    
    // 3. 主要コンポーネントの確認
    console.log('\n3️⃣ 主要コンポーネントの表示確認...');
    
    const components = [
      { selector: 'text=/詳細予測分析/i', name: 'ページタイトル' },
      { selector: 'text=/表示期間/i', name: '期間選択' },
      { selector: 'text=/テクニカル指標/i', name: 'テクニカル指標' },
      { selector: 'text=/経済指標影響度/i', name: '経済指標' },
      { selector: 'text=/予測信頼度分析/i', name: '予測信頼度' }
    ];
    
    for (const comp of components) {
      const exists = await page.locator(comp.selector).count() > 0;
      console.log(`   ${comp.name}: ${exists ? '✅' : '❌'}`);
    }
    
    // 4. チャート表示の確認
    console.log('\n4️⃣ チャート表示の確認...');
    const chartExists = await page.locator('div[id*="apexcharts"]').count() > 0;
    console.log(`   ApexChartsチャート: ${chartExists ? '✅ 表示されています' : '❌ 表示されていません'}`);
    
    // 5. API呼び出し状態の確認
    console.log('\n5️⃣ APIレスポンス状態...');
    
    const apiStatus = {};
    page.on('response', response => {
      const url = response.url();
      if (url.includes('/api/')) {
        const endpoint = url.split('/api/')[1].split('?')[0];
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
    
    // 6. インタラクティブ要素のテスト
    console.log('\n6️⃣ インタラクティブ要素のテスト...');
    
    // 期間ボタンクリック
    const periodButton = await page.locator('button:has-text("1年")').first();
    if (await periodButton.isVisible()) {
      await periodButton.click();
      await page.waitForTimeout(1000);
      console.log('   ✅ 期間選択ボタンが動作しています');
    }
    
    // チェックボックスのテスト
    const checkbox = await page.locator('input[type="checkbox"]').first();
    if (await checkbox.isVisible()) {
      await checkbox.click();
      await page.waitForTimeout(500);
      console.log('   ✅ テクニカル指標チェックボックスが動作しています');
    }
    
    // 7. スクリーンショット保存
    await page.screenshot({ path: 'analysis_page.png', fullPage: true });
    console.log('\n📸 スクリーンショット保存: analysis_page.png');
    
    console.log('\n✅ テスト完了！');
    console.log('📌 ブラウザで詳細予測分析ページを確認してください: http://localhost:5173/analysis');
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    await browser.close();
  }
})();