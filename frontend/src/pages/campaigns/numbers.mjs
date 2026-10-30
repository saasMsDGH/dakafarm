// Les montants du rapport sont des entiers décimaux sérialisés en chaînes.
export function money(value) {
  if (value === null || value === undefined) return 'À vérifier';
  return new Intl.NumberFormat('fr-FR').format(BigInt(value)) + ' FCFA';
}
export function chartRows(rows, keys) {
  const max = BigInt(Number.MAX_SAFE_INTEGER);
  for (const row of rows) for (const key of keys) {
    if (row[key] === null || row[key] === undefined) return null;
    const n = BigInt(row[key]);
    if (n > max || n < -max) return null;
  }
  return rows.map(row => ({ ...row, ...Object.fromEntries(keys.map(k => [k, Number(row[k])])) }));
}
