import re
with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

m_invoice = re.search(r'const handlePrintInvoice = \(\) => \{.*?(?=const handlePrintReceipt)', code, flags=re.DOTALL)
m_receipt = re.search(r'const handlePrintReceipt = \(\) => \{.*?(?=const submitPayment)', code, flags=re.DOTALL)

with open("print_funcs.txt", "w", encoding="utf-8") as f:
    f.write(m_invoice.group(0))
    f.write("\n\n")
    if m_receipt:
        f.write(m_receipt.group(0))
