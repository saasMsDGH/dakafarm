import React, { useState } from "react";
import SimpleBar from 'simplebar-react';
import { useLocation } from "react-router-dom";
import { CSSTransition } from 'react-transition-group';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBoxOpen, faChartPie, faSignOutAlt, faTimes, faWarehouse, faCashRegister, faUsers, faDesktop, faLandmark, faUserShield, faChartBar } from "@fortawesome/free-solid-svg-icons";
import { Nav, Badge, Image, Button, Dropdown, Accordion, Navbar } from '@themesberg/react-bootstrap';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { useAuth } from "../context/AuthContext";
import { Routes } from "../routes";
import ReactHero from "../assets/img/technologies/react-hero-logo.svg";

const Sidebar = (props) => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const location = useLocation();
  const { pathname } = location;
  const [show, setShow] = useState(false);
  const showClass = show ? "show" : "";

  const onCollapse = () => setShow(!show);

  const UserAvatar = ({ name }) => {
    const initial = name ? name.charAt(0).toUpperCase() : 'U';
    return (
      <div
        className="user-avatar lg-avatar rounded-circle d-flex align-items-center justify-content-center bg-secondary text-white fw-bold me-4 border-white"
        style={{ fontSize: '1.5rem', border: '2px solid white', width: '3rem', height: '3rem' }}
      >
        {initial}
      </div>
    );
  };

  const CollapsableNavItem = (props) => {
    const { eventKey, title, icon, children = null } = props;
    const defaultKey = pathname.indexOf(eventKey) !== -1 ? eventKey : "";

    return (
      <Accordion as={Nav.Item} defaultActiveKey={defaultKey}>
        <Accordion.Item eventKey={eventKey}>
          <Accordion.Button as={Nav.Link} className="d-flex justify-content-between align-items-center">
            <span>
              <span className="sidebar-icon"><FontAwesomeIcon icon={icon} /> </span>
              <span className="sidebar-text">{title}</span>
            </span>
          </Accordion.Button>
          <Accordion.Body className="multi-level">
            <Nav className="flex-column">
              {children}
            </Nav>
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    );
  };

  const NavItem = (props) => {
    const { title, link, external, target, icon, image, badgeText, badgeBg = "secondary", badgeColor = "primary" } = props;
    const classNames = badgeText ? "d-flex justify-content-start align-items-center justify-content-between" : "";
    const navItemClassName = link === pathname ? "active" : "";
    const linkProps = external ? { href: link } : { as: Link, to: link };

    return (
      <Nav.Item className={navItemClassName} onClick={() => setShow(false)}>
        <Nav.Link {...linkProps} target={target} className={classNames}>
          <span>
            {icon ? <span className="sidebar-icon"><FontAwesomeIcon icon={icon} /> </span> : null}
            {image ? <Image src={image} width={20} height={20} className="sidebar-icon svg-icon" /> : null}
            <span className="sidebar-text">{title}</span>
          </span>
          {badgeText ? (
            <Badge pill bg={badgeBg} text={badgeColor} className="badge-md notification-count ms-2">{badgeText}</Badge>
          ) : null}
        </Nav.Link>
      </Nav.Item>
    );
  };

  return (
    <>
      <style>
        {`
          .sidebar .nav-link {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .sidebar .sidebar-icon {
            font-size: 0.9rem !important;
            margin-right: 0.5rem !important;
          }
          .sidebar .accordion-button {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .sidebar .accordion-button::after {
            width: 0.75rem;
            height: 0.75rem;
            background-size: 0.75rem;
          }
          .sidebar .multi-level .nav-link {
            padding-left: 2.25rem !important;
            padding-top: 0.35rem !important;
            padding-bottom: 0.35rem !important;
          }
          .sidebar .sidebar-inner {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
          }
          .sidebar .nav-item {
            margin-bottom: 0.1rem;
          }
          .simplebar-content {
             overflow-x: hidden !important;
          }
        `}
      </style>

      

      <Navbar expand={false} collapseOnSelect variant="dark" className="navbar-theme-primary px-4 d-md-none d-print-none">
        <Navbar.Brand className="me-lg-5" as={Link} to={Routes.DashboardOverview.path}>
          <Image src={ReactHero} className="navbar-brand-light" />
        </Navbar.Brand>
        <Navbar.Toggle as={Button} aria-controls="main-navbar" onClick={onCollapse}>
          <span className="navbar-toggler-icon" />
        </Navbar.Toggle>
      </Navbar>
      <CSSTransition timeout={300} in={show} classNames="sidebar-transition">
        <SimpleBar className={`collapse ${showClass} sidebar d-md-block bg-primary text-white d-print-none`}>
          <div className="sidebar-inner px-4 pt-3">
            <div className="user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4">
              <div className="d-flex align-items-center">
                <UserAvatar name={user?.first_name} />
                <div className="d-block">
                  <h6>Hi, {user?.first_name}</h6>
                  <Button variant="secondary" size="xs" onClick={logout} className="text-dark">
                    <FontAwesomeIcon icon={faSignOutAlt} className="me-2" /> {t('logout', 'Sign Out')}
                  </Button>
                </div>
              </div>
              <Nav.Link className="collapse-close d-md-none" onClick={onCollapse}>
                <FontAwesomeIcon icon={faTimes} />
              </Nav.Link>
            </div>
            
            <Nav className="flex-column pt-3 pt-md-0">
              <NavItem title="AMAS FARM" link={Routes.DashboardOverview.path} image={ReactHero} />
              <Dropdown.Divider className="my-3 border-indigo" />
              
              {/* Core Dashboard - Visible if they have roles for DashboardOverview */}
              {(user?.role_name === 'admin' || Routes.DashboardOverview.roles.includes(user?.role_name)) && (
                <NavItem title={t('dashboard', 'Dashboard')} link={Routes.DashboardOverview.path} icon={faChartPie} />
              )}

              {/* Admin Subsystem */}
              {user?.role_name === 'admin' && (
                <CollapsableNavItem eventKey="admin/" title={t("system_administration", "System Administration")} icon={faUserShield}>
                  <NavItem title={t("user_management", "User Management")} link={Routes.UsersManagement?.path || '#'} />
                </CollapsableNavItem>
              )}

              {/* Farm Subsystem */}
              {(user?.role_name === 'admin' || ["Farm Manager", "Farm Worker"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="farm/" title={t('farm_management', 'Farm Management')} icon={faBoxOpen}>
                  <NavItem title={t('houses')} link={Routes.Houses?.path || '#'} />
                  <NavItem title={t('flocks')} link={Routes.Flocks?.path || '#'} />
                  <NavItem title={t('medications')} link={Routes.Medications?.path || '#'} />
                  <NavItem title={t('vaccinations')} link={Routes.Vaccinations?.path || '#'} />
                  <NavItem title={t('productions')} link={Routes.Productions?.path || '#'} />
                  <NavItem title={t('mortalities')} link={Routes.Mortalities?.path || '#'} />
                  <NavItem title={t('feeds')} link={Routes.Feeds?.path || '#'} />
                  {(user?.role_name === 'admin' || user?.role_name === 'Farm Manager') && (
                    <NavItem title={t('farm_report', 'Farm Report')} link={Routes.FarmReport?.path || '#'} />
                  )}
                </CollapsableNavItem>
              )}

              {/* Inventory Subsystem */}
              {(user?.role_name === 'admin' || ["inventory_admin", "Farm Manager", "Farm Worker", "sell_manager"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="inventory/" title={t('inventory_management', 'Inventory Management')} icon={faWarehouse}>
                  {(user?.role_name === 'admin' || ["inventory_admin", "Farm Manager"].includes(user?.role_name)) && (
                    <>
                      <NavItem title={t('products', 'Products')} link={Routes.Products?.path || '#'} />
                      <NavItem title={t('product_categories', 'Categories')} link={Routes.ProductCategories?.path || '#'} />
                    </>
                  )}
                  {(user?.role_name === 'admin' || ["inventory_admin", "Farm Manager", "Farm Worker"].includes(user?.role_name)) && (
                    <NavItem title={t('stock_movements', 'Stock Movements')} link={Routes.StockMovements?.path || '#'} />
                  )}
                  {(user?.role_name === 'admin' || ["inventory_admin", "Farm Manager", "sell_manager"].includes(user?.role_name)) && (
                    <NavItem title={t('inventory_status', 'Inventory Status')} link={Routes.InventoryStatus?.path || '#'} />
                  )}
                </CollapsableNavItem>
              )}
              
              {/* POS Sales Subsystem */}
              {(user?.role_name === 'admin' || ["sell_manager", "sell_officer"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="pos/" title={t('pos_sales', 'POS / Sales')} icon={faCashRegister}>
                  <NavItem title={t('customers', 'Customers')} link={Routes.Customers?.path || '#'} />
                  <NavItem title={t('sales', 'Sales')} link={Routes.Sales?.path || '#'} />
                </CollapsableNavItem>
              )}

              {/* POS Purchases / Expenses */}
              {(user?.role_name === 'admin' || ["sell_manager", "sell_officer", "inventory_admin", "finance_manager", "Accountant"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="pos_purchases/" title={t('pos_purchases', 'Purchases & Expenses')} icon={faCashRegister}>
                  {(user?.role_name === 'admin' || ["sell_manager", "sell_officer", "inventory_admin"].includes(user?.role_name)) && (
                    <>
                      <NavItem title={t('suppliers', 'Suppliers')} link={Routes.Suppliers?.path || '#'} />
                      <NavItem title={t('purchases', 'Purchases')} link={Routes.Purchases?.path || '#'} />
                    </>
                  )}
                  {(user?.role_name === 'admin' || ["finance_manager", "Accountant", "sell_manager"].includes(user?.role_name)) && (
                    <NavItem title={t('expenses', 'Expenses')} link={Routes.Expenses?.path || '#'} />
                  )}
                </CollapsableNavItem>
              )}

              {/* Reports Subsystem */}
              {(user?.role_name === 'admin' || ["finance_manager", "Farm Manager"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="reports/" title={t('reports', 'Reports')} icon={faChartBar}>
                  <NavItem title={t('reports_overview', 'Overview')} link={Routes.ReportsOverview?.path || '#'} />
                </CollapsableNavItem>
              )}
            
              {/* HR Subsystem */}
              {(user?.role_name === 'admin' || ["hr_manager", "hr_officer", "finance_manager"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="hr/" title={t('hr_management', 'HR Management')} icon={faUsers}>
                  {(user?.role_name === 'admin' || ["hr_manager", "hr_officer"].includes(user?.role_name)) && (
                    <NavItem title={t('employees', 'Employees')} link={Routes.Employees?.path || '#'} />
                  )}
                  {(user?.role_name === 'admin' || ["hr_manager", "finance_manager"].includes(user?.role_name)) && (
                    <NavItem title={t('payroll', 'Payroll')} link={Routes.Payroll?.path || '#'} />
                  )}
                </CollapsableNavItem>
              )}

              {/* Assets Subsystem */}
              {(user?.role_name === 'admin' || ["finance_manager", "Accountant", "Farm Manager"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="assets/" title={t('asset_management', 'Asset Management')} icon={faDesktop}>
                  <NavItem title={t('assets', 'Assets')} link={Routes.AssetsList?.path || '#'} />
                </CollapsableNavItem>
              )}

              {/* Finance Subsystem */}
              {(user?.role_name === 'admin' || ["finance_manager", "Accountant"].includes(user?.role_name)) && (
                <CollapsableNavItem eventKey="finance/" title={t('finance', 'Finance')} icon={faLandmark}>
                  <NavItem title={t("dashboard", "Dashboard")} link={Routes.FinanceDashboard?.path || '#'} />
                  <NavItem title={t('financial_accounts', 'Accounts')} link={Routes.FinanceAccounts?.path || '#'} />
                  <NavItem title={t("general_ledger", "General Ledger")} link={Routes.FinanceTransactions?.path || '#'} />
                  <NavItem title={t("debtors_creditors", "Debtors & Creditors")} link={Routes.FinanceDebts?.path || '#'} />
                  <NavItem title={t("financial_reports", "Financial Reports")} link={Routes.FinanceReports?.path || '#'} />
                </CollapsableNavItem>
              )}

              <Dropdown.Divider className="my-3 border-indigo" />
            </Nav>

          </div>
        </SimpleBar>
      </CSSTransition>
    </>
  );
};

export default Sidebar;


