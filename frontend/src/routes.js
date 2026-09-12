export const Routes = {
    // Core
    DashboardOverview: { path: "/" },
    Signin: { path: "/examples/sign-in" },
    NotFound: { path: "/examples/404" },
    ServerError: { path: "/examples/500" },

    // User Subsystem
    Settings: { path: "/settings" }, // Profile & Settings

    // Farm Subsystem
    Houses: { path: "/farm/houses" },
    Flocks: { path: "/farm/flocks" },
    Medications: { path: "/farm/medications" },
    Vaccinations: { path: "/farm/vaccinations" },
    Productions: { path: "/farm/productions" },
    Mortalities: { path: "/farm/mortalities" },
    Feeds: { path: "/farm/feeds" },
    FarmReport: { path: "/farm/report" },

    // Inventory Subsystem
    Products: { path: "/inventory/products" },
    ProductCategories: { path: "/inventory/categories" },
    StockMovements: { path: "/inventory/stock-movements" },
    InventoryStatus: { path: "/inventory/status" },

    // POS Subsystem
    Customers: { path: "/pos/customers" },
    Sales: { path: "/pos/sales" },
};

