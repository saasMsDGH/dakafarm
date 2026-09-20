import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";

export default () => {
  const { t } = useTranslation();
  
  const [statusList, setStatusList] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/inventory/stock/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setStatusList(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch inventory status:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [page, searchTerm]);

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('inventory_status', 'Inventory Status')}</h4>
        </div>
      </div>

      <div className="table-settings mb-4">
        <Row className="justify-content-between align-items-center">
          <Col xs={8} md={6} lg={3} xl={4}>
            <InputGroup>
              <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
              <Form.Control 
                type="text" 
                placeholder={t('search', 'Search...')} 
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
              />
            </InputGroup>
          </Col>
        </Row>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">{t('product', 'Product')}</th>
                <th className="border-bottom">{t('current_stock', 'Current Stock')}</th>
                <th className="border-bottom">{t('reorder_level', 'Reorder Level')}</th>
                <th className="border-bottom">{t('status', 'Status')}</th>
                <th className="border-bottom">{t('date', 'Last Updated')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="5" className="text-center">Loading...</td></tr>
              ) : statusList.length === 0 ? (
                <tr><td colSpan="5" className="text-center">No inventory found</td></tr>
              ) : (
                statusList.map(item => (
                  <tr key={item.product_id}>
                    <td><span className="fw-normal">{item.product_name}</span></td>
                    <td><span className="fw-bold">{item.quantity} {item.unit_of_measure}</span></td>
                    <td><span className="fw-normal">{item.reorder_level} {item.unit_of_measure}</span></td>
                    <td>
                      {item.status === 'Low Stock' || item.status === 'Out of Stock' ? (
                        <Badge bg="danger" className="badge-lg">
                          <FontAwesomeIcon icon={faExclamationTriangle} className="me-1"/> 
                          {item.status}
                        </Badge>
                      ) : (
                        <Badge bg="success" className="badge-lg">
                          <FontAwesomeIcon icon={faCheckCircle} className="me-1"/> 
                          {item.status}
                        </Badge>
                      )}
                    </td>
                    <td><span className="fw-normal">{item.updated_at ? new Date(item.updated_at).toLocaleString() : '-'}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
          
          <Card.Footer className="px-3 border-0 d-flex flex-column flex-lg-row align-items-center justify-content-between">
            <Pagination className="mb-2 mb-lg-0">
              <Pagination.Prev disabled={page === 1} onClick={() => setPage(page - 1)}>
                {t('previous', 'Previous')}
              </Pagination.Prev>
              <Pagination.Item active>{page}</Pagination.Item>
              <Pagination.Next disabled={page === totalPages || totalPages === 0} onClick={() => setPage(page + 1)}>
                {t('next', 'Next')}
              </Pagination.Next>
            </Pagination>
          </Card.Footer>
        </Card.Body>
      </Card>
    </>
  );
};
