import React, { useState, useEffect, useRef } from "react";
import { Card, Button, Spinner, Alert, Form, Row, Col, Table } from "@themesberg/react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPrint, faTractor, faChartLine, faMoneyBillWave, faUsers, faCrow } from "@fortawesome/free-solid-svg-icons";
import { reportsApi } from "../../api/reportsApi";
import moment from "moment";
import { useReactToPrint } from 'react-to-print';

export default () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dateRange, setDateRange] = useState({ date_from: '', date_to: '' });

    const reportRef = useRef();

    const fetchSummary = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await reportsApi.getMasterSummary(dateRange);
            setData(res.data);
        } catch (err) {
            console.error("Failed to fetch master summary:", err);
            setError("Unable to load the farm operations report. Try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSummary();
    }, []);

    const handlePrint = useReactToPrint({
        contentRef: reportRef,
        documentTitle: `AMAS_FARM_Management_Summary_${moment().format('YYYYMMDD')}`,
    });

    const formatMoney = (val) => {
        return Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    };

    const renderOfficialReport = () => {
        if (!data) return null;

        const period = (dateRange.date_from && dateRange.date_to)
            ? `${moment(dateRange.date_from).format('DD/MM/YYYY')} - ${moment(dateRange.date_to).format('DD/MM/YYYY')}`
            : moment().format('MMMM YYYY');

        const generatedOn = moment(data.generated_on).format('DD/MM/YYYY HH:mm');

        const f = data.financial_overview;
        const c = data.cash_position;
        const o = data.farm_operations;
        const cs = data.customers_suppliers;

        return (
            <div className="official-report" ref={reportRef}>
                {/* Header Section */}
                <div className="report-header text-center mb-5">
                    <div className="mb-3 text-primary">
                        <FontAwesomeIcon icon={faTractor} size="3x" />
                    </div>
                    <h2 className="fw-bolder tracking-tight text-uppercase mb-1" style={{ letterSpacing: '2px' }}>Amas Farm</h2>
                    <h4 className="text-muted text-uppercase mb-4" style={{ letterSpacing: '1px' }}>Management Summary</h4>
                    
                    <Row className="text-start mt-4 border-bottom border-top py-3 mb-4">
                        <Col xs={6}>
                            <strong className="text-muted d-block text-uppercase" style={{ fontSize: '0.8rem' }}>Reporting Period</strong>
                            <span className="fw-bold">{period}</span>
                        </Col>
                        <Col xs={6} className="text-end">
                            <strong className="text-muted d-block text-uppercase" style={{ fontSize: '0.8rem' }}>Generated On</strong>
                            <span className="fw-bold">{generatedOn}</span>
                        </Col>
                    </Row>
                </div>

                <Row>
                    {/* Left Column */}
                    <Col md={6} className="pe-md-4">
                        {/* Financial Overview */}
                        <div className="mb-5">
                            <h5 className="border-bottom pb-2 mb-3 text-uppercase fw-bold text-primary">
                                <FontAwesomeIcon icon={faChartLine} className="me-2" /> Financial Overview
                            </h5>
                            <Table borderless size="sm" className="report-table">
                                <tbody>
                                    <tr><td className="text-muted">Total Sales</td><td className="text-end fw-bold">{formatMoney(f.total_sales)}</td></tr>
                                    <tr><td className="text-muted">Total Purchases</td><td className="text-end fw-bold">{formatMoney(f.total_purchases)}</td></tr>
                                    <tr><td className="text-muted">Total Expenses</td><td className="text-end fw-bold">{formatMoney(f.total_expenses)}</td></tr>
                                    <tr><td className="text-muted">Total Payroll</td><td className="text-end fw-bold">{formatMoney(f.total_payroll)}</td></tr>
                                    <tr className="border-top">
                                        <td className="pt-2 fw-bolder fs-5">Net Profit</td>
                                        <td className="pt-2 text-end fw-bolder fs-5 text-success">{formatMoney(f.net_profit)}</td>
                                    </tr>
                                </tbody>
                            </Table>
                        </div>

                        {/* Customers & Suppliers */}
                        <div className="mb-5">
                            <h5 className="border-bottom pb-2 mb-3 text-uppercase fw-bold text-primary">
                                <FontAwesomeIcon icon={faUsers} className="me-2" /> Customers & Suppliers
                            </h5>
                            <Table borderless size="sm" className="report-table">
                                <tbody>
                                    <tr><td className="text-muted">Customer Outstanding</td><td className="text-end fw-bold text-warning">{formatMoney(cs.customer_outstanding)}</td></tr>
                                    <tr><td className="text-muted">Supplier Payable</td><td className="text-end fw-bold text-danger">{formatMoney(cs.supplier_payable)}</td></tr>
                                    <tr><td className="text-muted">Active Customers</td><td className="text-end fw-bold">{formatMoney(cs.active_customers)}</td></tr>
                                    <tr><td className="text-muted">Active Suppliers</td><td className="text-end fw-bold">{formatMoney(cs.active_suppliers)}</td></tr>
                                </tbody>
                            </Table>
                        </div>
                    </Col>

                    {/* Right Column */}
                    <Col md={6} className="ps-md-4">
                        {/* Cash Position */}
                        <div className="mb-5">
                            <h5 className="border-bottom pb-2 mb-3 text-uppercase fw-bold text-primary">
                                <FontAwesomeIcon icon={faMoneyBillWave} className="me-2" /> Cash Position
                            </h5>
                            <Table borderless size="sm" className="report-table">
                                <tbody>
                                    <tr><td className="text-muted">Cash</td><td className="text-end fw-bold">{formatMoney(c.cash)}</td></tr>
                                    <tr><td className="text-muted">Bank</td><td className="text-end fw-bold">{formatMoney(c.bank)}</td></tr>
                                    <tr><td className="text-muted">Mobile Money</td><td className="text-end fw-bold">{formatMoney(c.mobile_money)}</td></tr>
                                    <tr className="border-top">
                                        <td className="pt-2 fw-bolder fs-5 text-uppercase">Total Funds</td>
                                        <td className="pt-2 text-end fw-bolder fs-5 text-primary">{formatMoney(c.total_available)}</td>
                                    </tr>
                                </tbody>
                            </Table>
                        </div>

                        {/* Farm Operations */}
                        <div className="mb-5">
                            <h5 className="border-bottom pb-2 mb-3 text-uppercase fw-bold text-primary">
                                <FontAwesomeIcon icon={faCrow} className="me-2" /> Farm Operations
                            </h5>
                            <Table borderless size="sm" className="report-table">
                                <tbody>
                                    <tr><td className="text-muted">Total Birds</td><td className="text-end fw-bold">{formatMoney(o.total_birds)}</td></tr>
                                    <tr><td className="text-muted">Eggs Produced</td><td className="text-end fw-bold">{formatMoney(o.eggs_produced)}</td></tr>
                                    <tr><td className="text-muted">Mortality Rate</td><td className="text-end fw-bold">{o.mortality_rate}</td></tr>
                                    <tr><td className="text-muted">Feed Used</td><td className="text-end fw-bold">{o.feed_used}</td></tr>
                                    <tr><td className="text-muted">Vaccinations Due</td><td className="text-end fw-bold">{formatMoney(o.vaccinations_due)}</td></tr>
                                    <tr>
                                        <td className="text-muted">Low Stock Items</td>
                                        <td className="text-end fw-bold">
                                            {o.low_stock_items > 0 ? (
                                                <span className="text-danger">{formatMoney(o.low_stock_items)}</span>
                                            ) : (
                                                <span className="text-success">0</span>
                                            )}
                                        </td>
                                    </tr>
                                </tbody>
                            </Table>
                        </div>
                    </Col>
                </Row>
                
                {/* Footer Section */}
                <div className="mt-5 pt-4 border-top text-center text-muted" style={{ fontSize: '0.85rem' }}>
                    <p className="mb-0">This document is a system-generated summary of farm operations and finances.</p>
                    <p><strong>Amas Farm Management System</strong> &copy; {new Date().getFullYear()}</p>
                </div>
            </div>
        );
    };

    return (
        <div className="report-container">
            <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4 d-print-none">
                <div className="d-block mb-4 mb-md-0">
                    <h4>Management Summary</h4>
                    <p className="mb-0">High-level overview of farm operations and finances.</p>
                </div>
                <div className="btn-toolbar mb-2 mb-md-0">
                    <Button variant="outline-primary" size="sm" onClick={handlePrint} disabled={!data || loading}>
                        <FontAwesomeIcon icon={faPrint} className="me-2" /> Print PDF Report
                    </Button>
                </div>
            </div>

            <Card className="border-0 shadow mb-4 d-print-none">
                <Card.Body>
                    <Row className="align-items-end">
                        <Col md={4} className="mb-3">
                            <Form.Group>
                                <Form.Label>From Date</Form.Label>
                                <Form.Control 
                                    type="date" 
                                    value={dateRange.date_from}
                                    onChange={(e) => setDateRange({...dateRange, date_from: e.target.value})}
                                />
                            </Form.Group>
                        </Col>
                        <Col md={4} className="mb-3">
                            <Form.Group>
                                <Form.Label>To Date</Form.Label>
                                <Form.Control 
                                    type="date" 
                                    value={dateRange.date_to}
                                    onChange={(e) => setDateRange({...dateRange, date_to: e.target.value})}
                                />
                            </Form.Group>
                        </Col>
                        <Col md={4} className="mb-3">
                            <Button variant="primary" className="w-100" onClick={fetchSummary} disabled={loading}>
                                {loading ? <Spinner animation="border" size="sm" /> : "Generate Report"}
                            </Button>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger" className="d-print-none">{error}</Alert>}
            
            {loading ? (
                <div className="text-center py-5 d-print-none">
                    <Spinner animation="border" variant="primary" />
                </div>
            ) : data ? (
                <div className="d-flex justify-content-center pb-5">
                    {/* The physical "A4 Paper" look */}
                    <div className="paper-container shadow-lg" style={{ 
                        background: '#ffffff', 
                        width: '100%', 
                        maxWidth: '210mm', // A4 width
                        minHeight: '297mm', // A4 height
                        padding: '15mm 20mm',
                        borderRadius: '8px'
                    }}>
                        {renderOfficialReport()}
                    </div>
                </div>
            ) : null}
            
            <style type="text/css">
                {`
                /* Styling the tables for the report */
                .report-table td {
                    padding-top: 0.5rem;
                    padding-bottom: 0.5rem;
                    font-size: 0.95rem;
                }

                @media print {
                    @page { 
                        size: A4 portrait; 
                        margin: 15mm; 
                    }
                    body { 
                        background: #fff !important; 
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                    .d-print-none, nav, aside, .sidebar, header, .navbar { 
                        display: none !important; 
                    }
                    .report-container, .content, main { 
                        width: 100% !important; 
                        margin: 0 !important; 
                        padding: 0 !important; 
                    }
                    .paper-container { 
                        box-shadow: none !important; 
                        max-width: none !important; 
                        min-height: auto !important; 
                        padding: 0 !important; 
                        width: 100% !important; 
                    }
                }
                `}
            </style>
        </div>
    );
};
