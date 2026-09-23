import codecs

# 1. Update routes.js
routes_file = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/routes.js'
with codecs.open(routes_file, 'r', 'utf-8') as f:
    routes_content = f.read()

# DashboardOverview
routes_content = routes_content.replace(
    'DashboardOverview: { path: "/", roles: ["admin", "finance_manager", "Farm Manager"] }',
    'DashboardOverview: { path: "/", roles: ["admin", "Farm Manager"] }'
)
# Expenses
routes_content = routes_content.replace(
    'Expenses: { path: "/pos/expenses", roles: ["admin", "finance_manager", "Accountant", "sell_manager"] }',
    'Expenses: { path: "/pos/expenses", roles: ["admin", "Accountant", "sell_manager"] }'
)
# Payroll
routes_content = routes_content.replace(
    'Payroll: { path: "/hr/payroll", roles: ["admin", "hr_manager", "finance_manager"] }',
    'Payroll: { path: "/hr/payroll", roles: ["admin", "hr_manager"] }'
)
# AssetsList
routes_content = routes_content.replace(
    'AssetsList: { path: "/assets/list", roles: ["admin", "finance_manager", "Accountant", "Farm Manager"] }',
    'AssetsList: { path: "/assets/list", roles: ["admin", "Accountant", "Farm Manager"] }'
)
# ReportsOverview
routes_content = routes_content.replace(
    'ReportsOverview: { path: "/reports", roles: ["admin", "finance_manager", "Farm Manager"] }',
    'ReportsOverview: { path: "/reports", roles: ["admin", "Farm Manager"] }'
)

with codecs.open(routes_file, 'w', 'utf-8') as f:
    f.write(routes_content)

# 2. Update HomePage.jsx
home_file = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/HomePage.jsx'
with codecs.open(home_file, 'r', 'utf-8') as f:
    home_content = f.read()

home_content = home_content.replace(
    "if (role === 'Accountant') return Routes.FinanceDashboard.path;",
    "if (role === 'Accountant' || role === 'finance_manager') return Routes.FinanceDashboard.path;"
)

with codecs.open(home_file, 'w', 'utf-8') as f:
    f.write(home_content)


# 3. Update Sidebar.jsx
sidebar_file = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/components/Sidebar.jsx'
with codecs.open(sidebar_file, 'r', 'utf-8') as f:
    sidebar_content = f.read()

# POS Purchases
sidebar_content = sidebar_content.replace(
    '["sell_manager", "sell_officer", "inventory_admin", "finance_manager", "Accountant"].includes(user?.role_name)',
    '["sell_manager", "sell_officer", "inventory_admin", "Accountant"].includes(user?.role_name)'
)
sidebar_content = sidebar_content.replace(
    '["finance_manager", "Accountant", "sell_manager"].includes(user?.role_name)',
    '["Accountant", "sell_manager"].includes(user?.role_name)'
)
# Reports
sidebar_content = sidebar_content.replace(
    '["finance_manager", "Farm Manager"].includes(user?.role_name)',
    '["Farm Manager"].includes(user?.role_name)'
)
# HR
sidebar_content = sidebar_content.replace(
    '["hr_manager", "hr_officer", "finance_manager"].includes(user?.role_name)',
    '["hr_manager", "hr_officer"].includes(user?.role_name)'
)
sidebar_content = sidebar_content.replace(
    '["hr_manager", "finance_manager"].includes(user?.role_name)',
    '["hr_manager"].includes(user?.role_name)'
)
# Assets
sidebar_content = sidebar_content.replace(
    '["finance_manager", "Accountant", "Farm Manager"].includes(user?.role_name)',
    '["Accountant", "Farm Manager"].includes(user?.role_name)'
)

with codecs.open(sidebar_file, 'w', 'utf-8') as f:
    f.write(sidebar_content)

print("Removed finance_manager from unwanted modules successfully!")
