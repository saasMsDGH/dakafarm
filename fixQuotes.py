with open("frontend/src/pages/pos/Customers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("'{t('add_customer')}'", "t('add_customer')")
code = code.replace('"{t(\'search_customers\')}"', "t('search_customers')")
code = code.replace("show{t('add_customer')}Modal", "showAddCustomerModal")
code = code.replace("setShow{t('add_customer')}Modal", "setShowAddCustomerModal")
code = code.replace("handle{t('add_customer')}Click", "handleAddCustomerClick")
code = code.replace("submit{t('add_customer')}", "submitAddCustomer")


with open("frontend/src/pages/pos/Customers.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code2 = f.read()

code2 = code2.replace("handle{t('view_sale')}Sale", "handleViewSale")
code2 = code2.replace("show{t('view_sale')}Modal", "showViewModal")
code2 = code2.replace("setShow{t('view_sale')}Modal", "setShowViewModal")
code2 = code2.replace("'{t('view_sale')}'", "t('view_sale')")
code2 = code2.replace('"{t(\'view_sale\')}"', "t('view_sale')")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code2)

