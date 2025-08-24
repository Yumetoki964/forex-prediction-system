const { chromium } = require('playwright');

(async () => {
  console.log('🔍 認証デバッグテスト開始...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100,
    devtools: true // 開発者ツールを自動で開く
  });
  
  const page = await browser.newPage();
  
  // localStorage の値を監視
  page.on('console', msg => {
    console.log('ブラウザコンソール:', msg.text());
  });
  
  try {
    // 1. ログイン実行
    console.log('1️⃣ ログインページへアクセス...');
    await page.goto('http://localhost:5173/login');
    await page.waitForTimeout(1000);
    
    // ログイン前のlocalStorage確認
    const beforeLogin = await page.evaluate(() => {
      return {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user'),
        allKeys: Object.keys(localStorage)
      };
    });
    console.log('   ログイン前のlocalStorage:', beforeLogin);
    
    // ログイン実行
    console.log('\n2️⃣ ログイン実行中...');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // ログイン後のlocalStorage確認
    const afterLogin = await page.evaluate(() => {
      return {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user'),
        allKeys: Object.keys(localStorage)
      };
    });
    console.log('   ログイン後のlocalStorage:', afterLogin);
    
    // 現在のURL確認
    console.log('   現在のURL:', page.url());
    
    // 3. ダッシュボードへ直接アクセス
    console.log('\n3️⃣ ダッシュボードへ直接アクセス...');
    await page.goto('http://localhost:5173/dashboard');
    await page.waitForTimeout(2000);
    
    console.log('   ダッシュボードURL:', page.url());
    
    // ページ内容確認
    const pageContent = await page.evaluate(() => {
      return {
        title: document.title,
        bodyText: document.body.innerText.substring(0, 200),
        hasError: document.body.innerText.includes('404') || document.body.innerText.includes('見つかりません')
      };
    });
    
    console.log('\n4️⃣ ページ内容:');
    console.log('   タイトル:', pageContent.title);
    console.log('   404エラー:', pageContent.hasError ? '❌ あり' : '✅ なし');
    console.log('   本文抜粋:', pageContent.bodyText);
    
    // React Routerの状態確認
    const routerState = await page.evaluate(() => {
      // React Router の情報を取得
      const rootEl = document.getElementById('root');
      if (rootEl && rootEl._reactRootContainer) {
        return 'React app is mounted';
      }
      return 'React app status unknown';
    });
    console.log('\n5️⃣ Reactアプリ状態:', routerState);
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    console.log('\n⏸️ ブラウザを開いたままにします。手動で確認してください。');
    console.log('終了するにはターミナルでCtrl+Cを押してください。');
    
    // ブラウザを開いたままにする
    await new Promise(() => {});
  }
})();