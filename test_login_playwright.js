const { chromium } = require('playwright');

(async () => {
  console.log('🚀 ログインテスト開始...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500 
  });
  
  const page = await browser.newPage();
  
  try {
    // ログインページにアクセス
    console.log('1️⃣ ログインページへアクセス中...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    await page.screenshot({ path: 'login_page.png' });
    console.log('   ✅ ログインページ表示完了\n');
    
    // ページの状態確認
    console.log('2️⃣ ページ要素を確認中...');
    const usernameInput = await page.locator('input[type="text"], input[name="username"], input[placeholder*="ユーザー"], input[placeholder*="user"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="パスワード"], input[placeholder*="pass"]').first();
    const loginButton = await page.locator('button:has-text("ログイン"), button:has-text("Login"), button[type="submit"]').first();
    
    console.log('   ユーザー名入力欄: ' + (await usernameInput.count() > 0 ? '✅ 存在' : '❌ 見つからない'));
    console.log('   パスワード入力欄: ' + (await passwordInput.count() > 0 ? '✅ 存在' : '❌ 見つからない'));
    console.log('   ログインボタン: ' + (await loginButton.count() > 0 ? '✅ 存在' : '❌ 見つからない\n'));
    
    // ログイン情報入力
    console.log('3️⃣ ログイン情報を入力中...');
    await usernameInput.fill('admin');
    console.log('   ユーザー名: admin');
    await passwordInput.fill('password');
    console.log('   パスワード: ********\n');
    
    // ネットワークリクエストを監視
    console.log('4️⃣ APIリクエストを監視開始...');
    
    page.on('request', request => {
      if (request.url().includes('login') || request.url().includes('auth')) {
        console.log('   📤 リクエスト:', request.method(), request.url());
        if (request.method() === 'POST') {
          console.log('   📦 ボディ:', request.postData());
        }
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('login') || response.url().includes('auth')) {
        console.log('   📥 レスポンス:', response.status(), response.url());
      }
    });
    
    // ログインボタンクリック
    console.log('\n5️⃣ ログインボタンをクリック...');
    await loginButton.click();
    
    // レスポンス待機
    await page.waitForTimeout(3000);
    
    // エラーメッセージ確認
    console.log('\n6️⃣ 結果を確認中...');
    const errorMessage = await page.locator('text=/ログインに失敗|エラー|失敗|Invalid|Error/i').first();
    if (await errorMessage.count() > 0) {
      console.log('   ❌ エラーメッセージ検出:', await errorMessage.textContent());
    }
    
    // 現在のURL確認
    const currentUrl = page.url();
    console.log('   現在のURL:', currentUrl);
    
    // ダッシュボードへの遷移確認
    if (currentUrl.includes('dashboard')) {
      console.log('   ✅ ダッシュボードへ遷移成功！');
    } else {
      console.log('   ⚠️ ダッシュボードへ遷移していません');
      
      // コンソールエラー確認
      const consoleMessages = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleMessages.push(msg.text());
        }
      });
      
      await page.waitForTimeout(1000);
      if (consoleMessages.length > 0) {
        console.log('\n   📝 コンソールエラー:');
        consoleMessages.forEach(msg => console.log('      -', msg));
      }
    }
    
    // 最終スクリーンショット
    await page.screenshot({ path: 'login_result.png' });
    console.log('\n📸 スクリーンショット保存: login_page.png, login_result.png');
    
  } catch (error) {
    console.error('\n❌ エラー発生:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ テスト完了');
  }
})();