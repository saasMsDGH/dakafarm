const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/home/romeo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'); const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1050},locale:'fr-FR'});page.setDefaultTimeout(25000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.TEST_WEB_URL+'/#/examples/sign-in');
  await page.locator('#username input').fill(process.env.TEST_ADMIN_EMAIL);await page.locator('#password input').fill(process.env.TEST_ADMIN_PASSWORD);await page.locator('button[type=submit]').click();
  await page.getByRole('button',{name:'Élevage de poules',exact:true}).waitFor();await page.getByRole('button',{name:'Élevage de poules',exact:true}).click();
  await page.getByRole('heading',{name:'Élevage de poules pondeuses',exact:true}).waitFor();
  const bands=page.locator('.poultry-band');
  assert.equal(await bands.count(),4);
  assert.match(await page.locator('section').innerText(),/10 employés/);
  assert.match(await page.locator('section').innerText(),/100\s000 FCFA/);
  assert.match(await page.locator('section').innerText(),/10 clients/);
  assert.match((await bands.allInnerTexts()).join(' '),/Pas encore atteint/);
  await page.evaluate(()=>window.scrollTo(0,0));await page.waitForTimeout(1100);
  await page.screenshot({path:path.join(__dirname,'../docs/screenshots/poules-ponte-couts-roi.png'),fullPage:true});
  // Les listes natives contiennent les objets RH/ferme, pas seulement des cartes de dashboard.
  for (const [route,pattern] of [['/farm/flocks','DEMO-PONTE'],['/farm/productions','→'],['/farm/feeds','DEMO-PONTE'],['/farm/vaccinations','DEMO-PONTE'],['/pos/customers','DÉMO'],['/hr/employees','Employé'],['/hr/payroll','FCFA']]) {
   await page.goto(process.env.TEST_WEB_URL+'/#'+route);
   await page.locator('table tbody tr').first().waitFor();
   await page.waitForFunction(p=>document.querySelector('main')?.innerText.includes(p),pattern);
   assert.doesNotMatch(await page.locator('main').innerText(),/\bTZS\b|\bTSh\b/);
  }
  await page.goto(process.env.TEST_WEB_URL+'/#/campaigns?view=poultry');
  await page.getByRole('heading',{name:'Élevage de poules pondeuses',exact:true}).waitFor();
  await page.setViewportSize({width:390,height:844});
  await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth+1,null,{timeout:6000});
  assert.deepEqual(errors,[]);
  console.log('Navigateur avicole : 4 bandes, coûts/ROI, 10 clients, 10 employés, paies FCFA, listes natives et mobile vérifiés.');
 } finally {await browser.close();}
})().catch(e=>{let m=e.message;for(const v of [process.env.TEST_ADMIN_PASSWORD,process.env.TEST_ADMIN_EMAIL])if(v)m=m.replaceAll(v,'[masqué]');console.error('Échec recette avicole : '+m);process.exitCode=1;});
