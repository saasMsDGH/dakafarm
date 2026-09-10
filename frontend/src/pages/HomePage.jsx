import React, { useState, useEffect } from 'react';
import { Route, Switch, Redirect } from "react-router-dom";
import { Routes } from "../routes";

// pages
import DashboardOverview from "./dashboard/DashboardOverview";
import Settings from "./Settings";
import Signin from "./examples/Signin";
import NotFoundPage from "./examples/NotFound";
import ServerError from "./examples/ServerError";

import Houses from "./farm/Houses";
import Flocks from "./farm/Flocks";
import MedicationRecords from "./farm/MedicationRecords";
import VaccinationRecords from "./farm/VaccinationRecords";
import ProductionRecords from "./farm/ProductionRecords";
import MortalityRecords from "./farm/MortalityRecords";
import FeedRecords from "./farm/FeedRecords";

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
    <RouteWithSidebar exact path={Routes.Houses.path} component={Houses} />
    <RouteWithSidebar exact path={Routes.Flocks.path} component={Flocks} />
    <RouteWithSidebar exact path={Routes.Medications.path} component={MedicationRecords} />
    <RouteWithSidebar exact path={Routes.Vaccinations.path} component={VaccinationRecords} />
    <RouteWithSidebar exact path={Routes.Productions.path} component={ProductionRecords} />
    <RouteWithSidebar exact path={Routes.Mortalities.path} component={MortalityRecords} />
    <RouteWithSidebar exact path={Routes.Feeds.path} component={FeedRecords} />

    <Redirect to={Routes.NotFound.path} />
  </Switch>
);
