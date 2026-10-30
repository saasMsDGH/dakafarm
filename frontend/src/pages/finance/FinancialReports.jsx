import LegacyDataNotice from '../../components/LegacyDataNotice';
import { useTranslation } from 'react-i18next';
import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileInvoiceDollar, faCheckCircle, faExclamationTriangle, faCalendarAlt, faChartLine, faBalanceScale, faMoneyBillWave } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Form, InputGroup, Button, Tabs, Tab, Alert, Badge } from '@themesberg/react-bootstrap';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('pnl');
  const [loading, setLoading] = useState(false);
  
  // Date Filters
  const [dateFrom, setDateFrom] = useState(moment().format('YYYY-MM-DD'));
  const [dateTo, setDateTo] = useState(moment().format('YYYY-MM-DD'));

  // Report Data
  const [trialBalance, setTrialBalance] = useState(null);
  const [pnl, setPnl] = useState(null);
  const [cashFlow, setCashFlow] = useState(null);
  const [balanceSheet, setBalanceSheet] = useState(null);

  const fetchReports = async () => {
    setLoading(true);
    try {
      // PNL & CashFlow use start_date, end_date
      let rangeQuery = '';
      if (dateFrom) rangeQuery += `start_date=${moment(dateFrom).startOf('day').toISOString()}&`;
      if (dateTo) rangeQuery += `end_date=${moment(dateTo).endOf('day').toISOString()}&`;
      if (rangeQuery.endsWith('&')) rangeQuery = rangeQuery.slice(0, -1);
      const rangeStr = rangeQuery ? `?${rangeQuery}` : '';
      
      // {t("trial_balance", "Trial Balance")} & {t("balance_sheet", "Balance Sheet")} use as_of_date
      const asOfQuery = dateTo ? `?as_of_date=${moment(dateTo).endOf('day').toISOString()}` : '';

      const [tbRes, pnlRes, cfRes, bsRes] = await Promise.all([
        api.get(`/api/v1/finance/trial-balance/${asOfQuery}`),
        api.get(`/api/v1/finance/pnl/${rangeStr}`),
        api.get(`/api/v1/finance/cash-flow/${rangeStr}`),
        api.get(`/api/v1/finance/balance-sheet/${asOfQuery}`)
      ]);

      setTrialBalance(tbRes.data);
      setPnl(pnlRes.data);
      setCashFlow(cfRes.data);
      setBalanceSheet(bsRes.data);
    } catch (error) {
      console.error(error);
      Swal.fire('Error', 'Failed to generate financial reports.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleApplyFilter = () => {
    fetchReports();
  };

  const handleClearFilter = () => {
    setDateFrom(moment().format('YYYY-MM-DD'));
    setDateTo(moment().format('YYYY-MM-DD'));
    setTimeout(fetchReports, 100);
  };

  // Helper for formatting money
  const fmt = (num) => parseFloat(num || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <>
      <LegacyDataNotice />
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t("financial_reports", "Financial Reports")}</h4>
          <p className="mb-0">{t("financial_reports_desc", "Real-time accounting insights and statements for DAKAFARM.")}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0 d-flex gap-2">
            <InputGroup>
              <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
              <Form.Control type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} placeholder="From Date" />
            </InputGroup>
            <InputGroup>
              <InputGroup.Text>{t("to", "To")}</InputGroup.Text>
              <Form.Control type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} placeholder="To Date" />
            </InputGroup>
            <Button variant="primary" onClick={handleApplyFilter}>{t("generate", "Generate")}</Button>
            <Button variant="outline-secondary" onClick={handleClearFilter}>{t("clear", "Clear")}</Button>
        </div>
      </div>

      <Card border="light" className="shadow-sm">
        <Card.Body>
          <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-4">
            
            {/* ---------------- PROFIT & LOSS ---------------- */}
            <Tab eventKey="pnl" title={<span><FontAwesomeIcon icon={faChartLine} className="me-2" /> {t("profit_loss", "Profit & Loss")}</span>}>
              {loading ? <div className="text-center p-5">{t("generating_report", "Generating Report...")}</div> : pnl && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <h4 className="text-center mb-4">INCOME STATEMENT</h4>
                  
                  {/* Revenue */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                    <span className="fw-bold fs-5">Revenue</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Sales Income</span>
                    <span>{fmt(pnl.revenue.sales)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Total Revenue</span>
                    <span className="fw-bold">{fmt(pnl.revenue.total_revenue)}</span>
                  </div>

                  {/* COGS */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                    <span className="fw-bold fs-5">Cost of Goods Sold (COGS)</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Purchases (Inventory/Direct)</span>
                    <span>{fmt(pnl.cogs.purchases)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Total COGS</span>
                    <span className="fw-bold text-danger">({fmt(pnl.cogs.total_cogs)})</span>
                  </div>

                  {/* Gross Profit */}
                  <div className="d-flex justify-content-between bg-light p-2 mb-4 rounded">
                    <span className="fw-bold fs-5">Gross Profit</span>
                    <span className="fw-bold fs-5">{fmt(pnl.gross_profit)}</span>
                  </div>

                  {/* OPEX */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                    <span className="fw-bold fs-5">Operating Expenses (OPEX)</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Direct Expenses</span>
                    <span>{fmt(pnl.opex.direct_expenses)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Payroll / Wages</span>
                    <span>{fmt(pnl.opex.payroll)}</span>
                  </div>
                  {parseFloat(pnl.opex.negative_adjustments) > 0 && (
                    <div className="d-flex justify-content-between mb-1 ms-3 text-muted">
                      <span>Inventory Loss/Adjustments</span>
                      <span>{fmt(pnl.opex.negative_adjustments)}</span>
                    </div>
                  )}
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Total Operating Expenses</span>
                    <span className="fw-bold text-danger">({fmt(pnl.opex.total_opex)})</span>
                  </div>

                  {/* Operating Profit */}
                  <div className="d-flex justify-content-between p-2 mb-4">
                    <span className="fw-bold fs-5 text-muted">Operating Profit</span>
                    <span className="fw-bold fs-5 text-muted">{fmt(pnl.operating_profit)}</span>
                  </div>

                  {/* Non-Operating */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                    <span className="fw-bold fs-6">Non-Operating & Other</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3 text-muted small">
                    <span>Other Income</span>
                    <span>{fmt(pnl.non_operating.other_income)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3 text-muted small">
                    <span>Uncategorized Adjustments</span>
                    <span>{fmt(parseFloat(pnl.non_operating.uncategorized_income) - parseFloat(pnl.non_operating.uncategorized_expense))}</span>
                  </div>
                  
                  {/* NET PROFIT */}
                  <div className={`d-flex justify-content-between p-3 mt-4 rounded text-white ${parseFloat(pnl.net_profit) >= 0 ? 'bg-success' : 'bg-danger'}`}>
                    <span className="fw-bold fs-4">NET PROFIT</span>
                    <span className="fw-bold fs-4">{fmt(pnl.net_profit)}</span>
                  </div>

                </div>
              )}
            </Tab>

            {/* ---------------- CASH FLOW ---------------- */}
            <Tab eventKey="cashflow" title={<span><FontAwesomeIcon icon={faMoneyBillWave} className="me-2" /> {t("cash_flow", "Cash Flow")}</span>}>
              {loading ? <div className="text-center p-5">{t("generating_report", "Generating Report...")}</div> : cashFlow && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <h4 className="text-center mb-4">STATEMENT OF CASH FLOWS</h4>
                  
                  <div className="d-flex justify-content-between mb-4 pb-2 border-bottom">
                    <span className="fw-bold">Opening Cash Balance</span>
                    <span className="fw-bold">{fmt(cashFlow.opening_balance)}</span>
                  </div>

                  {/* Operating */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                    <span className="fw-bold fs-5 text-primary">Cash from Operating Activities</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Cash Received from Customers</span>
                    <span className="text-success">{fmt(cashFlow.operating.cash_from_sales)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Cash Paid to Suppliers</span>
                    <span className="text-danger">({fmt(cashFlow.operating.cash_to_suppliers)})</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Cash Paid for Expenses</span>
                    <span className="text-danger">({fmt(cashFlow.operating.cash_for_expenses)})</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Cash Paid for Payroll</span>
                    <span className="text-danger">({fmt(cashFlow.operating.cash_for_payroll)})</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Net Operating Cash Flow</span>
                    <span className="fw-bold">{fmt(cashFlow.operating.net_operating_cash_flow)}</span>
                  </div>

                  {/* Investing */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2 mt-4">
                    <span className="fw-bold fs-5 text-primary">Cash from Investing Activities</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Cash Paid for Assets (Equipment, etc.)</span>
                    <span className="text-danger">({fmt(cashFlow.investing.cash_for_assets)})</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Net Investing Cash Flow</span>
                    <span className="fw-bold">{fmt(cashFlow.investing.net_investing_cash_flow)}</span>
                  </div>

                  {/* Financing */}
                  <div className="d-flex justify-content-between border-bottom pb-2 mb-2 mt-4">
                    <span className="fw-bold fs-5 text-primary">Cash from Financing Activities</span>
                  </div>
                  <div className="d-flex justify-content-between mb-1 ms-3">
                    <span>Owner Investments (Capital Introduced)</span>
                    <span className="text-success">{fmt(cashFlow.financing.owner_investments)}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span className="fw-bold">Net Financing Cash Flow</span>
                    <span className="fw-bold">{fmt(cashFlow.financing.net_financing_cash_flow)}</span>
                  </div>

                  {/* Net Increase and Closing */}
                  <div className="d-flex justify-content-between bg-light p-2 mb-2 mt-4 rounded">
                    <span className="fw-bold">Net Change in Cash</span>
                    <span className="fw-bold">{fmt(cashFlow.net_change_in_cash)}</span>
                  </div>
                  <div className="d-flex justify-content-between p-3 rounded text-white bg-dark">
                    <span className="fw-bold fs-5">Closing Cash Balance</span>
                    <span className="fw-bold fs-5">{fmt(cashFlow.ending_balance)}</span>
                  </div>
                </div>
              )}
            </Tab>

            {/* ---------------- BALANCE SHEET ---------------- */}
            <Tab eventKey="balancesheet" title={<span><FontAwesomeIcon icon={faBalanceScale} className="me-2" /> {t("balance_sheet", "Balance Sheet")}</span>}>
              {loading ? <div className="text-center p-5">Generating Report...</div> : balanceSheet && (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                  <div className="d-flex justify-content-between align-items-center mb-4">
                    <h4 className="mb-0">BALANCE SHEET</h4>
                    {balanceSheet.is_balanced ? 
                      <Badge bg="success" className="fs-6 p-2"><FontAwesomeIcon icon={faCheckCircle} className="me-1"/> Books are Balanced</Badge> : 
                      <Badge bg="danger" className="fs-6 p-2"><FontAwesomeIcon icon={faExclamationTriangle} className="me-1"/> Out of Balance</Badge>
                    }
                  </div>
                  
                  <Row>
                    <Col md={6}>
                      <div className="bg-light p-3 rounded h-100">
                        <h5 className="border-bottom pb-2 text-primary">ASSETS</h5>
                        
                        <div className="fw-bold mt-3 mb-1">Current Assets</div>
                        <div className="d-flex justify-content-between ms-2 mb-1 text-sm">
                          <span>Cash & Bank</span>
                          <span>{fmt(balanceSheet.assets.cash_and_bank)}</span>
                        </div>
                        <div className="d-flex justify-content-between ms-2 mb-1 text-sm">
                          <span>Accounts Receivable</span>
                          <span>{fmt(balanceSheet.assets.accounts_receivable)}</span>
                        </div>
                        <div className="d-flex justify-content-between ms-2 mb-3 text-sm">
                          <span>Prepaid Purchases (Advance)</span>
                          <span>{fmt(balanceSheet.assets.prepaid_purchases)}</span>
                        </div>
                        
                        <div className="fw-bold mt-3 mb-1">Non-Current Assets</div>
                        <div className="d-flex justify-content-between ms-2 mb-3 text-sm">
                          <span>Fixed Assets (Tractors, Land)</span>
                          <span>{fmt(balanceSheet.assets.fixed_assets)}</span>
                        </div>

                        <div className="d-flex justify-content-between mt-4 pt-2 border-top">
                          <span className="fw-bold fs-5">Total Assets</span>
                          <span className="fw-bold fs-5 text-success">{fmt(balanceSheet.assets.total_assets)}</span>
                        </div>
                      </div>
                    </Col>

                    <Col md={6}>
                      <div className="bg-light p-3 rounded h-100 d-flex flex-column">
                        
                        <div>
                          <h5 className="border-bottom pb-2 text-danger">LIABILITIES</h5>
                          <div className="fw-bold mt-3 mb-1">Current Liabilities</div>
                          <div className="d-flex justify-content-between ms-2 mb-1 text-sm">
                            <span>Accounts Payable (Unpaid Bills)</span>
                            <span>{fmt(balanceSheet.liabilities.accounts_payable)}</span>
                          </div>
                          <div className="d-flex justify-content-between ms-2 mb-3 text-sm">
                            <span>Unearned Revenue (Advance Sales)</span>
                            <span>{fmt(balanceSheet.liabilities.unearned_revenue)}</span>
                          </div>
                          <div className="d-flex justify-content-between mt-2 pt-2 border-top">
                            <span className="fw-bold">Total Liabilities</span>
                            <span className="fw-bold">{fmt(balanceSheet.liabilities.total_liabilities)}</span>
                          </div>
                        </div>

                        <div className="mt-4">
                          <h5 className="border-bottom pb-2 text-info">EQUITY</h5>
                          <div className="d-flex justify-content-between ms-2 mt-3 mb-1 text-sm">
                            <span>Owner's Capital</span>
                            <span>{fmt(balanceSheet.equity.owner_capital)}</span>
                          </div>
                          <div className="d-flex justify-content-between ms-2 mb-3 text-sm">
                            <span>Retained Earnings (Net Profit)</span>
                            <span>{fmt(balanceSheet.equity.retained_earnings)}</span>
                          </div>
                          <div className="d-flex justify-content-between mt-2 pt-2 border-top">
                            <span className="fw-bold">Total Equity</span>
                            <span className="fw-bold">{fmt(balanceSheet.equity.total_equity)}</span>
                          </div>
                        </div>

                        <div className="mt-auto d-flex justify-content-between pt-3 border-top border-2 border-dark">
                          <span className="fw-bold fs-5">Liabilities + Equity</span>
                          <span className="fw-bold fs-5 text-primary">{fmt(parseFloat(balanceSheet.liabilities.total_liabilities) + parseFloat(balanceSheet.equity.total_equity))}</span>
                        </div>

                      </div>
                    </Col>
                  </Row>
                </div>
              )}
            </Tab>

            {/* ---------------- TRIAL BALANCE ---------------- */}
            <Tab eventKey="trialbalance" title={<span><FontAwesomeIcon icon={faFileInvoiceDollar} className="me-2" /> {t("trial_balance", "Trial Balance")}</span>}>
              {loading ? <div className="text-center p-5">Generating Report...</div> : trialBalance && (
                <div>
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4 className="mb-0">TRIAL BALANCE</h4>
                    {trialBalance.is_balanced ? 
                      <Badge bg="success" className="p-2"><FontAwesomeIcon icon={faCheckCircle} className="me-1"/> Balanced</Badge> : 
                      <Badge bg="danger" className="p-2"><FontAwesomeIcon icon={faExclamationTriangle} className="me-1"/> Out of Balance</Badge>
                    }
                  </div>
                  
                  <Table responsive hover bordered className="bg-white">
                    <thead className="thead-light">
                      <tr>
                        <th>Account Name</th>
                        <th className="text-end">Debit (Dr)</th>
                        <th className="text-end">Credit (Cr)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trialBalance.entries.map((entry, idx) => (
                        <tr key={idx}>
                          <td>{entry.account_name}</td>
                          <td className="text-end">{parseFloat(entry.debit) !== 0 ? fmt(entry.debit) : '-'}</td>
                          <td className="text-end">{parseFloat(entry.credit) !== 0 ? fmt(entry.credit) : '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="fw-bold bg-light">
                      <tr>
                        <td className="text-end fs-5">TOTALS:</td>
                        <td className="text-end fs-5 text-primary">{fmt(trialBalance.total_debits)}</td>
                        <td className="text-end fs-5 text-primary">{fmt(trialBalance.total_credits)}</td>
                      </tr>
                    </tfoot>
                  </Table>
                </div>
              )}
            </Tab>

          </Tabs>
        </Card.Body>
      </Card>
    </>
  );
};
