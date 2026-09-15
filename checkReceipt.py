import re
with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

m_receipt = re.search(r'const handlePrintReceipt = \(\) => \{.*?(?=const handlePrintInvoice)', code, flags=re.DOTALL)
if m_receipt:
    print(m_receipt.group(0))
