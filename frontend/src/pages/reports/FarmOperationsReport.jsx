import React, { useState, useEffect } from "react";
import { Card, Row, Col, Form, Button, Spinner, Alert } from "@themesberg/react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { 
    faCrow, faHeartbeat, faEgg, faUsers, faMoneyBillWave, 
    faTractor, faChartLine, faCalendarAlt, faPrint 
} from "@fortawesome/free-solid-svg-icons";
import { reportsApi } from "../../api/reportsApi";
import moment from "moment";

export default () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dateRange, setDateRange] = useState({ date_from: '', date_to: '' });

    const fetchSummary = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await reportsApi.getMasterSummary(dateRange);
            setData(res.data);
        } catch (err) {
            console.error("Failed to fetch master summary:", err);
            setError(typeof err.response?.data?.detail === 'object' 
                ? JSON.stringify(err.response.data.detail) 
                : err.response?.data?.detail || "Unable to load the farm operations report. Try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Fetch current month by default
        const start = moment().startOf('month').format('YYYY-MM-DD');
        const end = moment().endOf('month').format('YYYY-MM-DD');
        setDateRange({ date_from: start, date_to: end });
    }, []);

    // We fetch when dateRange changes if it is populated
    useEffect(() => {
        if (dateRange.date_from && dateRange.date_to) {
            fetchSummary();
        }
    }, [dateRange.date_from, dateRange.date_to]);

    const handleFilter = (e) => {
        e.preventDefault();
        fetchSummary();
    };

    const handlePrint = () => {
        window.print();
    };

    const SummaryWidget = ({ title, value, icon, color, subtitle }) => (
        <Col xs={12} sm={6} xl={4} className="mb-4">
            <Card border="light" className="shadow-sm h-100">
                <Card.Body>
                    <Row className="d-block d-xl-flex align-items-center">
                        <Col xl={5} className="text-xl-center d-flex align-items-center justify-content-xl-center mb-3 mb-xl-0">
                            <div className={`icon-shape icon-shape-${color} rounded me-4 me-sm-0`}>
                                <FontAwesomeIcon icon={icon} size="2x" />
                            </div>
                        </Col>
                        <Col xl={7} className="px-xl-0">
                            <div className="d-none d-sm-block">
                                <h6 className="text-muted mb-0">{title}</h6>
                                <h3 className="fw-extrabold mb-2">{value}</h3>
                                {subtitle && <small className="text-muted">{subtitle}</small>}
                            </div>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>
        </Col>
    );

    return (
        <div className="report-container">
            <style type="text/css">
                {`
                @media print {
                    @page { size: landscape; margin: 10mm; }
                    
                    /* Hide navigation elements */
                    nav, aside, .sidebar, header, .navbar {
                        display: none !important;
                    }

                    /* Reset main content layout constraints for print */
                    main, .content {
                        margin-left: 0 !important;
                        margin-top: 0 !important;
                        padding: 0 !important;
                        width: 100% !important;
                        max-width: 100% !important;
                    }

                    /* Hide items explicitly marked not for print */
                    .d-print-none {
                        display: none !important;
                    }

                    /* Force print styles on elements */
                    body {
                        background-color: #fff !important;
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                    
                    /* Tidy up cards for print */
                    .card {
                        border: 1px solid #dee2e6 !important;
                        box-shadow: none !important;
                        page-break-inside: avoid;
                    }
                    
                    /* Display block elements that were d-none on small screens */
                    .d-none.d-sm-block {
                        display: block !important;
                    }
                }
                `}
            </style>

            <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
                <div className="d-block mb-4 mb-md-0">
                    <h1 className="h4">Farm Operations Dashboard</h1>
                    <p className="mb-0">Executive overview of all farm activities, health, and finances.</p>
                </div>
                <div className="btn-toolbar mb-2 mb-md-0 d-print-none">
                    <Button variant="outline-primary" size="sm" onClick={handlePrint}>
                        <FontAwesomeIcon icon={faPrint} className="me-2" /> Print Report
                    </Button>
                </div>
            </div>

            <Card border="light" className="shadow-sm mb-4 d-print-none">
                <Card.Body>
                    <Form onSubmit={handleFilter}>
                        <Row>
                            <Col md={4} className="mb-3">
                                <Form.Group id="date_from">
                                    <Form.Label>Date From</Form.Label>
                                    <Form.Control 
                                        type="date" 
                                        value={dateRange.date_from}
                                        onChange={(e) => setDateRange({...dateRange, date_from: e.target.value})}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4} className="mb-3">
                                <Form.Group id="date_to">
                                    <Form.Label>Date To</Form.Label>
                                    <Form.Control 
                                        type="date" 
                                        value={dateRange.date_to}
                                        onChange={(e) => setDateRange({...dateRange, date_to: e.target.value})}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4} className="mb-3 d-flex align-items-end">
                                <Button variant="primary" type="submit" className="w-100">
                                    <FontAwesomeIcon icon={faCalendarAlt} className="me-2" /> Apply Filter
                                </Button>
                            </Col>
                        </Row>
                    </Form>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger">{error}</Alert>}
            
            {loading ? (
                <div className="text-center py-5 d-print-none">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-3">Compiling operations data...</p>
                </div>
            ) : data ? (
                <div className="print-friendly-area">
                    {/* Header info visible only in print */}
                    <div className="d-none d-print-block mb-4">
                        <h5>Report Period: {dateRange.date_from} to {dateRange.date_to}</h5>
                        <hr />
                    </div>

                    <h5 className="mb-3 mt-2">Flocks & Livestock</h5>
                    <Row>
                        <SummaryWidget title="Total Live Birds" value={data.flocks.total_birds} icon={faCrow} color="primary" subtitle={`Across ${data.flocks.active_flocks} active flocks`} />
                        <SummaryWidget title="Total Mortality" value={data.flocks.total_mortality} icon={faHeartbeat} color="danger" subtitle="Birds lost in period" />
                        <SummaryWidget title="Sick Birds" value={data.flocks.sick_birds} icon={faHeartbeat} color="warning" subtitle="Currently under treatment" />
                    </Row>

                    <h5 className="mb-3 mt-4">Health & Medication</h5>
                    <Row>
                        <SummaryWidget title="Medication Cost" value={`Tsh ${Number(data.health.medication_cost).toLocaleString()}`} icon={faHeartbeat} color="info" />
                        <SummaryWidget title="Vaccination Cost" value={`Tsh ${Number(data.health.vaccines_used).toLocaleString()}`} icon={faHeartbeat} color="secondary" />
                    </Row>

                    <h5 className="mb-3 mt-4">Production</h5>
                    <Row>
                        <SummaryWidget title="Total Production" value={data.production.total_quantity} icon={faEgg} color="tertiary" subtitle="Total collected units" />
                    </Row>

                    <h5 className="mb-3 mt-4">Financial Overview</h5>
                    <Row>
                        <SummaryWidget title="Revenue" value={`Tsh ${Number(data.finance.revenue).toLocaleString()}`} icon={faMoneyBillWave} color="success" />
                        <SummaryWidget title="Expenses" value={`Tsh ${Number(data.finance.expenses).toLocaleString()}`} icon={faMoneyBillWave} color="danger" />
                        <SummaryWidget title="Net Profit" value={`Tsh ${Number(data.finance.net_profit).toLocaleString()}`} icon={faChartLine} color={data.finance.net_profit >= 0 ? "success" : "danger"} />
                    </Row>

                    <h5 className="mb-3 mt-4">Resources & Assets</h5>
                    <Row>
                        <SummaryWidget title="Active Employees" value={data.hr.total_employees} icon={faUsers} color="info" subtitle={`Payroll: Tsh ${Number(data.hr.payroll_total).toLocaleString()}`} />
                        <SummaryWidget title="Active Assets" value={data.assets.total_active_assets} icon={faTractor} color="primary" subtitle={`Value: Tsh ${Number(data.assets.asset_value).toLocaleString()}`} />
                    </Row>
                </div>
            ) : null}
        </div>
    );
};
