with open("frontend/src/pages/pos/Customers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# I will replace some obvious english strings with t('...')
code = code.replace("<h2>Customers</h2>", "<h2>{t('customers')}</h2>")
code = code.replace("Manage your point of sale customers, credit limits, and balances.", "{t('profile_description')}")
code = code.replace("Search Customers...", "{t('search_customers')}")
code = code.replace("Add Customer", "{t('add_customer')}")
code = code.replace("Business Type", "{t('business_type')}")
code = code.replace("Credit Limit", "{t('credit_limit')}")
code = code.replace("Outstanding Balance", "{t('outstanding_balance')}")

with open("frontend/src/pages/pos/Customers.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<h2>Sales & Invoices</h2>", "<h2>{t('pos_sales')}</h2>")
code = code.replace("Manage point of sale transactions, credit limits, and receipts.", "{t('profile_description')}")
code = code.replace("New Sale", "{t('new_sale')}")
code = code.replace("Invoice No", "{t('invoice_no')}")
code = code.replace("Payment Status", "{t('payment_status')}")
code = code.replace("Amount Paid", "{t('amount_paid')}")
code = code.replace("View", "{t('view_sale')}")
code = code.replace("Print Receipt (Small)", "{t('print_receipt_small')}")
code = code.replace("Print Invoice (A4)", "{t('print_invoice_a4')}")
code = code.replace("Add Payment", "{t('add_payment')}")
code = code.replace("Subtotal", "{t('subtotal')}")
code = code.replace("Discount", "{t('discount')}")
code = code.replace("Total Due", "{t('total_due')}")
code = code.replace("Add to Cart", "{t('add_to_cart')}")
code = code.replace("Submit Sale", "{t('checkout')}")

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
