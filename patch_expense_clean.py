import os

path = 'frontend/src/pages/pos/Expenses.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(r"{t(\'amount_paid\', \'Amount Paid\')}", "{t('amount_paid', 'Amount Paid')}")
content = content.replace(r"currentExpense.amount_paid || \'0.00\'", "currentExpense.amount_paid || '0.00'")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
