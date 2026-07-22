const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const outputDir = path.join(__dirname, '../docs/images');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  console.log('Navigating to https://trinetra-wsfr.onrender.com...');
  await page.goto('https://trinetra-wsfr.onrender.com', { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(3000);

  // 1. Capture Login View
  console.log('Capturing Login View...');
  await page.screenshot({ path: path.join(outputDir, 'login_screen.png') });

  // 2. Perform Sign In
  console.log('Signing in...');
  await page.fill('input[name="email"]', 'admin@industrial.local');
  await page.fill('input[name="password"]', 'SafetyDemo!2026');
  await page.click('button[type="submit"]');

  await page.waitForSelector('#appView:not(.hidden)', { timeout: 15000 });
  await page.waitForTimeout(2000);

  // 3. Mission Control Dashboard
  console.log('Capturing Mission Control...');
  await page.screenshot({ path: path.join(outputDir, 'mission_control.png') });

  // 4. Digital Twin
  console.log('Navigating to Digital Twin...');
  await page.click('button[data-module="twin"]');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outputDir, 'digital_twin.png') });

  // 5. Risk Intelligence
  console.log('Navigating to Risk Intelligence...');
  await page.click('button[data-module="risk"]');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outputDir, 'risk_intelligence.png') });

  // 6. Administration & CCTV Wall
  console.log('Navigating to Administration / CCTV Wall...');
  await page.click('button[data-module="admin"]');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, 'cctv_surveillance_wall.png') });

  console.log('Screenshots successfully captured!');
  await browser.close();
})();
