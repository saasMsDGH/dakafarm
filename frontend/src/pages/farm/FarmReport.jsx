import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPrint, faCalendarAlt, faEgg, faSkullCrossbones, faSeedling, faSyringe, faMoneyBillWave, faChartLine } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Button, Form, InputGroup } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  
  // Date filters
  const [startDate, setStartDate] = useState(moment().format('YYYY-MM-DD'));
  const [endDate, setEndDate] = useState(moment().format('YYYY-MM-DD'));

  const fetchReport = async (start, end) => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/farm/reports/summary', {
        params: { start_date: start, end_date: end }
      });
      setReportData(response.data);
    } catch (error) {
      console.error("Failed to fetch report:", error);
      let errorMsg = error.response?.data?.detail || 'Failed to generate report.';
      if (error.response?.status === 403) {
         errorMsg = t('admin_only', 'You do not have permission to view this report.');
      }
      Swal.fire('Error', errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch for today
    fetchReport(startDate, endDate);
  }, []);

  const handleApplyFilter = (e) => {
    e.preventDefault();
    fetchReport(startDate, endDate);
  };

  const setQuickRange = (range) => {
    let start, end = moment().format('YYYY-MM-DD');
    if (range === 'daily') {
      start = moment().format('YYYY-MM-DD');
    } else if (range === 'monthly') {
      start = moment().startOf('month').format('YYYY-MM-DD');
      end = moment().endOf('month').format('YYYY-MM-DD');
    } else if (range === 'yearly') {
      start = moment().startOf('year').format('YYYY-MM-DD');
      end = moment().endOf('year').format('YYYY-MM-DD');
    }
    setStartDate(start);
    setEndDate(end);
    fetchReport(start, end);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4 d-print-none">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('farm_report')}</h4>
          <p className="mb-0">{t('summary')} ({startDate} to {endDate})</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="outline-primary" size="sm" onClick={handlePrint}>
            <FontAwesomeIcon icon={faPrint} className="me-2" /> {t('print_report')}
          </Button>
        </div>
      </div>

      <Card className="mb-4 shadow-sm d-print-none">
        <Card.Body>
          <Form onSubmit={handleApplyFilter}>
            <Row className="align-items-end">
              <Col md={3} className="mb-3">
                <Form.Group id="start_date">
                  <Form.Label>{t('start_date')}</Form.Label>
                  <InputGroup>
                    <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                    <Form.Control 
                      required 
                      type="date" 
                      value={startDate} 
                      onChange={(e) => setStartDate(e.target.value)} 
                    />
                  </InputGroup>
                </Form.Group>
              </Col>
              <Col md={3} className="mb-3">
                <Form.Group id="end_date">
                  <Form.Label>{t('end_date')}</Form.Label>
                  <InputGroup>
                    <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                    <Form.Control 
                      required 
                      type="date" 
                      value={endDate} 
                      onChange={(e) => setEndDate(e.target.value)} 
                    />
                  </InputGroup>
                </Form.Group>
              </Col>
              <Col md={2} className="mb-3">
                <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                  {loading ? '...' : t('apply_filter')}
                </Button>
              </Col>
              <Col md={4} className="mb-3 d-flex justify-content-end">
                <div className="btn-group">
                  <Button variant="outline-secondary" onClick={() => setQuickRange('daily')}>{t('daily_report')}</Button>
                  <Button variant="outline-secondary" onClick={() => setQuickRange('monthly')}>{t('monthly_report')}</Button>
                  <Button variant="outline-secondary" onClick={() => setQuickRange('yearly')}>{t('yearly_report')}</Button>
                </div>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>

      {/* Print Header (Visible only when printing) */}
      <div className="d-none d-print-block mb-4 text-center">
        <h2>{t('farm_report')}</h2>
        <h5>{startDate} to {endDate}</h5>
        <hr />
      </div>

      {reportData ? (
        <div className="report-content">
          <Row>
            {/* Production Summary */}
            <Col xs={12} className="mb-4">
              <Card border="light" className="shadow-sm">
                <Card.Header className="bg-primary text-white">
                  <h5 className="mb-0"><FontAwesomeIcon icon={faEgg} className="me-2" /> {t('production_summary')}</h5>
                </Card.Header>
                <Card.Body>
                  <Row className="text-center">
                    <Col sm={4} className="mb-3 mb-sm-0">
                      <div className="fs-5 fw-normal text-gray-500">{t('total_eggs')}</div>
                      <div className="fs-2 fw-bold">{reportData.total_eggs}</div>
                    </Col>
                    <Col sm={4} className="mb-3 mb-sm-0">
                      <div className="fs-5 fw-normal text-gray-500">{t('good_eggs')}</div>
                      <div className="fs-2 fw-bold text-success">{reportData.good_eggs}</div>
                    </Col>
                    <Col sm={4}>
                      <div className="fs-5 fw-normal text-gray-500">{t('damaged_eggs')}</div>
                      <div className="fs-2 fw-bold text-danger">{reportData.damaged_eggs}</div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>

            {/* Health Summary */}
            <Col xs={12} md={6} className="mb-4">
              <Card border="light" className="shadow-sm h-100">
                <Card.Header className="bg-danger text-white">
                  <h5 className="mb-0"><FontAwesomeIcon icon={faSkullCrossbones} className="me-2" /> {t('health_summary')}</h5>
                </Card.Header>
                <Card.Body className="d-flex align-items-center justify-content-center">
                  <div className="text-center">
                    <div className="fs-5 fw-normal text-gray-500">{t('quantity_dead', 'Total Mortality')}</div>
                    <div className="fs-1 fw-bold text-danger">{reportData.total_mortality}</div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            {/* Expense Summary Breakdown */}
            <Col xs={12} md={6} className="mb-4">
              <Card border="light" className="shadow-sm h-100">
                <Card.Header className="bg-info text-white">
                  <h5 className="mb-0"><FontAwesomeIcon icon={faChartLine} className="me-2" /> {t('expense_summary')}</h5>
                </Card.Header>
                <Card.Body>
                  <ul className="list-group list-group-flush">
                    <li className="list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-2">
                      <span><FontAwesomeIcon icon={faSeedling} className="me-2 text-warning" /> Feed Cost (Used: {reportData.total_feed_used})</span>
                      <span className="fw-bold">{reportData.total_feed_cost}</span>
                    </li>
                    <li className="list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-2">
                      <span><FontAwesomeIcon icon={faSyringe} className="me-2 text-info" /> Medication Cost</span>
                      <span className="fw-bold">{reportData.total_medication_cost}</span>
                    </li>
                    <li className="list-group-item d-flex justify-content-between align-items-center border-0 px-0 pb-2">
                      <span><FontAwesomeIcon icon={faSyringe} className="me-2 text-info" /> Vaccination Cost</span>
                      <span className="fw-bold">{reportData.total_vaccination_cost}</span>
                    </li>
                    <hr />
                    <li className="list-group-item d-flex justify-content-between align-items-center border-0 px-0 pt-0">
                      <span className="fs-5 fw-bold">{t('total_expenses')}</span>
                      <span className="fs-4 fw-bold text-success">{reportData.total_expenses}</span>
                    </li>
                  </ul>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </div>
      ) : (
        <div className="text-center mt-5">
          {loading ? <p>Loading report data...</p> : <p>No data available. Try selecting a different date range.</p>}
        </div>
      )}
    </>
  );
};
