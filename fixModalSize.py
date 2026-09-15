with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<Modal as={Modal.Dialog} size=\"lg\" centered show={showNewSaleModal}", "<Modal size=\"xl\" centered show={showNewSaleModal}")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
