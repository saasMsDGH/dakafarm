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

    content = content.replace('>Save<', '>{t("save_all", "Save")}<')
    content = content.replace('>Save Changes<', '>{t("save_all", "Save Changes")}<')
    content = content.replace('>Close<', '>{t("cancel", "Close")}<')
    content = content.replace('>Cancel<', '>{t("cancel", "Cancel")}<')
    content = content.replace('>Delete<', '>{t("delete", "Delete")}<')
    content = content.replace('>Update<', '>{t("update", "Update")}<')
    content = content.replace('Filter', '{t("filter", "Filter")}')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Buttons translated!")
