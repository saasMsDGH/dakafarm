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
    'first_name': 'Jina la Kwanza',
    'last_name': 'Jina la Mwisho',
    'phone_number': 'Namba ya Simu',
    'initial_password': 'Nenosiri la Awali',
    'new_password': 'Nenosiri Jipya',
    'submit': 'Wasilisha',
    'cancel': 'Ghairi',
    'general_ledger': 'Leja Kuu',
    'search_transactions': 'Tafuta Miamala...',
    'all_types': 'Aina Zote',
    'type': 'Aina',
    'ref_number': 'Namba ya Kumbukumbu',
    'description': 'Maelezo',
    'date': 'Tarehe',
    'credit': 'Kuingia (Credit)',
    'debit': 'Kutoka (Debit)',
    'debtors_creditors': 'Wadai & Wadaiwa',
    'financial_reports': 'Ripoti za Fedha',
    'search': 'Tafuta',
    'balance': 'Salio',
    'total': 'Jumla',
    'print': 'Chapisha',
    'export': 'Pakua',
    'income': 'Mapato',
    'expense': 'Matumizi',
    'asset': 'Mali',
    'liability': 'Deni',
    'equity': 'Mtaji',
    'users_management': 'Usimamizi wa Watumiaji'
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

# File replacer
def replace_in_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we need to add useTranslation
    if 'useTranslation' not in content:
        if 'import React' in content:
            content = content.replace('import React', "import { useTranslation } from 'react-i18next';\nimport React")
        # Add const { t } = useTranslation();
        content = content.replace('export default () => {', 'export default () => {\n  const { t } = useTranslation();')

    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# UsersManagement.jsx
replace_in_file('frontend/src/pages/admin/UsersManagement.jsx', {
    '<Form.Label>First Name</Form.Label>': '<Form.Label>{t("first_name", "First Name")}</Form.Label>',
    '<Form.Label>Last Name</Form.Label>': '<Form.Label>{t("last_name", "Last Name")}</Form.Label>',
    '<Form.Label>Email</Form.Label>': '<Form.Label>{t("email", "Email")}</Form.Label>',
    '<Form.Label>Phone Number</Form.Label>': '<Form.Label>{t("phone_number", "Phone Number")}</Form.Label>',
    '<Form.Label>Role</Form.Label>': '<Form.Label>{t("role", "Role")}</Form.Label>',
    '<Form.Label>Initial Password</Form.Label>': '<Form.Label>{t("initial_password", "Initial Password")}</Form.Label>',
    '<Form.Label>New Password</Form.Label>': '<Form.Label>{t("new_password", "New Password")}</Form.Label>',
    'placeholder="Search users..."': 'placeholder={t("search", "Search...")}',
})

# Transactions.jsx
replace_in_file('frontend/src/pages/finance/Transactions.jsx', {
    '<h4>General Ledger</h4>': '<h4>{t("general_ledger", "General Ledger")}</h4>',
    '<th className="border-bottom">Date</th>': '<th className="border-bottom">{t("date", "Date")}</th>',
    '<th className="border-bottom">Ref Number</th>': '<th className="border-bottom">{t("ref_number", "Ref Number")}</th>',
    '<th className="border-bottom">Account</th>': '<th className="border-bottom">{t("financial_accounts", "Account")}</th>',
    '<th className="border-bottom">Description</th>': '<th className="border-bottom">{t("description", "Description")}</th>',
    '<th className="border-bottom">Debit</th>': '<th className="border-bottom">{t("debit", "Debit")}</th>',
    '<th className="border-bottom">Credit</th>': '<th className="border-bottom">{t("credit", "Credit")}</th>',
    '<option value="">All Types</option>': '<option value="">{t("all_types", "All Types")}</option>',
    'placeholder="Search transactions..."': 'placeholder={t("search_transactions", "Search transactions...")}',
})

# Debts.jsx
replace_in_file('frontend/src/pages/finance/Debts.jsx', {
    '<h4>Debtors & Creditors</h4>': '<h4>{t("debtors_creditors", "Debtors & Creditors")}</h4>',
    '<th className="border-bottom">Type</th>': '<th className="border-bottom">{t("type", "Type")}</th>',
    '<th className="border-bottom">Partner</th>': '<th className="border-bottom">{t("name", "Partner")}</th>',
    '<th className="border-bottom">Amount Owed</th>': '<th className="border-bottom">{t("balance", "Amount Owed")}</th>',
    '<th className="border-bottom">Due Date</th>': '<th className="border-bottom">{t("date", "Due Date")}</th>',
    '<th className="border-bottom">Status</th>': '<th className="border-bottom">{t("status", "Status")}</th>',
    '<th className="border-bottom">Actions</th>': '<th className="border-bottom">{t("actions", "Actions")}</th>',
    '<option value="">All Types</option>': '<option value="">{t("all_types", "All Types")}</option>'
})

# FinancialReports.jsx
replace_in_file('frontend/src/pages/finance/FinancialReports.jsx', {
    '<h4>Financial Reports</h4>': '<h4>{t("financial_reports", "Financial Reports")}</h4>',
    '<h5>Profit & Loss (Income Statement)</h5>': '<h5>{t("profit_selected_period", "Profit & Loss")}</h5>',
    '<h5>Trial Balance</h5>': '<h5>Trial Balance</h5>',
    '<th className="border-bottom">Account</th>': '<th className="border-bottom">{t("financial_accounts", "Account")}</th>',
    '<th className="border-bottom text-end">Amount</th>': '<th className="border-bottom text-end">{t("balance", "Amount")}</th>',
    '<th className="border-bottom text-end">Debit</th>': '<th className="border-bottom text-end">{t("debit", "Debit")}</th>',
    '<th className="border-bottom text-end">Credit</th>': '<th className="border-bottom text-end">{t("credit", "Credit")}</th>',
    '<strong>Total Income:</strong>': '<strong>{t("income", "Total Income")}:</strong>',
    '<strong>Total Expenses:</strong>': '<strong>{t("expense", "Total Expenses")}:</strong>',
    '<strong>Net Profit:</strong>': '<strong>{t("profit_selected_period", "Net Profit")}:</strong>'
})

print("Completed translating Finance and HR files!")
