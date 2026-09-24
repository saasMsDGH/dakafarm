import codecs

file_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/pos/Sales.jsx'

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# Replace exact matches
replacements = {
    # 1. Total Paid
    '{t("total_paid", "Total Paid:")}': '',
    
    # 2. Title Type (the single quotes and curly braces)
    "'{t(\"sales_receipt\", \"SALES RECEIPT\")}'": 't("sales_receipt", "SALES RECEIPT")',
    "'{t(\"invoice\", \"INVOICE\")}'": 't("invoice", "INVOICE")',
    
    # 3. Item
    '<th>{t("item", "ITEM")}</th>': '<th></th>',
    
    # 4. Total Due
    '<td>{t("total_due", "TOTAL DUE:")}</td>': '<td></td>',
    
    # 5. Receipt Start/End
    '*** START OF {t("sales_receipt", "SALES RECEIPT")} ***': '*** START OF  ***',
    '*** END OF {t("sales_receipt", "SALES RECEIPT")} ***': '*** END OF  ***',
}

for old_str, new_str in replacements.items():
    content = content.replace(old_str, new_str)

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)

print("Replacements completed successfully!")
