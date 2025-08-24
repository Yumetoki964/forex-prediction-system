const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    console.log('Opening application...');
    await page.goto('http://localhost:5173');
    
    // Wait for login form to be visible
    await page.waitForSelector('input[type="text"]', { timeout: 5000 });
    
    // Take screenshot of login page
    await page.screenshot({ path: 'screenshot_login_page.png' });
    console.log('Login page loaded successfully');
    
    // Fill in credentials
    console.log('Entering credentials...');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'password');
    
    // Take screenshot before clicking login
    await page.screenshot({ path: 'screenshot_before_login.png' });
    
    // Click login button
    console.log('Clicking login button...');
    await page.click('button[type="submit"]');
    
    // Wait for navigation or error message
    await page.waitForTimeout(2000);
    
    // Take screenshot after login attempt
    await page.screenshot({ path: 'screenshot_after_login.png' });
    
    // Check if we're still on login page (error) or navigated to dashboard
    const currentUrl = page.url();
    if (currentUrl.includes('dashboard') || !await page.isVisible('input[type="text"]')) {
      console.log('✅ Login successful! Redirected to:', currentUrl);
    } else {
      // Check for error message
      const errorText = await page.textContent('body');
      if (errorText.includes('失敗') || errorText.includes('error')) {
        console.log('❌ Login failed with error');
      } else {
        console.log('⚠️ Login status unclear');
      }
    }
    
  } catch (error) {
    console.error('Error during test:', error);
  } finally {
    await browser.close();
  }
})();