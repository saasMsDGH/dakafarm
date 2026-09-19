import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faWallet, faFileInvoiceDollar, faHandHoldingUsd, faChartLine, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Spinner, Form, Button } from '@themesberg/react-bootstrap';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { api } from "../../api/axios";
import { useTranslation } from 'react-i18next';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [pnlData, setPnlData] = useState(null);
  const [startDate, setStartDate] = useState(moment().format('YYYY-MM-DD'));
  const [endDate, setEndDate] = useState(moment().format('YYYY-MM-DD'));

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const params = {};
      if (startDate) params.start_date = moment(startDate).startOf('day').toISOString();
      if (endDate) params.end_date = moment(endDate).endOf('day').toISOString();

      const [dashRes, pnlRes] = await Promise.all([
        api.get('/api/v1/finance/dashboard', { params }),
        api.get('/api/v1/finance/pnl', { params })
      ]);
      setMetrics(dashRes.data);
      setPnlData(pnlRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (val) => {
    return Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' TZS';
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
        <Spinner animation="border" variant="primary" />
      </div>
    );
  }

  if (!metrics || !pnlData) return <div>Error loading data.</div>;

  // Prepare data for Income vs Expenses Bar Chart
  const incomeVsExpenseData = [
    {
      name: 'Total Money In (Income)',
      amount: parseFloat(pnlData.revenue.total_revenue || 0) + parseFloat(pnlData.non_operating.other_income || 0),
      fill: '#10B981' // Green
    },
    {
      name: 'Total Money Out (Expenses)',
      amount: parseFloat(pnlData.cogs.total_cogs || 0) + parseFloat(pnlData.opex.total_opex || 0),
      fill: '#EF4444' // Red
    }
  ];

  // Prepare data for Expenses Pie Chart
  const expenseBreakdownData = [
    { name: 'Purchases (Inventory)', value: parseFloat(pnlData.cogs.total_cogs || 0), color: '#3B82F6' },
    { name: 'Direct Expenses', value: parseFloat(pnlData.opex.direct_expenses || 0), color: '#F59E0B' },
    { name: 'Payroll (Salaries)', value: parseFloat(pnlData.opex.payroll || 0), color: '#8B5CF6' },
  ].filter(item => item.value > 0);

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4 className="mb-0">Finance Dashboard</h4>
          <p className="mb-0 text-muted">A simple overview of your farm's financial health.</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Form onSubmit={fetchDashboardData} className="d-flex align-items-center">
            <Form.Group className="me-2 mb-0">
              <Form.Control type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} size="sm" />
            </Form.Group>
            <span className="me-2">to</span>
            <Form.Group className="me-2 mb-0">
              <Form.Control type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} size="sm" />
            </Form.Group>
            <Button variant="primary" size="sm" type="submit">
              <FontAwesomeIcon icon={faSearch} className="me-2"/> Filter
            </Button>
          </Form>
        </div>
      </div>

      {/* KPI CARDS */}
      <Row className="mb-4">
        {/* Cash on Hand */}
        <Col xs={12} sm={6} xl={3} className="mb-4">
          <Card border="light" className="shadow-sm">
            <Card.Body>
              <Row className="d-block d-xl-flex align-items-center">
                <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
                  <div className="icon-shape icon-shape-success rounded me-4 me-sm-0">
                    <FontAwesomeIcon icon={faWallet} size="2x" />
                  </div>
                </Col>
                <Col xl={7} className="px-xl-0">
                  <div className="d-none d-sm-block">
                    <h6 className="fw-extrabold mb-1">Cash Available</h6>
                  </div>
                  <div className="small d-flex mt-1">
                    <h4 className="fw-bolder mb-0">{formatCurrency(metrics.cash_on_hand)}</h4>
                  </div>
                  <div className="small mt-2 text-muted">Total money in banks & cash</div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Money Owed To Us */}
        <Col xs={12} sm={6} xl={3} className="mb-4">
          <Card border="light" className="shadow-sm">
            <Card.Body>
              <Row className="d-block d-xl-flex align-items-center">
                <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
                  <div className="icon-shape icon-shape-info rounded me-4 me-sm-0">
                    <FontAwesomeIcon icon={faHandHoldingUsd} size="2x" />
                  </div>
                </Col>
                <Col xl={7} className="px-xl-0">
                  <div className="d-none d-sm-block">
                    <h6 className="fw-extrabold mb-1">Customers Owe Us</h6>
                  </div>
                  <div className="small d-flex mt-1">
                    <h4 className="fw-bolder mb-0 text-info">{formatCurrency(metrics.accounts_receivable)}</h4>
                  </div>
                  <div className="small mt-2 text-muted">Unpaid customer invoices</div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Money We Owe */}
        <Col xs={12} sm={6} xl={3} className="mb-4">
          <Card border="light" className="shadow-sm">
            <Card.Body>
              <Row className="d-block d-xl-flex align-items-center">
                <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
                  <div className="icon-shape icon-shape-danger rounded me-4 me-sm-0">
                    <FontAwesomeIcon icon={faFileInvoiceDollar} size="2x" />
                  </div>
                </Col>
                <Col xl={7} className="px-xl-0">
                  <div className="d-none d-sm-block">
                    <h6 className="fw-extrabold mb-1">We Owe Suppliers</h6>
                  </div>
                  <div className="small d-flex mt-1">
                    <h4 className="fw-bolder mb-0 text-danger">{formatCurrency(metrics.accounts_payable)}</h4>
                  </div>
                  <div className="small mt-2 text-muted">Unpaid supplier bills</div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Monthly Net Profit */}
        <Col xs={12} sm={6} xl={3} className="mb-4">
          <Card border="light" className="shadow-sm">
            <Card.Body>
              <Row className="d-block d-xl-flex align-items-center">
                <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
                  <div className={`icon-shape icon-shape-${metrics.monthly_net_profit >= 0 ? 'success' : 'danger'} rounded me-4 me-sm-0`}>
                    <FontAwesomeIcon icon={faChartLine} size="2x" />
                  </div>
                </Col>
                <Col xl={7} className="px-xl-0">
                  <div className="d-none d-sm-block">
                    <h6 className="fw-extrabold mb-1">Profit (Selected Period)</h6>
                  </div>
                  <div className="small d-flex mt-1">
                    <h4 className={`fw-bolder mb-0 text-${metrics.monthly_net_profit >= 0 ? 'success' : 'danger'}`}>
                      {formatCurrency(metrics.monthly_net_profit)}
                    </h4>
                  </div>
                  <div className="small mt-2 text-muted">Revenue - Expenses</div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* CHARTS */}
      <Row>
        {/* Income vs Expenses Bar Chart */}
        <Col xs={12} xl={6} className="mb-4">
          <Card border="light" className="shadow-sm h-100">
            <Card.Header>
              <h5 className="mb-0">Income vs Expenses (Selected Period)</h5>
            </Card.Header>
            <Card.Body>
              <div style={{ width: '100%', height: 350 }}>
                <ResponsiveContainer>
                  <BarChart data={incomeVsExpenseData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <XAxis dataKey="name" />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="amount" radius={[5, 5, 0, 0]}>
                      {incomeVsExpenseData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Expenses Breakdown Pie Chart */}
        <Col xs={12} xl={6} className="mb-4">
          <Card border="light" className="shadow-sm h-100">
            <Card.Header>
              <h5 className="mb-0">Where Our Money Goes (Expenses)</h5>
            </Card.Header>
            <Card.Body className="d-flex flex-column justify-content-center align-items-center">
              {expenseBreakdownData.length > 0 ? (
                <div style={{ width: '100%', height: 350 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={expenseBreakdownData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {expenseBreakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Legend verticalAlign="bottom" height={36}/>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-muted mt-5">No expenses recorded yet.</div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </>
  );
};
