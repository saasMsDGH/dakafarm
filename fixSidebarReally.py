with open("frontend/src/components/Sidebar.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# We will inject this standard block for both Admin and Sales roles
purchases_block = """
                    <CollapsableNavItem eventKey="pos_purchases/" title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>"""

# Fix admin: add it right after pos_sales
# Wait, for admin, it's currently:
# <CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
#   <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
#   <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
# </CollapsableNavItem>
# <Dropdown.Divider className="my-3 border-indigo" />
code = code.replace(
    """<CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
                      <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </CollapsableNavItem>""",
    """<CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
                      <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </CollapsableNavItem>""" + purchases_block
)

# Fix sell_manager/sell_officer
# Currently:
# ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
#   <>
#     <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
#     <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
#   </>
# )
code = code.replace(
    """                  ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                    <>
                      <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                      <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    </>""",
    """                  ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                    <>
                      <CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
                        <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                        <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                      </CollapsableNavItem>
""" + purchases_block + """
                    </>"""
)

with open("frontend/src/components/Sidebar.jsx", "w", encoding="utf-8") as f:
    f.write(code)
