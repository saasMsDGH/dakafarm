import os
import json

sw_path = 'frontend/public/locales/sw/translation.json'
en_path = 'frontend/public/locales/en/translation.json'

with open(sw_path, 'r', encoding='utf-8') as f:
    sw_data = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# 1. Update Locales with new keys
new_keys = {
    'general_ledger': {'en': 'General Ledger', 'sw': 'Leja Kuu'},
    'debtors_creditors': {'en': 'Debtors & Creditors', 'sw': 'Wadai & Wadaiwa'},
    'financial_reports': {'en': 'Financial Reports', 'sw': 'Ripoti za Fedha'},
    'system_administration': {'en': 'System Administration', 'sw': 'Utawala wa Mfumo'},
    'user_management': {'en': 'User Management', 'sw': 'Usimamizi wa Watumiaji'},
    'add_new_user': {'en': 'Add New User', 'sw': 'Ongeza Mtumiaji Mpya'},
    'edit_user_profile': {'en': 'Edit User Profile', 'sw': 'Hariri Wasifu wa Mtumiaji'},
    'change_password': {'en': 'Change Password', 'sw': 'Badilisha Nenosiri'},
    'status': {'en': 'Status', 'sw': 'Hali'},
    'actions': {'en': 'Actions', 'sw': 'Vitendo'},
    'name': {'en': 'Name', 'sw': 'Jina'},
    'email': {'en': 'Email', 'sw': 'Barua Pepe'},
    'phone': {'en': 'Phone', 'sw': 'Simu'},
    'role': {'en': 'Role', 'sw': 'Cheo'},
    'finance_dashboard': {'en': 'Finance Dashboard', 'sw': 'Dashibodi ya Fedha'},
    'cash_available': {'en': 'Cash Available', 'sw': 'Fedha Inayopatikana'},
    'profit_selected_period': {'en': 'Profit (Selected Period)', 'sw': 'Faida (Kipindi Kilichochaguliwa)'},
    'income_vs_expenses': {'en': 'Income vs Expenses (Selected Period)', 'sw': 'Mapato vs Matumizi (Kipindi Kilichochaguliwa)'},
    'where_money_goes': {'en': 'Where Our Money Goes (Expenses)', 'sw': 'Matumizi Yetu (Gharama)'},
    'financial_accounts': {'en': 'Financial Accounts', 'sw': 'Akaunti za Fedha'},
    'add_account': {'en': 'Add Financial Account', 'sw': 'Ongeza Akaunti ya Fedha'},
    'edit_account': {'en': 'Edit Financial Account', 'sw': 'Hariri Akaunti ya Fedha'}
}

for k, v in new_keys.items():
    sw_data[k] = v['sw']
    en_data[k] = v['en']

with open(sw_path, 'w', encoding='utf-8') as f:
    json.dump(sw_data, f, indent=2, ensure_ascii=False)

with open(en_path, 'w', encoding='utf-8') as f:
    json.dump(en_data, f, indent=2, ensure_ascii=False)

# 2. Update Sidebar.jsx
with open('frontend/src/components/Sidebar.jsx', 'r', encoding='utf-8') as f:
    sb = f.read()

sb = sb.replace('title="Dashboard"', 'title={t("dashboard", "Dashboard")}')
sb = sb.replace('title="General Ledger"', 'title={t("general_ledger", "General Ledger")}')
sb = sb.replace('title="Debtors & Creditors"', 'title={t("debtors_creditors", "Debtors & Creditors")}')
sb = sb.replace('title="Financial Reports"', 'title={t("financial_reports", "Financial Reports")}')
sb = sb.replace('title="System Administration"', 'title={t("system_administration", "System Administration")}')
sb = sb.replace('title="User Management"', 'title={t("user_management", "User Management")}')

with open('frontend/src/components/Sidebar.jsx', 'w', encoding='utf-8') as f:
    f.write(sb)

# 3. Update UsersManagement.jsx
with open('frontend/src/pages/admin/UsersManagement.jsx', 'r', encoding='utf-8') as f:
    um = f.read()

um = um.replace('<h4>Users Management</h4>', '<h4>{t("user_management", "Users Management")}</h4>')
um = um.replace('<Modal.Title>Add New User</Modal.Title>', '<Modal.Title>{t("add_new_user", "Add New User")}</Modal.Title>')
um = um.replace('<Modal.Title>Edit User Profile</Modal.Title>', '<Modal.Title>{t("edit_user_profile", "Edit User Profile")}</Modal.Title>')
um = um.replace('<Modal.Title>Change Password</Modal.Title>', '<Modal.Title>{t("change_password", "Change Password")}</Modal.Title>')
um = um.replace('<th className="border-bottom">Name</th>', '<th className="border-bottom">{t("name", "Name")}</th>')
um = um.replace('<th className="border-bottom">Email</th>', '<th className="border-bottom">{t("email", "Email")}</th>')
um = um.replace('<th className="border-bottom">Phone</th>', '<th className="border-bottom">{t("phone", "Phone")}</th>')
um = um.replace('<th className="border-bottom">Role</th>', '<th className="border-bottom">{t("role", "Role")}</th>')
um = um.replace('<th className="border-bottom">Status</th>', '<th className="border-bottom">{t("status", "Status")}</th>')
um = um.replace('<th className="border-bottom">Actions</th>', '<th className="border-bottom">{t("actions", "Actions")}</th>')

with open('frontend/src/pages/admin/UsersManagement.jsx', 'w', encoding='utf-8') as f:
    f.write(um)

# 4. Update FinanceDashboard.jsx
with open('frontend/src/pages/finance/FinanceDashboard.jsx', 'r', encoding='utf-8') as f:
    fd = f.read()

fd = fd.replace('<h4 className="mb-0">Finance Dashboard</h4>', '<h4 className="mb-0">{t("finance_dashboard", "Finance Dashboard")}</h4>')
fd = fd.replace('<h6 className="fw-extrabold mb-1">Cash Available</h6>', '<h6 className="fw-extrabold mb-1">{t("cash_available", "Cash Available")}</h6>')
fd = fd.replace('<h6 className="fw-extrabold mb-1">Customers Owe Us</h6>', '<h6 className="fw-extrabold mb-1">{t("customers_owe", "Customers Owe Us")}</h6>')
fd = fd.replace('<h6 className="fw-extrabold mb-1">We Owe Suppliers</h6>', '<h6 className="fw-extrabold mb-1">{t("we_owe", "We Owe Suppliers")}</h6>')
fd = fd.replace('<h6 className="fw-extrabold mb-1">Profit (Selected Period)</h6>', '<h6 className="fw-extrabold mb-1">{t("profit_selected_period", "Profit")}</h6>')
fd = fd.replace('<h5 className="mb-0">Income vs Expenses (Selected Period)</h5>', '<h5 className="mb-0">{t("income_vs_expenses", "Income vs Expenses")}</h5>')
fd = fd.replace('<h5 className="mb-0">Where Our Money Goes (Expenses)</h5>', '<h5 className="mb-0">{t("where_money_goes", "Where Our Money Goes")}</h5>')

with open('frontend/src/pages/finance/FinanceDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(fd)

print("Translation script executed!")
