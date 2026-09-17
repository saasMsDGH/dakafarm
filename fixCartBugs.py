with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# 1. Fix removeCartItem -> removeFromCart
code = code.replace("removeCartItem(idx)", "removeFromCart(idx)")

# 2. Fix the supplierOptions mapping
supplier_options_search = """  const supplierOptions = suppliers.map(c => ({
    value: c.id,
    label: `${c.name} (${c.business_type || 'Retail'}) - Limit: ${parseFloat(c.credit_limit).toLocaleString()}`
  }));"""
supplier_options_replace = """  const supplierOptions = suppliers.map(c => ({
    value: c.id,
    label: c.name
  }));"""
code = code.replace(supplier_options_search, supplier_options_replace)

# 3. Fix the default zero in cart inputs
# unit_price input
unit_price_search = """newCart[idx].unit_price = parseFloat(e.target.value) || 0;"""
unit_price_replace = """newCart[idx].unit_price = e.target.value;"""
code = code.replace(unit_price_search, unit_price_replace)

# new_selling_price input
selling_price_search = """newCart[idx].new_selling_price = parseFloat(e.target.value) || 0;"""
selling_price_replace = """newCart[idx].new_selling_price = e.target.value;"""
code = code.replace(selling_price_search, selling_price_replace)

# 4. Fix discount and amount_paid
# Wait, let's see how they are handled. If they just use `e.target.value`, then backspacing is fine.
# In `Purchases.jsx`: `value={newPurchase.discount} onChange={(e) => setNewPurchase({...newPurchase, discount: e.target.value})}`
# This is fine, but if the state defaults to `0`, maybe we should allow it to be `""`.
code = code.replace("discount: 0, amount_paid: 0,", "discount: '', amount_paid: '',")

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)


with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    sales_code = f.read()

sales_code = sales_code.replace("removeCartItem(idx)", "removeFromCart(idx)")
sales_code = sales_code.replace("discount: 0, amount_paid: 0,", "discount: '', amount_paid: '',")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(sales_code)

