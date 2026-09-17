with open("frontend/src/components/Sidebar.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

purchases_block = """
                    <CollapsableNavItem eventKey="pos_purchases/" title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>"""

# Admin
code = re.sub(
    r'(<CollapsableNavItem eventKey="pos/" title=\{t\(\'pos_sales\', \'POS / Sales\'\)\} icon=\{faCashRegister\}>\s*<NavItem title=\{t\(\'customers\', \'Customers\'\)\} link=\{Routes\.Customers\?\.path \|\| \'#\'\} />\s*<NavItem title=\{t\(\'sales\', \'Sales\'\)\} link=\{Routes\.Sales\?\.path \|\| \'#\'\} />\s*</CollapsableNavItem>)',
    r'\1' + purchases_block,
    code
)

# Sell manager / officer
code = re.sub(
    r'(\)\s*:\s*user\?\.role_name === \'sell_manager\' \|\| user\?\.role_name === \'sell_officer\' \?\s*\(\s*<>\s*<NavItem title=\{t\(\'customers\', \'Customers\'\)\} link=\{Routes\.Customers\?\.path \|\| \'#\'\} />\s*<NavItem title=\{t\(\'sales\', \'Sales\'\)\} link=\{Routes\.Sales\?\.path \|\| \'#\'\} />)',
    r'\1' + purchases_block,
    code
)

with open("frontend/src/components/Sidebar.jsx", "w", encoding="utf-8") as f:
    f.write(code)
