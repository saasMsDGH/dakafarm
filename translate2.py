import os

def replace_in_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements.items():
        content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

replace_in_file('frontend/src/pages/finance/AccountsList.jsx', {
    '<h4>Financial Accounts</h4>': '<h4>{t("financial_accounts", "Financial Accounts")}</h4>',
    "isEdit ? 'Edit Financial Account' : 'Add Financial Account'": "isEdit ? t('edit_account', 'Edit Financial Account') : t('add_account', 'Add Financial Account')"
})

print("Accounts translated!")
