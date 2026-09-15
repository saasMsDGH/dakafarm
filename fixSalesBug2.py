with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("cart{t('subtotal')}", "cartSubtotal")
code = code.replace("// {t('new_sale')} State", "// New Sale State")
# And let's check Customers.jsx
with open("frontend/src/pages/pos/Customers.jsx", "r", encoding="utf-8") as f:
    code2 = f.read()

code2 = code2.replace("set{t('add_customer')}", "setAddCustomer")
code2 = code2.replace("{t('search_customers')}", "Tafuta Wateja...") # placeholder text shouldn't have JSX braces inside the string if it's an attribute!
# wait, if it's placeholder="{t('search_customers')}", then it should be placeholder={t('search_customers')}!
# Let's fix placeholder="{t('search_customers')}" to placeholder={t('search_customers')}

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Customers.jsx", "w", encoding="utf-8") as f:
    f.write(code2)
