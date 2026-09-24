export const Routes = {
    // Core (All roles)
    DashboardOverview: { path: "/", roles: ["admin", "Farm Manager"] },
    Signin: { path: "/examples/sign-in", roles: [] },
    NotFound: { path: "/examples/404", roles: [] },
    ServerError: { path: "/examples/500", roles: [] },
    Settings: { path: "/settings", roles: ["admin", "finance_manager", "Farm Manager", "Accountant", "hr_officer", "Farm Worker", "inventory_admin", "sell_manager", "sell_officer", "hr_manager"] },

    // Farm Subsystem
    Houses: { path: "/farm/houses", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Flocks: { path: "/farm/flocks", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Medications: { path: "/farm/medications", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Vaccinations: { path: "/farm/vaccinations", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Productions: { path: "/farm/productions", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Mortalities: { path: "/farm/mortalities", roles: ["admin", "Farm Manager", "Farm Worker"] },
    Feeds: { path: "/farm/feeds", roles: ["admin", "Farm Manager", "Farm Worker"] },
    FarmReport: { path: "/farm/report", roles: ["admin", "Farm Manager"] },

    // Inventory Subsystem
    Products: { path: "/inventory/products", roles: ["admin", "inventory_admin", "Farm Manager"] },
    ProductCategories: { path: "/inventory/categories", roles: ["admin", "inventory_admin", "Farm Manager"] },
    StockMovements: { path: "/inventory/stock-movements", roles: ["admin", "inventory_admin", "Farm Manager", "Farm Worker"] },
    InventoryStatus: { path: "/inventory/status", roles: ["admin", "inventory_admin", "Farm Manager", "sell_manager"] },

    // POS Subsystem
    Customers: { path: "/pos/customers", roles: ["admin", "sell_manager", "sell_officer"] },
    Sales: { path: "/pos/sales", roles: ["admin", "sell_manager", "sell_officer"] },
    Suppliers: { path: "/pos/suppliers", roles: ["admin", "sell_manager", "sell_officer", "inventory_admin"] },
    Purchases: { path: "/pos/purchases", roles: ["admin", "sell_manager", "sell_officer", "inventory_admin"] },
    Expenses: { path: "/pos/expenses", roles: ["admin", "Accountant", "sell_manager"] },

    // HR Subsystem
    Employees: { path: "/hr/employees", roles: ["admin", "hr_manager", "hr_officer"] },
    Payroll: { path: "/hr/payroll", roles: ["admin", "hr_manager"] },

    // Assets Subsystem
    AssetsList: { path: "/assets/list", roles: ["admin", "Accountant", "Farm Manager"] },

    // Finance Subsystem
    FinanceDashboard: { path: "/finance/dashboard", roles: ["admin", "finance_manager", "Accountant"] },
    FinanceAccounts: { path: "/finance/accounts", roles: ["admin", "finance_manager", "Accountant"] },
    FinanceTransactions: { path: "/finance/transactions", roles: ["admin", "finance_manager", "Accountant"] },
    FinanceDebts: { path: "/finance/debts", roles: ["admin", "finance_manager", "Accountant"] },
    FinanceReports: { path: "/finance/reports", roles: ["admin", "finance_manager", "Accountant"] },

    // Admin Subsystem
    UsersManagement: { path: "/admin/users", roles: ["admin"] },

    // Reports Subsystem - The Master Dashboard
    ReportsOverview: { path: "/reports", roles: ["admin", "Farm Manager"] },
};
