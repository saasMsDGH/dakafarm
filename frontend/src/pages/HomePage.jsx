import React, { useState, useEffect } from 'react';
import { Route, Switch, Redirect } from "react-router-dom";
import { Routes } from "../routes";

// pages
import DashboardOverview from "./dashboard/DashboardOverview";
import Settings from "./Settings";
import Signin from "./examples/Signin";
import NotFoundPage from "./examples/NotFound";
import ServerError from "./examples/ServerError";

// farm
import Houses from "./farm/Houses";
import Flocks from "./farm/Flocks";
import MedicationRecords from "./farm/MedicationRecords";
import VaccinationRecords from "./farm/VaccinationRecords";
import ProductionRecords from "./farm/ProductionRecords";
import MortalityRecords from "./farm/MortalityRecords";
import FeedRecords from "./farm/FeedRecords";
import FarmReport from "./farm/FarmReport";

// inventory
import Products from "./inventory/Products";
import ProductCategories from "./inventory/ProductCategories";
import StockMovements from "./inventory/StockMovements";
import InventoryStatus from "./inventory/InventoryStatus";


// hr
import Employees from "./hr/Employees";
import Payroll from "./hr/Payroll";


// assets
import AssetsList from "./assets/AssetsList";

// finance
import FinanceDashboard from "./finance/FinanceDashboard";
import AccountsList from "./finance/AccountsList";
import Transactions from "./finance/Transactions";
import Debts from "./finance/Debts";
import FinancialReports from "./finance/FinancialReports";

// admin
import UsersManagement from "./admin/UsersManagement";

// pos
import Customers from "./pos/Customers";
import Sales from "./pos/Sales";
import Suppliers from "./pos/Suppliers";
import Purchases from "./pos/Purchases";
import Expenses from "./pos/Expenses";

// reports
import FarmOperationsReport from "./reports/FarmOperationsReport";

// components
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Preloader from "../components/Preloader";

import { useAuth } from "../context/AuthContext";

const RouteWithLoader = ({ component: Component, ...rest }) => {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Route {...rest} render={props => ( <> <Preloader show={loaded ? false : true} /> <Component {...props} /> </> ) } />
  );
};

const RouteWithSidebar = ({ component: Component, roles, ...rest }) => {
  const { user } = useAuth();
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Route {...rest} render={props => {
      // Protect the route
      if (!user) {
        return <Redirect to={Routes.Signin.path} />;
      }

      // Smart redirect for roles that don't have access to the main dashboard
      const getDefaultRoute = (role) => {
        if (role === 'hr_manager' || role === 'hr_officer') return Routes.Employees.path;
        if (role === 'inventory_admin') return Routes.Products.path;
        if (role === 'sell_manager' || role === 'sell_officer') return Routes.Sales.path;
        if (role === 'Accountant') return Routes.FinanceDashboard.path;
        if (role === 'Farm Worker') return Routes.Flocks.path;
        return Routes.Settings.path; // Safe generic fallback
      };

      // Check RBAC roles
      if (roles && roles.length > 0) {
        const hasAccess = user.role_name === 'admin' || roles.includes(user.role_name);
        if (!hasAccess) {
          // If they are not allowed on this page, redirect to their designated home page
          return <Redirect to={getDefaultRoute(user.role_name)} />;
        }
      }

      return (
        <>
          <Preloader show={loaded ? false : true} />
          <Sidebar />

          <main className="content d-flex flex-column min-vh-100">
            <Navbar />
            <Component {...props} />
            <Footer />
          </main>
        </>
      );
    }}
    />
  );
};

export default () => (
  <Switch>
    <RouteWithLoader exact path={Routes.Signin.path} component={Signin} />
    <RouteWithLoader exact path={Routes.NotFound.path} component={NotFoundPage} />
    <RouteWithLoader exact path={Routes.ServerError.path} component={ServerError} />

    {/* pages */}
    <RouteWithSidebar exact path={Routes.DashboardOverview.path} component={DashboardOverview} roles={Routes.DashboardOverview.roles} />
    <RouteWithSidebar exact path={Routes.Settings.path} component={Settings} roles={Routes.Settings.roles} />
    
    {/* farm pages */}
    <RouteWithSidebar exact path={Routes.Houses.path} component={Houses} roles={Routes.Houses.roles} />
    <RouteWithSidebar exact path={Routes.Flocks.path} component={Flocks} roles={Routes.Flocks.roles} />
    <RouteWithSidebar exact path={Routes.Medications.path} component={MedicationRecords} roles={Routes.Medications.roles} />
    <RouteWithSidebar exact path={Routes.Vaccinations.path} component={VaccinationRecords} roles={Routes.Vaccinations.roles} />
    <RouteWithSidebar exact path={Routes.Productions.path} component={ProductionRecords} roles={Routes.Productions.roles} />
    <RouteWithSidebar exact path={Routes.Mortalities.path} component={MortalityRecords} roles={Routes.Mortalities.roles} />
    <RouteWithSidebar exact path={Routes.Feeds.path} component={FeedRecords} roles={Routes.Feeds.roles} />
    <RouteWithSidebar exact path={Routes.FarmReport.path} component={FarmReport} roles={Routes.FarmReport.roles} />

    {/* inventory pages */}
    <RouteWithSidebar exact path={Routes.Products.path} component={Products} roles={Routes.Products.roles} />
    <RouteWithSidebar exact path={Routes.ProductCategories.path} component={ProductCategories} roles={Routes.ProductCategories.roles} />
    <RouteWithSidebar exact path={Routes.StockMovements.path} component={StockMovements} roles={Routes.StockMovements.roles} />
    <RouteWithSidebar exact path={Routes.InventoryStatus.path} component={InventoryStatus} roles={Routes.InventoryStatus.roles} />

    
    {/* hr pages */}
    <RouteWithSidebar exact path={Routes.Employees.path} component={Employees} roles={Routes.Employees.roles} />
    <RouteWithSidebar exact path={Routes.Payroll.path} component={Payroll} roles={Routes.Payroll.roles} />

    
    {/* assets pages */}
    <RouteWithSidebar exact path={Routes.AssetsList.path} component={AssetsList} roles={Routes.AssetsList.roles} />
    <RouteWithSidebar exact path={Routes.FinanceDashboard.path} component={FinanceDashboard} roles={Routes.FinanceDashboard.roles} />
    <RouteWithSidebar exact path={Routes.FinanceAccounts.path} component={AccountsList} roles={Routes.FinanceAccounts.roles} />
    <RouteWithSidebar exact path={Routes.FinanceTransactions.path} component={Transactions} roles={Routes.FinanceTransactions.roles} />
    <RouteWithSidebar exact path={Routes.FinanceDebts.path} component={Debts} roles={Routes.FinanceDebts.roles} />
    <RouteWithSidebar exact path={Routes.FinanceReports.path} component={FinancialReports} roles={Routes.FinanceReports.roles} />

    {/* admin pages */}
    <RouteWithSidebar exact path={Routes.UsersManagement.path} component={UsersManagement} roles={Routes.UsersManagement.roles} />

    {/* pos pages */}
    <RouteWithSidebar exact path={Routes.Customers.path} component={Customers} roles={Routes.Customers.roles} />
    <RouteWithSidebar exact path={Routes.Sales.path} component={Sales} roles={Routes.Sales.roles} />
    <RouteWithSidebar exact path={Routes.Suppliers.path} component={Suppliers} roles={Routes.Suppliers.roles} />
    <RouteWithSidebar exact path={Routes.Purchases.path} component={Purchases} roles={Routes.Purchases.roles} />
    <RouteWithSidebar exact path={Routes.Expenses.path} component={Expenses} roles={Routes.Expenses.roles} />

    {/* reports pages */}
    <RouteWithSidebar exact path={Routes.ReportsOverview.path} component={FarmOperationsReport} roles={Routes.ReportsOverview.roles} />

    <Redirect to={Routes.NotFound.path} />
  </Switch>
);

