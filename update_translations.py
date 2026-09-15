import json

sw_path = "frontend/public/locales/sw/translation.json"
with open(sw_path, "r", encoding="utf-8-sig") as f:
    sw_data = json.load(f)

sw_data.update({
    "pos_management": "Mauzo (POS)",
    "customers": "Wateja",
    "pos_sales": "Mauzo na Risiti",
    "add_customer": "Ongeza Mteja",
    "business_type": "Aina ya Biashara",
    "credit_limit": "Kikomo cha Deni",
    "outstanding_balance": "Deni",
    "search_customers": "Tafuta Wateja...",
    "new_sale": "Mauzo Mapya",
    "invoice_no": "Namba ya Ankara",
    "subtotal": "Jumla Ndogo",
    "discount": "Punguzo",
    "total_due": "Jumla",
    "amount_paid": "Kiasi Kilicholipwa",
    "payment_status": "Hali ya Malipo",
    "payment_method": "Njia ya Malipo",
    "add_payment": "Ongeza Malipo",
    "print_receipt_small": "Chapisha Risiti (Ndogo)",
    "print_invoice_a4": "Chapisha Ankara (A4)",
    "receipt_no": "Namba ya Risiti",
    "cash": "Taslimu",
    "mobile_money": "Pesa Mtandao",
    "bank_transfer": "Benki",
    "unpaid": "Haijalipwa",
    "partial": "Nusu",
    "paid": "Imelipwa",
    "add_to_cart": "Weka Kikapuni",
    "checkout": "Kamilisha Mauzo",
    "select_customer": "-- Chagua Mteja --",
    "retail": "Rejareja",
    "wholesale": "Jumla",
    "view_sale": "Tazama Mauzo"
})

with open(sw_path, "w", encoding="utf-8") as f:
    json.dump(sw_data, f, indent=4, ensure_ascii=False)

en_path = "frontend/public/locales/en/translation.json"
try:
    with open(en_path, "r", encoding="utf-8-sig") as f:
        en_data = json.load(f)
except FileNotFoundError:
    en_data = {}

en_data.update({
    "pos_management": "Point of Sale",
    "customers": "Customers",
    "pos_sales": "Sales & Invoices",
    "add_customer": "Add Customer",
    "business_type": "Business Type",
    "credit_limit": "Credit Limit",
    "outstanding_balance": "Outstanding Balance",
    "search_customers": "Search Customers...",
    "new_sale": "New Sale",
    "invoice_no": "Invoice No",
    "subtotal": "Subtotal",
    "discount": "Discount",
    "total_due": "Total Due",
    "amount_paid": "Amount Paid",
    "payment_status": "Payment Status",
    "payment_method": "Payment Method",
    "add_payment": "Add Payment",
    "print_receipt_small": "Print Receipt (Small)",
    "print_invoice_a4": "Print Invoice (A4)",
    "receipt_no": "Receipt No",
    "cash": "Cash",
    "mobile_money": "Mobile Money",
    "bank_transfer": "Bank Transfer",
    "unpaid": "UNPAID",
    "partial": "PARTIAL",
    "paid": "PAID",
    "add_to_cart": "Add",
    "checkout": "Submit Sale",
    "select_customer": "-- Select Customer --",
    "retail": "Retail",
    "wholesale": "Wholesale",
    "view_sale": "View"
})

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(en_data, f, indent=4, ensure_ascii=False)
