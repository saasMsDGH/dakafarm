
import os

filepath = rfrontend/src/components/Sidebar.jsx

with open(filepath, r, encoding=utf-8) as f:
    content = f.read()

old = "                ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                  <>
                    <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                    <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    <CollapsableNavItem eventKey=pos_purchases/ title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>
                  </>
                ) : (
                <>
                  <NavItem title={t('houses')} link={Routes.Houses?.path || '#'} />
                  <NavItem title={t('flocks')} link={Routes.Flocks?.path || '#'} />
                  <NavItem title={t('medications')} link={Routes.Medications?.path || '#'} />
                  <NavItem title={t('vaccinations')} link={Routes.Vaccinations?.path || '#'} />
                  <NavItem title={t('productions')} link={Routes.Productions?.path || '#'} />
                  <NavItem title={t('mortalities')} link={Routes.Mortalities?.path || '#'} />
                  <NavItem title={t('feeds')} link={Routes.Feeds?.path || '#'} />
                  <NavItem title={t('farm_report', 'Farm Report')} link={Routes.FarmReport?.path || '#'} />
                </>
              )}"

new = "                ) : user?.role_name === 'sell_manager' || user?.role_name === 'sell_officer' ? (
                  <>
                    <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                    <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                    <CollapsableNavItem eventKey=pos_purchases/ title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                      <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                    </CollapsableNavItem>
                  </>
                ) : user?.role_name === 'finance_manager' || user?.role_name === 'finance_officer' ? (
                  <>
                    <CollapsableNavItem eventKey=finance/ title={t('finance', 'Finance')} icon={faLandmark}>
                      <NavItem title=Dashboard link={Routes.FinanceDashboard?.path || '#'} />
                      <NavItem title={t('financial_accounts', 'Accounts')} link={Routes.FinanceAccounts?.path || '#'} />
                      <NavItem title=General Ledger link={Routes.FinanceTransactions?.path || '#'} />
                      <NavItem title=Debtors & Creditors link={Routes.FinanceDebts?.path || '#'} />
                      <NavItem title=Financial Reports link={Routes.FinanceReports?.path || '#'} />
                    </CollapsableNavItem>
                  </>
                ) : user?.role_name === 'farm_manager' || user?.role_name === 'farm_officer' ? (
                  <>
                    <NavItem title={t('houses')} link={Routes.Houses?.path || '#'} />
                    <NavItem title={t('flocks')} link={Routes.Flocks?.path || '#'} />
                    <NavItem title={t('medications')} link={Routes.Medications?.path || '#'} />
                    <NavItem title={t('vaccinations')} link={Routes.Vaccinations?.path || '#'} />
                    <NavItem title={t('productions')} link={Routes.Productions?.path || '#'} />
                    <NavItem title={t('mortalities')} link={Routes.Mortalities?.path || '#'} />
                    <NavItem title={t('feeds')} link={Routes.Feeds?.path || '#'} />
                    <NavItem title={t('farm_report', 'Farm Report')} link={Routes.FarmReport?.path || '#'} />
                  </>
                ) : null}"

if old in content:
    content = content.replace(old, new)
    with open(filepath, w, encoding=utf-8) as f:
        f.write(content)
    print(Replaced successfully)
else:
    print(String not found)

