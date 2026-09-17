with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()
import re
code = re.sub(r'discount:\s*0,\s*amount_paid:\s*0,', "discount: '', amount_paid: '',", code)
with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()
code = re.sub(r'discount:\s*0,\s*amount_paid:\s*0,', "discount: '', amount_paid: '',", code)
with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
