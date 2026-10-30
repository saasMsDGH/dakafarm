import test from 'node:test';
import assert from 'node:assert/strict';
import { money, chartRows } from './numbers.mjs';
test('formatte exactement les grands montants sans passage par Number', () => {
  assert.equal(money('9007199254740993').replace(/\s/g, ''), '9007199254740993FCFA');
  assert.equal(money(null), 'À vérifier');
});
test('refuse un graphique qui perdrait la précision ou inventerait un résultat', () => {
  assert.equal(chartRows([{ v: '9007199254740993' }], ['v']), null);
  assert.equal(chartRows([{ v: null }], ['v']), null);
  assert.deepEqual(chartRows([{ v: '-1200', period: '2025' }], ['v']), [{ v: -1200, period: '2025' }]);
});
import { readFileSync } from 'node:fs';
test('les pages financières et les impressions ne portent plus de libellé shilling', () => {
  for (const file of ['../hr/Payroll.jsx','../pos/Sales.jsx','../pos/Purchases.jsx','../assets/AssetsList.jsx','../finance/FinanceDashboard.jsx','../dashboard/DashboardOverview.jsx','../reports/FarmOperationsReport.jsx']) {
    assert.doesNotMatch(readFileSync(new URL(file, import.meta.url), 'utf8'), /TZS|TSh|Tanzanian Shillings/);
  }
});
