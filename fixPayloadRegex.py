with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re
code = re.sub(
    r'items:\s*cartItems\.map\(item => \(\{\s*product_id:\s*item\.product_id,\s*quantity:\s*item\.quantity,\s*unit_price:\s*item\.unit_price\s*\}\)\)',
    """items: cartItems.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          unit_cost: item.unit_price,
          new_selling_price: item.new_selling_price
        }))""",
    code
)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
