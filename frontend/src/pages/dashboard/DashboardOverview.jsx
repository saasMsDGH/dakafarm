import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faEgg, 
  faCrow, 
  faMoneyBillWave, 
  faChartLine, 
  faUsers, 
  faShoppingCart, 
  faExclamationTriangle,
  faCheckCircle
} from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Spinner, Table, Badge } from '@themesberg/react-bootstrap';
import { api } from "../../api/axios";
import moment from "moment";
import Swal from 'sweetalert2';
// Recharts for graphs
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from "recharts";

export default () => {
  const [loading, setLoading] = useState(true);
  
  // Farm State
  const [farmData, setFarmData] = useState({
    totalBirds: 0,
    todayEggs: 0,
    todayMortality: 0,
    monthEggs: 0,
  });

  // Finance & POS State (Step 3)
  const [financeData, setFinanceData] = useState({ 
    cash: 0, 
    profit: 0, 
    todaySales: 0,
    receivables: 0,
    payables: 0
  });

  const [hrData, setHrData] = useState({ activeUsers: 0 });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Date formatting for API queries
      const today = moment().format("YYYY-MM-DD");
      const firstDayOfMonth = moment().startOf('month').format("YYYY-MM-DD");
      const todayStart = moment().startOf('day').toISOString();
      const todayEnd = moment().endOf('day').toISOString();

      // === 1. FETCH FARM DATA (Step 2) ===
      const flocksRes = await api.get('/api/v1/farm/flocks/?limit=100');
      const activeFlocks = flocksRes.data.items || [];
      const totalBirds = activeFlocks.reduce((sum, flock) => sum + (flock.current_quantity || 0), 0);

      const todaySummaryRes = await api.get(`/api/v1/farm/reports/summary?start_date=${today}&end_date=${today}`);
      const todaySummary = todaySummaryRes.data;

      const monthSummaryRes = await api.get(`/api/v1/farm/reports/summary?start_date=${firstDayOfMonth}&end_date=${today}`);
      const monthSummary = monthSummaryRes.data;

      setFarmData({
        totalBirds,
        todayEggs: todaySummary.good_eggs || 0,
        todayMortality: todaySummary.total_mortality || 0,
        monthEggs: monthSummary.good_eggs || 0
      });

      // === 2. FETCH FINANCE & POS DATA (Step 3) ===
      
      // A) Lifetime Balances (Cash, Receivables, Payables) & Monthly Profit
      const financeRes = await api.get('/api/v1/finance/dashboard');
      const globalFinance = financeRes.data;

      // B) Today's Revenue (Sales)
      const todayFinanceRes = await api.get(`/api/v1/finance/dashboard?start_date=${todayStart}&end_date=${todayEnd}`);
      const todayFinance = todayFinanceRes.data;

      setFinanceData({
        cash: globalFinance.cash_on_hand,
        profit: globalFinance.monthly_net_profit,
        todaySales: todayFinance.monthly_revenue,
        receivables: globalFinance.accounts_receivable,
        payables: globalFinance.accounts_payable
      });
      
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      Swal.fire('Warning', 'Some dashboard data could not be loaded.', 'warning');
    } finally {
      setLoading(false);
    }
  };

  const SummaryCard = ({ title, value, icon, color, subtitle }) => (
    <Card border="light" className="shadow-sm mb-4">
      <Card.Body>
        <Row className="d-block d-xl-flex align-items-center">
          <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
            <div className={`icon-shape icon-shape-${color} rounded me-4 me-sm-0`}>
              <FontAwesomeIcon icon={icon} size="2x" className={`text-${color}`} />
            </div>
          </Col>
          <Col xl={7} className="px-xl-0">
            <div className="d-none d-sm-block">
              <h6 className="fw-extrabold mb-1">{title}</h6>
            </div>
            <h4 className="mb-1 fw-bold">{value}</h4>
            {subtitle && <small className="text-muted">{subtitle}</small>}
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div>
          <h4>Control Center</h4>
          <p className="mb-0">Global overview of AMAS FARM operations.</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center mt-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading system metrics...</p>
        </div>
      ) : (
        <>
          {/* TOP ROW: KPIs */}
          <Row>
            {/* FARM KPIs */}
            <Col xs={12} sm={6} xl={3}>
              <SummaryCard 
                title="Total Live Birds" 
                value={farmData.totalBirds.toLocaleString()} 
                icon={faCrow} 
                color="warning" 
                subtitle="Across all active flocks"
              />
            </Col>
            <Col xs={12} sm={6} xl={3}>
              <SummaryCard 
                title="Today's Eggs" 
                value={farmData.todayEggs.toLocaleString()} 
                icon={faEgg} 
                color="info"
                subtitle={`Month total: ${farmData.monthEggs.toLocaleString()}`}
              />
            </Col>
            
            {/* FINANCE & POS KPIs (Step 3) */}
            <Col xs={12} sm={6} xl={3}>
              <SummaryCard 
                title="Cash on Hand" 
                value={`${Math.round(financeData.cash).toLocaleString()} TZS`} 
                icon={faMoneyBillWave} 
                color="success" 
                subtitle={`Month Profit: ${Math.round(financeData.profit).toLocaleString()} TZS`}
              />
            </Col>
            <Col xs={12} sm={6} xl={3}>
              <SummaryCard 
                title="Today's Sales" 
                value={`${Math.round(financeData.todaySales).toLocaleString()} TZS`} 
                icon={faShoppingCart} 
                color="primary" 
                subtitle="Total revenue generated today"
              />
            </Col>
          </Row>

          <Row>
            {/* MAIN CHART - FARM PRODUCTION (Placeholder static data until Step 2 is fully charted) */}
            <Col xs={12} xl={8} className="mb-4">
              <Card border="light" className="shadow-sm">
                <Card.Header>
                  <h5 className="mb-0">Farm Overview (Placeholder Chart)</h5>
                </Card.Header>
                <Card.Body>
                  <div style={{ width: "100%", height: 300 }}>
                    <div className="d-flex align-items-center justify-content-center h-100 bg-light text-muted rounded">
                      Detailed farm production & mortality charts will be wired here in upcoming steps.
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            {/* ACTION ALERTS */}
            <Col xs={12} xl={4} className="mb-4">
              <Card border="light" className="shadow-sm h-100">
                <Card.Header>
                  <h5 className="mb-0">System Alerts & Summaries</h5>
                </Card.Header>
                <Card.Body>
                  <ul className="list-unstyled mb-0">
                    {/* Mortality Alert */}
                    {farmData.todayMortality > 0 ? (
                      <li className="mb-3">
                        <div className="d-flex align-items-center text-danger">
                          <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
                          <span className="fw-bold">Mortality Alert:</span> 
                          <span className="ms-1">{farmData.todayMortality} birds died today.</span>
                        </div>
                      </li>
                    ) : (
                      <li className="mb-3 text-success">
                        <FontAwesomeIcon icon={faCheckCircle} className="me-2" />
                        No mortalities reported today.
                      </li>
                    )}
                    
                    <hr />

                    {/* Debt Alerts */}
                    <li className="mb-2">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="fw-bold">Customers Owe Us:</span>
                        <Badge bg={financeData.receivables > 0 ? "warning" : "success"}>
                          {Math.round(financeData.receivables).toLocaleString()} TZS
                        </Badge>
                      </div>
                    </li>
                    <li className="mb-3">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="fw-bold">We Owe Suppliers:</span>
                        <Badge bg={financeData.payables > 0 ? "danger" : "success"}>
                          {Math.round(financeData.payables).toLocaleString()} TZS
                        </Badge>
                      </div>
                    </li>

                    <hr />

                    <li className="mb-3 text-muted small">
                      <em>More alerts (Low Stock) will appear here in Step 4.</em>
                    </li>
                  </ul>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </>
  );
};
