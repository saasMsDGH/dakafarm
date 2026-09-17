with open("frontend/src/pages/HomePage.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Imports
code = code.replace(
    'import Sales from "./pos/Sales";',
    'import Sales from "./pos/Sales";\nimport Suppliers from "./pos/Suppliers";\nimport Purchases from "./pos/Purchases";\nimport Expenses from "./pos/Expenses";'
)

# Routes
route_inject = """<RouteWithSidebar exact path={Routes.Customers.path} component={Customers} />
    <RouteWithSidebar exact path={Routes.Sales.path} component={Sales} />
    <RouteWithSidebar exact path={Routes.Suppliers.path} component={Suppliers} />
    <RouteWithSidebar exact path={Routes.Purchases.path} component={Purchases} />
    <RouteWithSidebar exact path={Routes.Expenses.path} component={Expenses} />"""
code = code.replace(
    '<RouteWithSidebar exact path={Routes.Customers.path} component={Customers} />\n    <RouteWithSidebar exact path={Routes.Sales.path} component={Sales} />',
    route_inject
)

with open("frontend/src/pages/HomePage.jsx", "w", encoding="utf-8") as f:
    f.write(code)
