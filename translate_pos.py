import os
import json

sw_path = 'frontend/public/locales/sw/translation.json'
en_path = 'frontend/public/locales/en/translation.json'

with open(sw_path, 'r', encoding='utf-8') as f:
    sw_data = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# Extend translation dictionary
translations = {
    'pos_checkout': 'Malipo ya POS',
    'pop_checkout': 'Malipo ya Manunuzi',
    'invoice_details': 'Taarifa za Ankara',
    'create_new_product': 'Sajili Bidhaa Mpya',
    'payment_history': 'Historia ya Malipo',
    'item': 'Bidhaa',
    'qty': 'Idadi',
    'price': 'Bei',
    'total': 'Jumla',
    'receipt_no': 'Namba ya Risiti',
    'method': 'Njia',
    'amount': 'Kiasi',
    'total_due': 'JUMLA INAYODAIWA:',
    'total_paid': 'Jumla Iliyolipwa:',
    'sales_receipt': 'RISITI YA MAUZO',
    'purchases_receipt': 'RISITI YA MANUNUZI',
    'invoice': 'ANKARA',
    'payment_account': 'Akaunti ya Malipo',
    'pay_now': 'Lipa Sasa',
    'print_invoice': 'Chapisha Ankara',
    'print_receipt': 'Chapisha Risiti',
    'close': 'Funga',
    'save_changes': 'Hifadhi Mabadiliko'
}

for k, v in translations.items():
    if k not in sw_data:
        sw_data[k] = v
    if k not in en_data:
        en_data[k] = k.replace('_', ' ').title()

with open(sw_path, 'w', encoding='utf-8') as f:
    json.dump(sw_data, f, indent=2, ensure_ascii=False)

with open(en_path, 'w', encoding='utf-8') as f:
    json.dump(en_data, f, indent=2, ensure_ascii=False)

def safe_replace(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Sales.jsx & Purchases.jsx Replacements
pos_replacements = {
    '<Modal.Title>Point of Sale Checkout</Modal.Title>': '<Modal.Title>{t("pos_checkout", "Point of Sale Checkout")}</Modal.Title>',
    '<Modal.Title>Point of Purchase Checkout</Modal.Title>': '<Modal.Title>{t("pop_checkout", "Point of Purchase Checkout")}</Modal.Title>',
    '<Modal.Title>Invoice Details</Modal.Title>': '<Modal.Title>{t("invoice_details", "Invoice Details")}</Modal.Title>',
    '<Modal.Title>Create New Product</Modal.Title>': '<Modal.Title>{t("create_new_product", "Create New Product")}</Modal.Title>',
    '<h6>Payment History</h6>': '<h6>{t("payment_history", "Payment History")}</h6>',
    '<th>Item</th>': '<th>{t("item", "Item")}</th>',
    '<th>Qty</th>': '<th>{t("qty", "Qty")}</th>',
    '<th>Price</th>': '<th>{t("price", "Price")}</th>',
    '<th>Total</th>': '<th>{t("total", "Total")}</th>',
    '<th>Receipt No</th>': '<th>{t("receipt_no", "Receipt No")}</th>',
    '<th>Method</th>': '<th>{t("method", "Method")}</th>',
    '<th>Amount</th>': '<th>{t("amount", "Amount")}</th>',
    'TOTAL DUE:': '{t("total_due", "TOTAL DUE:")}',
    'Total Paid:': '{t("total_paid", "Total Paid:")}',
    'SALES RECEIPT': '{t("sales_receipt", "SALES RECEIPT")}',
    'PURCHASES RECEIPT': '{t("purchases_receipt", "PURCHASES RECEIPT")}',
    'INVOICE': '{t("invoice", "INVOICE")}',
    '<Form.Label>Payment Account</Form.Label>': '<Form.Label>{t("payment_account", "Payment Account")}</Form.Label>',
    '<th>ITEM</th>': '<th>{t("item", "ITEM")}</th>',
}

safe_replace('frontend/src/pages/pos/Sales.jsx', pos_replacements)
safe_replace('frontend/src/pages/pos/Purchases.jsx', pos_replacements)

# Finance Modules specific missed
fin_replacements = {
    '<th>Type</th>': '<th>{t("type", "Type")}</th>',
    '<th>Partner</th>': '<th>{t("name", "Partner")}</th>',
    '<th>Amount Owed</th>': '<th>{t("balance", "Amount Owed")}</th>',
    '<th>Due Date</th>': '<th>{t("date", "Due Date")}</th>',
    '<th>Status</th>': '<th>{t("status", "Status")}</th>',
    '<th>Actions</th>': '<th>{t("actions", "Actions")}</th>',
    '<th>Account</th>': '<th>{t("financial_accounts", "Account")}</th>',
    '<th>Description</th>': '<th>{t("description", "Description")}</th>',
    '<th>Debit</th>': '<th>{t("debit", "Debit")}</th>',
    '<th>Credit</th>': '<th>{t("credit", "Credit")}</th>',
}
safe_replace('frontend/src/pages/finance/Debts.jsx', fin_replacements)
safe_replace('frontend/src/pages/finance/Transactions.jsx', fin_replacements)
safe_replace('frontend/src/pages/finance/FinancialReports.jsx', fin_replacements)

print("POS and Finance tables translated successfully!")
