with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()
import re
code = re.sub(
    r'quantity:\s*item\.quantity \+ 1',
    r'quantity: (parseFloat(item.quantity) || 0) + 1',
    code
)
with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()
code = re.sub(
    r'quantity:\s*item\.quantity \+ 1',
    r'quantity: (parseFloat(item.quantity) || 0) + 1',
    code
)
with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
