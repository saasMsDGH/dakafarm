with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<td>${t('subtotal')}:</td>", "<td>Subtotal:</td>")
code = code.replace("<td>${t('discount')}:</td>", "<td>Discount:</td>")

# Check if there are any other t(...) in the print window strings
# The best way is to do a regex replace in these specific functions.
import re

# find anything like ${t('some_key')} or {t('some_key')} inside Sales.jsx that might be in a print string
# but we can just replace Subtotal and Discount manually.
code = code.replace("{t('subtotal')}:", "Subtotal:")
code = code.replace("{t('discount')}:", "Discount:")
code = code.replace("{t('total_due')}:", "Total Due:")
code = code.replace("{t('amount_paid')}:", "Amount Paid:")
code = code.replace("{t('payment_status')}:", "Payment Status:")
code = code.replace("{t('payment_method')}:", "Payment Method:")

# Wait, if I replace those globally, it will overwrite my UI translations in the view modal!
# I ONLY want to replace them inside the string literals for print windows.
