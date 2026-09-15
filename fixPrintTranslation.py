with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Only replace inside the literal HTML strings
code = code.replace("<td>${t('subtotal')}:</td>", "<td>Subtotal:</td>")
code = code.replace("<td>${t('discount')}:</td>", "<td>Discount:</td>")

# Also for the receipt
code = code.replace("<div>${t('subtotal')}</div>", "<div>SUBTOTAL</div>")
code = code.replace("<div>${t('discount')}</div>", "<div>DISCOUNT</div>")
code = code.replace("<div>${t('total_due')}</div>", "<div>TOTAL</div>")
code = code.replace("<div>${t('amount_paid')}</div>", "<div>CASH / PAID</div>")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
