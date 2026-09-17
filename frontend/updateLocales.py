import json
import os

files = {
    "public/locales/en/translation.json": {
        "suppliers": "Suppliers",
        "purchases": "Purchases",
        "expenses": "Expenses",
        "pos_purchases": "Purchases & Expenses",
        "contact_person": "Contact Person",
        "expense_number": "Expense No.",
        "expense_date": "Expense Date",
        "payment_method": "Payment Method",
        "cash": "Cash",
        "bank": "Bank",
        "mobile_money": "Mobile Money",
        "new_selling_price": "New Selling Price",
        "add_supplier": "Add Supplier"
    },
    "public/locales/sw/translation.json": {
        "suppliers": "Wauzaji (Suppliers)",
        "purchases": "Manunuzi",
        "expenses": "Matumizi",
        "pos_purchases": "Manunuzi & Matumizi",
        "contact_person": "Mhusika",
        "expense_number": "Namba ya Matumizi",
        "expense_date": "Tarehe ya Matumizi",
        "payment_method": "Njia ya Malipo",
        "cash": "Taslimu",
        "bank": "Benki",
        "mobile_money": "Tigo Pesa/M-Pesa/Airtel",
        "new_selling_price": "Bei Mpya ya Kuuzia",
        "add_supplier": "Ongeza Muuzaji"
    }
}

for path, new_data in files.items():
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.update(new_data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
