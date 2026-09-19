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

// pos
import Customers from "./pos/Customers";
import Sales from "./pos/Sales";
import Suppliers from "./pos/Suppliers";
import Purchases from "./pos/Purchases";
import Expenses from "./pos/Expenses";

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

const RouteWithSidebar = ({ component: Component, ...rest }) => {
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

      return (
        <>
          <Preloader show={loaded ? false : true} />
          <Sidebar />

          <main className="content">
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
    <RouteWithSidebar exact path={Routes.DashboardOverview.path} component={DashboardOverview} />
    <RouteWithSidebar exact path={Routes.Settings.path} component={Settings} />
    
    {/* farm pages */}
    <RouteWithSidebar exact path={Routes.Houses.path} component={Houses} />
    <RouteWithSidebar exact path={Routes.Flocks.path} component={Flocks} />
    <RouteWithSidebar exact path={Routes.Medications.path} component={MedicationRecords} />
    <RouteWithSidebar exact path={Routes.Vaccinations.path} component={VaccinationRecords} />
    <RouteWithSidebar exact path={Routes.Productions.path} component={ProductionRecords} />
    <RouteWithSidebar exact path={Routes.Mortalities.path} component={MortalityRecords} />
    <RouteWithSidebar exact path={Routes.Feeds.path} component={FeedRecords} />
    <RouteWithSidebar exact path={Routes.FarmReport.path} component={FarmReport} />

    {/* inventory pages */}
    <RouteWithSidebar exact path={Routes.Products.path} component={Products} />
    <RouteWithSidebar exact path={Routes.ProductCategories.path} component={ProductCategories} />
    <RouteWithSidebar exact path={Routes.StockMovements.path} component={StockMovements} />
    <RouteWithSidebar exact path={Routes.InventoryStatus.path} component={InventoryStatus} />

    
    {/* hr pages */}
    <RouteWithSidebar exact path={Routes.Employees.path} component={Employees} />
    <RouteWithSidebar exact path={Routes.Payroll.path} component={Payroll} />

    
    {/* assets pages */}
    <RouteWithSidebar exact path={Routes.AssetsList.path} component={AssetsList} />
    <RouteWithSidebar exact path={Routes.FinanceDashboard.path} component={FinanceDashboard} />
    <RouteWithSidebar exact path={Routes.FinanceAccounts.path} component={AccountsList} />
    <RouteWithSidebar exact path={Routes.FinanceTransactions.path} component={Transactions} />
    <RouteWithSidebar exact path={Routes.FinanceDebts.path} component={Debts} />
    <RouteWithSidebar exact path={Routes.FinanceReports.path} component={FinancialReports} />

    {/* pos pages */}
    <RouteWithSidebar exact path={Routes.Customers.path} component={Customers} />
    <RouteWithSidebar exact path={Routes.Sales.path} component={Sales} />
    <RouteWithSidebar exact path={Routes.Suppliers.path} component={Suppliers} />
    <RouteWithSidebar exact path={Routes.Purchases.path} component={Purchases} />
    <RouteWithSidebar exact path={Routes.Expenses.path} component={Expenses} />

    <Redirect to={Routes.NotFound.path} />
  </Switch>
);
