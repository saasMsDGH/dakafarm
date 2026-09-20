import os
import json

path = 'frontend/src/pages/finance/Debts.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('Receivables (Customers)', '{t("receivables_customers", "Receivables (Customers)")}')
content = content.replace('Payables (Suppliers)', '{t("payables_suppliers", "Payables (Suppliers)")}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

path = 'frontend/src/pages/finance/FinancialReports.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('Profit & Loss', '{t("profit_loss", "Profit & Loss")}')
content = content.replace('Trial Balance', '{t("trial_balance", "Trial Balance")}')
content = content.replace('Cash Flow Statement', '{t("cash_flow", "Cash Flow")}')
content = content.replace('Balance Sheet', '{t("balance_sheet", "Balance Sheet")}')
content = content.replace('Apply Dates', '{t("apply", "Apply Dates")}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Add translations to dictionary
sw_path = 'frontend/public/locales/sw/translation.json'
with open(sw_path, 'r', encoding='utf-8') as f:
    sw_data = json.load(f)

sw_data['receivables_customers'] = 'Wadaiwa (Wateja)'
sw_data['payables_suppliers'] = 'Wadai (Wasambazaji)'
sw_data['profit_loss'] = 'Faida na Hasara'
sw_data['trial_balance'] = 'Mizania ya Majaribio'
sw_data['cash_flow'] = 'Mtiririko wa Fedha'
sw_data['balance_sheet'] = 'Mizania'
sw_data['apply'] = 'Weka'

with open(sw_path, 'w', encoding='utf-8') as f:
    json.dump(sw_data, f, indent=2, ensure_ascii=False)

print("Tabs translated!")
