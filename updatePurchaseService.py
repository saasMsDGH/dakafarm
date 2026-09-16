with open("backend/app/api/v1/pos/service/PurchaseService.py", "r", encoding="utf-8") as f:
    code = f.read()

import re
code = code.replace(
    'product.unit_price = req_item.unit_cost',
    'product.unit_price = req_item.unit_cost\n            if req_item.new_selling_price is not None:\n                product.selling_price = req_item.new_selling_price'
)

with open("backend/app/api/v1/pos/service/PurchaseService.py", "w", encoding="utf-8") as f:
    f.write(code)
