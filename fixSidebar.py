with open("frontend/src/components/Sidebar.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Add purchases section under pos_sales
nav_inject = """<NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </CollapsableNavItem>
                    <Dropdown.Divider className="my-3 border-indigo" />

                    <CollapsableNavItem eventKey="pos_purchases/" title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>
                    <Dropdown.Divider className="my-3 border-indigo" />"""

code = code.replace(
    """<NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </CollapsableNavItem>
                    <Dropdown.Divider className="my-3 border-indigo" />""",
    nav_inject
)

# And for the specific roles: admin gets everything.
# inventory_admin only gets inventory stuff.
# sell_manager gets sales + purchases maybe? The user said: "how we implemented past modules including most important thing RBAC".
# RBAC for Purchases & Expenses: "purchase and expences we will start with purchases". Which role handles purchases?
# Probably `admin` or a new role? Let's check `backend/app/api/v1/pos/router.py` to see what roles were used!

with open("frontend/src/components/Sidebar.jsx", "w", encoding="utf-8") as f:
    f.write(code)
