import codecs

file_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/pos/Sales.jsx'

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# I will fix what Powershell broke, and also replace properly.

# Fix the broken empty start/end
content = content.replace('*** START OF  ***', '*** START OF ${t("sales_receipt", "SALES RECEIPT")} ***')
content = content.replace('*** END OF  ***', '*** END OF ${t("sales_receipt", "SALES RECEIPT")} ***')

# Fix total_paid which also probably got corrupted to just empty string or similar?
# Wait, let's see what was injected for total_paid.
content = content.replace('             ${parseFloat', '            ${t("total_paid", "Total Paid:")} ${parseFloat')

# Fix Item
content = content.replace('<th></th>', '<th>${t("item", "ITEM")}</th>')
content = content.replace('<td></td>', '<td>${t("total_due", "TOTAL DUE:")}</td>')

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)

print("Restored Powershell corruption and applied correct formatting")
