import os

paths = [
    'frontend/src/pages/admin/UsersManagement.jsx',
    'frontend/src/pages/finance/Transactions.jsx',
    'frontend/src/pages/finance/Debts.jsx',
    'frontend/src/pages/finance/FinancialReports.jsx',
    'frontend/src/pages/finance/AccountsList.jsx',
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Revert the bad filter
    content = content.replace('{t("filter", "Filter")}', 'Filter')
    
    # Correctly replace only the button text
    content = content.replace('>Filter<', '>{t("filter", "Filter")}<')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed!")
