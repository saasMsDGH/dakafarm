import re

with open("frontend/src/components/Sidebar.jsx", "r") as f:
    code = f.read()

# Add icons
code = code.replace(
    "import { faChartPie, faCog, faSignOutAlt, faTimes, faBoxOpen, faWarehouse, faLanguage } from '@fortawesome/free-solid-svg-icons';", 
    "import { faChartPie, faCog, faSignOutAlt, faTimes, faBoxOpen, faWarehouse, faLanguage, faCashRegister } from '@fortawesome/free-solid-svg-icons';"
)

# Admin POS menu
admin_pos_menu = """                  <CollapsableNavItem eventKey="inventory/" title={t('inventory_management')} icon={faWarehouse}>
                    <NavItem title={t('products', 'Products')} link={Routes.Products?.path || '#'} />
                    <NavItem title={t('product_categories', 'Categories')} link={Routes.ProductCategories?.path || '#'} />
                    <NavItem title={t('stock_movements', 'Stock Movements')} link={Routes.StockMovements?.path || '#'} />
                    <NavItem title={t('inventory_status', 'Inventory Status')} link={Routes.InventoryStatus?.path || '#'} />
                  </CollapsableNavItem>
                  <Dropdown.Divider className="my-3 border-indigo" />
                  
                  <CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
                    <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                    <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                  </CollapsableNavItem>
                  <Dropdown.Divider className="my-3 border-indigo" />"""

code = re.sub(
    r'                  <CollapsableNavItem eventKey="inventory/".*?<Dropdown\.Divider className="my-3 border-indigo" />', 
    admin_pos_menu, 
    code, 
    flags=re.DOTALL
)

# Inventory / POS user roles
pos_roles = """                ) : user?.role_name === 'inventory_admin' ? (
                  <>
                    <NavItem title={t('products', 'Products')} link={Routes.Products?.path || '#'} />
                    <NavItem title={t('product_categories', 'Categories')} link={Routes.ProductCategories?.path || '#'} />
                    <NavItem title={t('stock_movements', 'Stock Movements')} link={Routes.StockMovements?.path || '#'} />
                    <NavItem title={t('inventory_status', 'Inventory Status')} link={Routes.InventoryStatus?.path || '#'} />
                  </>
                ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                  <>
                    <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                    <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                  </>
                ) : ("""

code = re.sub(
    r"\s+\) : user\?\.role_name === 'inventory_admin' \? \(\s*<>\s*<NavItem title=\{t\('products', 'Products'\)\}.*?</>\s*\) : \(", 
    pos_roles, 
    code, 
    flags=re.DOTALL
)

with open("frontend/src/components/Sidebar.jsx", "w") as f:
    f.write(code)
