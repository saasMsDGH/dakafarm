// Recette des données réellement importées par les tests PostgreSQL, sans mocks HTTP.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/home/romeo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1050 }, locale: 'fr-FR' });
    page.setDefaultTimeout(20000);
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    await page.goto(process.env.TEST_WEB_URL + '/#/examples/sign-in');
    await page.locator('#username input').fill(process.env.TEST_ADMIN_EMAIL);
    await page.locator('#password input').fill(process.env.TEST_ADMIN_PASSWORD);
    await page.locator('button[type=submit]').click();
    await page.getByRole('heading', { name: 'Comment les activités coexistent', exact: true }).waitFor();
    const comparison = page.getByRole('table').filter({ has: page.getByRole('columnheader', { name: 'Besoin maximal avant apports', exact: true }) });
    assert.equal(await comparison.locator('tbody tr').count(), 8);
    assert.match(await comparison.innerText(), /Déficitaire/);
    assert.match(await comparison.innerText(), /Trésorerie à soutenir/);
    assert.match(await comparison.innerText(), /Excédentaire/);
    await page.getByText(/^Calendrier des 32 campagnes/).click();
    const calendar = page.getByRole('table').filter({ has: page.getByRole('columnheader', { name: 'Chronologie des campagnes', exact: true }) });
    assert.equal(await calendar.locator('tbody tr').count(), 32);
    await page.getByText(/^Calendrier des 32 campagnes/).click();
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForTimeout(1100);
    await page.screenshot({ path: path.join(__dirname, '../docs/screenshots/coexistence-8-activites-32-campagnes.png'), fullPage: true });
    await page.getByLabel('Activité à comparer').selectOption({ label: 'Téléphonie' });
    await comparison.getByRole('rowheader', { name: /Téléphonie/ }).waitFor();
    assert.equal(await comparison.locator('tbody tr').count(), 1);
    assert.match(await comparison.innerText(), /Téléphonie/);
    assert.match(await comparison.getByRole('rowheader').textContent(), /4 campagnes/);
    await page.getByLabel('Activité à comparer').selectOption('all');
    await page.getByRole('heading', { name: 'Comment les activités coexistent', exact: true }).waitFor();
    await page.getByRole('button', { name: '1. Lire les résultats', exact: true }).click();
    await page.getByRole('heading', { name: 'Lecture par année', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Activités côte à côte', exact: true }).click();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole('heading', { name: 'Comment les activités coexistent', exact: true }).waitFor();
    await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth + 1, null, { timeout: 5000 });
    assert.deepEqual(errors, []);
    console.log('Navigateur coexistence : 8 activités, 32 campagnes, scénarios contrastés, filtrage, chronologie, graphiques et mobile vérifiés.');
  } finally { await browser.close(); }
})().catch(e => {
  let message = e.message;
  for (const value of [process.env.TEST_ADMIN_PASSWORD, process.env.TEST_ADMIN_EMAIL]) if (value) message = message.replaceAll(value, '[masqué]');
  console.error('Échec recette coexistence : ' + message); process.exitCode = 1;
});
