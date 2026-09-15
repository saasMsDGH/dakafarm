with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# We want to find the whole handlePrintInvoice and handlePrintReceipt functions
m_invoice = re.search(r'const handlePrintInvoice = \(\) => \{.*?(?=const handlePrintReceipt)', code, flags=re.DOTALL)
if m_invoice:
    print("Found Invoice")

m_receipt = re.search(r'const handlePrintReceipt = \(\) => \{.*?(?=const submitPayment)', code, flags=re.DOTALL)
if m_receipt:
    print("Found Receipt")

