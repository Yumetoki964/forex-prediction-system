const { chromium } = require('playwright');

(async () => {
  console.log('🎯 詳細予測分析ページ直接アクセステスト...\n');
  
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
    
    // ログイン後のリダイレクトを待つ
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {
      console.log('   ⚠️ ダッシュボードへのリダイレクトなし');
    });
    
    // 2. 分析ページへ直接遷移
    console.log('\n2️⃣ 分析ページへ直接遷移...');
    await page.goto('http://localhost:5173/analysis');
    await page.waitForTimeout(3000);
    
    const url = page.url();
    console.log('   現在のURL:', url);
    
    // 3. ページ内容の確認
    console.log('\n3️⃣ ページ内容の確認...');
    
    // ページのHTMLを取得して表示
    const bodyText = await page.textContent('body');
    if (bodyText.includes('詳細予測分析')) {
      console.log('   ✅ 詳細予測分析ページが表示されています');
    } else if (bodyText.includes('404')) {
      console.log('   ❌ 404エラーページが表示されています');
    } else if (bodyText.includes('ログイン')) {
      console.log('   ⚠️ ログインページにリダイレクトされました');
    } else {
      console.log('   ❓ 不明なページが表示されています');
      console.log('   表示内容の最初の200文字:', bodyText.substring(0, 200));
    }
    
    // 4. コンソールエラーの確認
    console.log('\n4️⃣ コンソールエラーの確認...');
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('   ❌ エラー:', msg.text());
      }
    });
    
    // ページをリロードしてエラーを捕捉
    await page.reload();
    await page.waitForTimeout(2000);
    
    // 5. スクリーンショット
    await page.screenshot({ path: 'analysis_direct.png', fullPage: true });
    console.log('\n📸 スクリーンショット保存: analysis_direct.png');
    
    console.log('\n✅ テスト完了！');
    console.log('📌 ブラウザウィンドウを確認してください');
    
    // ブラウザは開いたままにする
    await page.waitForTimeout(10000);
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    await browser.close();
  }
})();