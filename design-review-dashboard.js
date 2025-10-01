// Design Review for Dashboard Page
const { chromium } = require('playwright');

async function designReviewDashboard() {
  console.log('🎨 Starting Comprehensive Design Review for Dashboard Page...');
  
  const browser = await chromium.launch({
    headless: false,
    devtools: true
  });
  
  const page = await browser.newPage();
  
  try {
    // Navigate to Dashboard page
    console.log('📱 Navigating to Dashboard page...');
    await page.goto('http://localhost:5175/');
    
    // Take screenshots for analysis
    console.log('📸 Taking screenshots for design analysis...');
    
    // Desktop screenshot
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({
      path: 'screenshots/dashboard-design-review-desktop.png',
      fullPage: true
    });
    
    // Mobile screenshot
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({
      path: 'screenshots/dashboard-design-review-mobile.png',
      fullPage: true
    });
    
    console.log('\n🎉 Design Review Complete! Check screenshots folder.');
    
  } catch (error) {
    console.error('❌ Design review failed:', error);
  } finally {
    await browser.close();
  }
}

designReviewDashboard();
