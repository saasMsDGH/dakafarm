import { useTranslation } from 'react-i18next';
import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faFilter } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Form, InputGroup, Pagination, Badge, Button } from '@themesberg/react-bootstrap';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Pagination and Filtering State
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    transaction_type: '',
    direction: '',
    date_from: '',
    date_to: ''
  });

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      let query = `/api/v1/finance/transactions/?page=${page}&limit=20`;
      if (searchTerm) query += `&search=${searchTerm}`;
      if (filters.transaction_type) query += `&transaction_type=${filters.transaction_type}`;
      if (filters.direction) query += `&direction=${filters.direction}`;
      if (filters.date_from) query += `&date_from=${moment(filters.date_from).startOf('day').toISOString()}`;
      if (filters.date_to) query += `&date_to=${moment(filters.date_to).endOf('day').toISOString()}`;

      const res = await api.get(query);
      setTransactions(res.data.items || res.data);
      setTotalPages(res.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch transactions", error);
      Swal.fire('Error', 'Failed to load general ledger transactions.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page]);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = () => {
    setPage(1);
    fetchTransactions();
  };

  const clearFilters = () => {
    setSearchTerm('');
    setFilters({
      transaction_type: '',
      direction: '',
      date_from: '',
      date_to: ''
    });
    setPage(1);
    // Setting state is async, so we wait for the next render or call explicitly
    setTimeout(() => {
      fetchTransactions();
    }, 100);
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t("general_ledger", "General Ledger")}</h4>
          <p className="mb-0">{t("general_ledger_desc", "A master list of all financial transactions across the farm.")}</p>
        </div>
      </div>

      <Card border="light" className="shadow-sm mb-4">
        <Card.Body>
          <Row className="mb-3">
            <Col md={3}>
              <InputGroup>
                <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
                <Form.Control type="text" placeholder={t("search_ref_desc", "Search ref or description...")} value={searchTerm} onChange={handleSearch} />
              </InputGroup>
            </Col>
            <Col md={2}>
              <Form.Select name="transaction_type" value={filters.transaction_type} onChange={handleFilterChange}>
                <option value="">{t("all_types", "All Types")}</option>
                <option value="SALE">Sale</option>
                <option value="PURCHASE">Purchase</option>
                <option value="EXPENSE">Expense</option>
                <option value="ASSET">Asset</option>
                <option value="PAYROLL">Payroll</option>
                <option value="TRANSFER">Transfer</option>
                <option value="EQUITY">Equity</option>
              </Form.Select>
            </Col>
            <Col md={2}>
              <Form.Select name="direction" value={filters.direction} onChange={handleFilterChange}>
                <option value="">{t("all_directions", "All Directions")}</option>
                <option value="IN">{t("money_in", "Money IN")}</option>
                <option value="OUT">{t("money_out", "Money OUT")}</option>
              </Form.Select>
            </Col>
            <Col md={2}>
              <Form.Control type="date" name="date_from" value={filters.date_from} onChange={handleFilterChange} placeholder="From Date" />
            </Col>
            <Col md={2}>
              <Form.Control type="date" name="date_to" value={filters.date_to} onChange={handleFilterChange} placeholder="To Date" />
            </Col>
            <Col md={1} className="d-flex align-items-end">
              <Button variant="primary" size="sm" onClick={applyFilters} className="w-100 me-2" title="Apply Filters">
                <FontAwesomeIcon icon={faFilter} />
              </Button>
              <Button variant="outline-secondary" size="sm" onClick={clearFilters} className="w-100">
                {t("clear", "Clear")}
              </Button>
            </Col>
          </Row>

          <Table responsive className="align-items-center table-flush">
            <thead className="thead-light">
              <tr>
                <th scope="col">{t("date", "Date")}</th>
                <th scope="col">{t("ref_number", "Ref No.")}</th>
                <th scope="col">{t("payment_account", "Account")}</th>
                <th scope="col">{t("type", "Type")}</th>
                <th scope="col">{t("description", "Description")}</th>
                <th scope="col" className="text-end">{t("money_in", "Money IN")}</th>
                <th scope="col" className="text-end">{t("money_out", "Money OUT")}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">{t("loading", "Loading transactions...")}</td></tr>
              ) : transactions.length === 0 ? (
                <tr><td colSpan="7" className="text-center">{t("no_transactions", "No transactions found.")}</td></tr>
              ) : (
                transactions.map(txn => (
                  <tr key={txn.id}>
                    <td>{new Date(txn.created_at).toLocaleDateString()}</td>
                    <td><Badge bg="secondary">{txn.reference_number || '-'}</Badge></td>
                    <td><span className="fw-bold">{txn.account ? txn.account.name : `Account ID: ${txn.account_id}`}</span></td>
                    <td>
                      <Badge bg={txn.transaction_type === 'SALE' ? 'success' : (txn.transaction_type === 'EXPENSE' || txn.transaction_type === 'PURCHASE') ? 'danger' : 'info'}>
                        {txn.transaction_type}
                      </Badge>
                    </td>
                    <td>
                      <div style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={txn.description}>
                        {txn.description}
                      </div>
                    </td>
                    <td className="text-end text-success fw-bold">
                      {txn.direction === 'IN' ? parseFloat(txn.amount).toLocaleString() : '-'}
                    </td>
                    <td className="text-end text-danger fw-bold">
                      {txn.direction === 'OUT' ? parseFloat(txn.amount).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>

          {totalPages > 1 && (
            <Card.Footer className="px-3 border-0 d-flex flex-column flex-lg-row align-items-center justify-content-between">
              <Pagination>
                <Pagination.Prev onClick={() => setPage(page - 1)} disabled={page === 1} />
                {[...Array(totalPages)].map((_, i) => (
                  <Pagination.Item key={i + 1} active={i + 1 === page} onClick={() => setPage(i + 1)}>
                    {i + 1}
                  </Pagination.Item>
                ))}
                <Pagination.Next onClick={() => setPage(page + 1)} disabled={page === totalPages} />
              </Pagination>
            </Card.Footer>
          )}
        </Card.Body>
      </Card>
    </>
  );
};
