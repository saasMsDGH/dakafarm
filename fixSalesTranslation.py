with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<td>{t('subtotal')}:</td>", "<td>${t('subtotal')}:</td>")
code = code.replace("<td>{t('discount')}:</td>", "<td>${t('discount')}:</td>")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
