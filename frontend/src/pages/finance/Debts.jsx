import { useTranslation } from 'react-i18next';
import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faEye } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Form, InputGroup, Pagination, Badge, Button, Tabs, Tab, Modal } from '@themesberg/react-bootstrap';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  const [key, setKey] = useState('receivables');
  
  // Receivables State
  const [receivables, setReceivables] = useState([]);
  const [rTotal, setRTotal] = useState(0);
  const [rPage, setRPage] = useState(1);
  const [rTotalPages, setRTotalPages] = useState(1);
  const [rSearch, setRSearch] = useState('');
  const [rLoading, setRLoading] = useState(false);

  // Payables State
  const [payables, setPayables] = useState([]);
  const [pTotal, setPTotal] = useState(0);
  const [pPage, setPPage] = useState(1);
  const [pTotalPages, setPTotalPages] = useState(1);
  const [pSearch, setPSearch] = useState('');
  const [pLoading, setPLoading] = useState(false);

  // Details Modal State
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailType, setDetailType] = useState('customer'); // 'customer' or 'supplier'

  const fetchReceivables = async () => {
    setRLoading(true);
    try {
      let query = `/api/v1/finance/receivables/customers?page=${rPage}&limit=20`;
      if (rSearch) query += `&search=${rSearch}`;
      const res = await api.get(query);
      setReceivables(res.data.items);
      setRTotal(res.data.total_outstanding);
      setRTotalPages(res.data.pages || 1);
    } catch (error) {
      console.error(error);
    } finally {
      setRLoading(false);
    }
  };

  const fetchPayables = async () => {
    setPLoading(true);
    try {
      let query = `/api/v1/finance/payables/suppliers?page=${pPage}&limit=20`;
      if (pSearch) query += `&search=${pSearch}`;
      const res = await api.get(query);
      setPayables(res.data.items);
      setPTotal(res.data.total_outstanding);
      setPTotalPages(res.data.pages || 1);
    } catch (error) {
      console.error(error);
    } finally {
      setPLoading(false);
    }
  };

  useEffect(() => {
    fetchReceivables();
  }, [rPage]);

  useEffect(() => {
    fetchPayables();
  }, [pPage]);

  const handleRSearch = (e) => { setRSearch(e.target.value); };
  const applyRSearch = () => { setRPage(1); fetchReceivables(); };
  
  const handlePSearch = (e) => { setPSearch(e.target.value); };
  const applyPSearch = () => { setPPage(1); fetchPayables(); };

  const viewCustomerDetails = async (id) => {
    setDetailType('customer');
    setShowDetailModal(true);
    setDetailLoading(true);
    setDetailData(null);
    try {
      const res = await api.get(`/api/v1/finance/receivables/customers/${id}`);
      setDetailData(res.data);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch details.', 'error');
      setShowDetailModal(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const viewSupplierDetails = async (id) => {
    setDetailType('supplier');
    setShowDetailModal(true);
    setDetailLoading(true);
    setDetailData(null);
    try {
      const res = await api.get(`/api/v1/finance/payables/suppliers/${id}`);
      setDetailData(res.data);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch details.', 'error');
      setShowDetailModal(false);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t("receivables_payables", "Receivables & Payables")}</h4>
          <p className="mb-0">{t("track_debts_desc", "Track who owes you money and who you owe money to.")}</p>
        </div>
      </div>

      <Card border="light" className="shadow-sm mb-4">
        <Card.Body>
          <Tabs activeKey={key} onSelect={(k) => setKey(k)} className="mb-4">
            {/* RECEIVABLES TAB */}
            <Tab eventKey="receivables" title={<span>{t("receivables_customers", "Receivables (Customers)")} <Badge bg="success" className="ms-2">{receivables.length}</Badge></span>}>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0 text-success">{t("total_expected", "Total Expected")}: {rTotal ? parseFloat(rTotal).toLocaleString() : '0.00'}</h5>
                <InputGroup style={{ maxWidth: '300px' }}>
                  <Form.Control type="text" placeholder={t("search_customer_placeholder", "Search customer...")} value={rSearch} onChange={handleRSearch} />
                  <Button variant="primary" onClick={applyRSearch}><FontAwesomeIcon icon={faSearch} /></Button>
                </InputGroup>
              </div>

              <Table responsive className="align-items-center table-flush">
                <thead className="thead-light">
                  <tr>
                    <th>{t("customer_name", "Customer Name")}</th>
                    <th>{t("code", "Code")}</th>
                    <th>{t("phone", "Phone")}</th>
                    <th className="text-end">{t("outstanding_balance", "Outstanding Balance")}</th>
                    <th className="text-end">{t("actions", "Actions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {rLoading ? (
                    <tr><td colSpan="5" className="text-center">{t("loading", "Loading...")}</td></tr>
                  ) : receivables.length === 0 ? (
                    <tr><td colSpan="5" className="text-center">{t("no_customer_debts", "No outstanding customer debts found.")}</td></tr>
                  ) : (
                    receivables.map(c => (
                      <tr key={c.customer_id}>
                        <td className="fw-bold">{c.name}</td>
                        <td>{c.customer_code}</td>
                        <td>{c.phone || '-'}</td>
                        <td className="text-end text-danger fw-bold">{parseFloat(c.outstanding_balance).toLocaleString()}</td>
                        <td className="text-end">
                          <Button variant="info" size="sm" onClick={() => viewCustomerDetails(c.customer_id)}>
                            <FontAwesomeIcon icon={faEye} className="me-1" /> {t("view_unpaid_sales", "View Unpaid Sales")}
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>

              {rTotalPages > 1 && (
                <div className="mt-3 d-flex justify-content-center">
                  <Pagination>
                    <Pagination.Prev onClick={() => setRPage(rPage - 1)} disabled={rPage === 1} />
                    <Pagination.Item active>{rPage}</Pagination.Item>
                    <Pagination.Next onClick={() => setRPage(rPage + 1)} disabled={rPage === rTotalPages} />
                  </Pagination>
                </div>
              )}
            </Tab>

            {/* PAYABLES TAB */}
            <Tab eventKey="payables" title={<span>{t("payables_suppliers", "Payables (Suppliers)")} <Badge bg="danger" className="ms-2">{payables.length}</Badge></span>}>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0 text-danger">{t("total_owed", "Total Owed")}: {pTotal ? parseFloat(pTotal).toLocaleString() : '0.00'}</h5>
                <InputGroup style={{ maxWidth: '300px' }}>
                  <Form.Control type="text" placeholder={t("search_supplier_placeholder", "Search supplier...")} value={pSearch} onChange={handlePSearch} />
                  <Button variant="primary" onClick={applyPSearch}><FontAwesomeIcon icon={faSearch} /></Button>
                </InputGroup>
              </div>

              <Table responsive className="align-items-center table-flush">
                <thead className="thead-light">
                  <tr>
                    <th>{t("supplier_name", "Supplier Name")}</th>
                    <th>{t("code", "Code")}</th>
                    <th>{t("phone", "Phone")}</th>
                    <th className="text-end">{t("outstanding_balance", "Outstanding Balance")}</th>
                    <th className="text-end">{t("actions", "Actions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {pLoading ? (
                    <tr><td colSpan="5" className="text-center">{t("loading", "Loading...")}</td></tr>
                  ) : payables.length === 0 ? (
                    <tr><td colSpan="5" className="text-center">{t("no_supplier_debts", "No outstanding supplier debts found.")}</td></tr>
                  ) : (
                    payables.map(s => (
                      <tr key={s.supplier_id}>
                        <td className="fw-bold">{s.name}</td>
                        <td>{s.supplier_code}</td>
                        <td>{s.phone || '-'}</td>
                        <td className="text-end text-danger fw-bold">{parseFloat(s.outstanding_balance).toLocaleString()}</td>
                        <td className="text-end">
                          <Button variant="info" size="sm" onClick={() => viewSupplierDetails(s.supplier_id)}>
                            <FontAwesomeIcon icon={faEye} className="me-1" /> {t("view_unpaid_purchases", "View Unpaid Purchases")}
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>

              {pTotalPages > 1 && (
                <div className="mt-3 d-flex justify-content-center">
                  <Pagination>
                    <Pagination.Prev onClick={() => setPPage(pPage - 1)} disabled={pPage === 1} />
                    <Pagination.Item active>{pPage}</Pagination.Item>
                    <Pagination.Next onClick={() => setPPage(pPage + 1)} disabled={pPage === pTotalPages} />
                  </Pagination>
                </div>
              )}
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* Details Modal */}
      <Modal as={Modal.Dialog} centered show={showDetailModal} onHide={() => setShowDetailModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {detailType === 'customer' ? t('unpaid_sales', 'Unpaid Sales') : t('unpaid_purchases', 'Unpaid Purchases')}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {detailLoading ? (
            <div className="text-center p-4">{t('loading_details', 'Loading details...')}</div>
          ) : detailData ? (
            <div>
              <h5 className="mb-4">
                {detailType === 'customer' ? detailData.customer_name : detailData.supplier_name}
                <span className="float-end text-danger">{t('total_due', 'Total Due')}: {parseFloat(detailData.total_outstanding).toLocaleString()}</span>
              </h5>
              
              <Table responsive hover size="sm">
                <thead className="thead-light">
                  <tr>
                    <th>{t("date", "Date")}</th>
                    <th>{t("invoice_no", "Invoice / Ref")}</th>
                    <th className="text-end">{t("total_due", "Total Amount")}</th>
                    <th className="text-end">{t("amount_paid", "Amount Paid")}</th>
                    <th className="text-end">{t("balance", "Balance Due")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(detailType === 'customer' ? detailData.sales : detailData.purchases).length === 0 ? (
                    <tr><td colSpan="5" className="text-center">{t("all_clear", "All clear!")}</td></tr>
                  ) : (
                    (detailType === 'customer' ? detailData.sales : detailData.purchases).map(item => (
                      <tr key={item.sale_id || item.purchase_id}>
                        <td>{new Date(item.sale_date || item.purchase_date).toLocaleDateString()}</td>
                        <td>{item.invoice_number || item.purchase_number}</td>
                        <td className="text-end">{parseFloat(item.total_amount).toLocaleString()}</td>
                        <td className="text-end text-success">{parseFloat(item.amount_paid).toLocaleString()}</td>
                        <td className="text-end text-danger fw-bold">{parseFloat(item.balance_due).toLocaleString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>
            </div>
          ) : (
            <div className="text-center p-4 text-danger">{t("error_loading", "Failed to load data.")}</div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>{t("close", "Close")}</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};
