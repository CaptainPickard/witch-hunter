const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ executablePath: '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell', args: ['--no-sandbox','--enable-unsafe-swiftshader'] });
  const page = await browser.newPage();
  const errs = []; const fails = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('requestfailed', r => { if (!/ERR_ABORTED/.test(r.failure() || '')) fails.push(r.url() + ' ' + (r.failure()||'')); });
  page.on('response', r => { if (r.status() >= 400) console.log('HTTP4XX', r.status(), r.url()); });
  const bars = [];
  page.on('console', m => { const t = m.text(); if (t.includes('boot barrier') || t.includes('loaded 80') || /stand-in/i.test(t)) bars.push(t); });
  await page.goto('http://172.16.5.1:8793/current/prototype/builds/v8-playable.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(25000);
  bars.forEach(b => console.log('CONSOLE:', b.slice(0, 160)));
  console.log('FINAL: pageerrors=' + errs.length + ' | reqfailed=' + fails.length);
  if (errs.length) console.log(errs.slice(0,3).join('\n').slice(0, 400));
  await browser.close();
})().catch(e => { console.error('HARNESS-ERROR:', String(e).slice(0,200)); process.exit(2); });
