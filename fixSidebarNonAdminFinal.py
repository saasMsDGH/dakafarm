with open("frontend/src/components/Sidebar.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

nav_inject = """                ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                  <>
                    <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                    <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    <Dropdown.Divider className="my-3 border-indigo" />
                    <CollapsableNavItem eventKey="pos_purchases/" title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>
                  </>"""

code = code.replace(
    """) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                    <>
                      <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </>""",
    nav_inject
)

with open("frontend/src/components/Sidebar.jsx", "w", encoding="utf-8") as f:
    f.write(code)
