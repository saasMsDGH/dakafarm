import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEye, faMoneyBillWave, faSearch, faTrash } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [sales, setSales] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // Modals state
  const [showNewSaleModal, setShowNewSaleModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  
  const [currentSale, setCurrentSale] = useState(null);
  
  // New Sale State
  const [newSale, setNewSale] = useState({
    customer_id: '',
    discount: 0,
    amount_paid: 0,
    payment_method: 'Cash'
  });
  const [cartItems, setCartItems] = useState([]);
  const [cartInput, setCartInput] = useState({
    product_id: '',
    quantity: 1,
    unit_price: 0
  });

  // Payment State
  const [paymentInput, setPaymentInput] = useState({
    amount: 0,
    payment_method: 'Cash'
  });

  const fetchSales = async (currentPage = page) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/pos/sales/?page=${currentPage}&limit=10`);
      setSales(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error(error);
      Swal.fire('Error', 'Failed to load sales', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchDependencies = async () => {
    try {
      const custRes = await api.get(`/api/v1/pos/customers/?limit=1000`);
      setCustomers(custRes.data.items);
      const prodRes = await api.get(`/api/v1/inventory/products/?limit=1000`);
      setProducts(prodRes.data.items);
    } catch (error) {
      console.error("Failed to load customers or products", error);
    }
  };

  useEffect(() => {
    fetchSales();
    fetchDependencies();
  }, []);

  const handlePageChange = (newPage) => {
    fetchSales(newPage);
  };

  // ----- NEW SALE LOGIC -----
  const handleProductSelect = (e) => {
    const prodId = parseInt(e.target.value);
    const prod = products.find(p => p.id === prodId);
    if (prod) {
      setCartInput({
        product_id: prodId,
        quantity: 1,
        unit_price: prod.selling_price
      });
    } else {
      setCartInput({ product_id: '', quantity: 1, unit_price: 0 });
    }
  };

  const addToCart = () => {
    if (!cartInput.product_id || cartInput.quantity <= 0) return;
    const prod = products.find(p => p.id === cartInput.product_id);
    
    // Check stock
    if (cartInput.quantity > prod.current_stock) {
      Swal.fire('Warning', `Not enough stock! Only ${prod.current_stock} available.`, 'warning');
      return;
    }

    const newItem = {
      product_id: cartInput.product_id,
      product_name: prod.name,
      quantity: parseFloat(cartInput.quantity),
      unit_price: parseFloat(cartInput.unit_price)
    };
    setCartItems([...cartItems, newItem]);
    
    // Reset input
    setCartInput({ product_id: '', quantity: 1, unit_price: 0 });
  };

  const removeFromCart = (index) => {
    const newItems = [...cartItems];
    newItems.splice(index, 1);
    setCartItems(newItems);
  };

  const cartSubtotal = cartItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  const cartTotal = cartSubtotal - (parseFloat(newSale.discount) || 0);

  const submitNewSale = async (e) => {
    e.preventDefault();
    if (cartItems.length === 0) {
      Swal.fire('Error', 'Cart is empty!', 'error');
      return;
    }
    if (!newSale.customer_id) {
      Swal.fire('Error', 'Select a customer!', 'error');
      return;
    }

    try {
      const payload = {
        customer_id: parseInt(newSale.customer_id),
        discount: parseFloat(newSale.discount) || 0,
        amount_paid: parseFloat(newSale.amount_paid) || 0,
        payment_method: newSale.payment_method,
        items: cartItems.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        }))
      };

      const res = await api.post(`/api/v1/pos/sales/`, payload);
      Swal.fire('Success', 'Sale created successfully!', 'success');
      setShowNewSaleModal(false);
      setCartItems([]);
      setNewSale({ customer_id: '', discount: 0, amount_paid: 0, payment_method: 'Cash' });
      fetchSales();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create sale', 'error');
    }
  };

  // ----- VIEW SALE LOGIC -----
  const handleViewSale = async (saleId) => {
    try {
      const res = await api.get(`/api/v1/pos/sales/${saleId}`);
      setCurrentSale(res.data);
      setShowViewModal(true);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch sale details', 'error');
    }
  };

  // ----- ADD PAYMENT LOGIC -----
  const handleAddPaymentClick = (sale) => {
    setCurrentSale(sale);
    const balance = parseFloat(sale.total_amount) - parseFloat(sale.amount_paid);
    setPaymentInput({ amount: balance, payment_method: 'Cash' });
    setShowPaymentModal(true);
  };

  const submitPayment = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        sale_id: currentSale.id,
        amount: parseFloat(paymentInput.amount),
        payment_method: paymentInput.payment_method
      };
      await api.post(`/api/v1/pos/sales/${currentSale.id}/payments`, payload);
      Swal.fire('Success', 'Payment recorded successfully!', 'success');
      setShowPaymentModal(false);
      fetchSales();
      // Update current sale if view modal is open
      if (showViewModal) {
          handleViewSale(currentSale.id);
      }
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to add payment', 'error');
    }
  };

  const handlePrintReceipt = () => {
    if (!currentSale) return;
    
    const printWindow = window.open('', '_blank', 'width=400,height=600');
    
    const itemsHtml = currentSale.items.map(item => `
      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
        <div style="flex: 2; text-align: left; padding-right: 5px;">
          <div>${getProductName(item.product_id)}</div>
          <div style="color: #555; font-size: 12px;">@ TSh ${parseFloat(item.unit_price).toLocaleString()}</div>
        </div>
        <div style="flex: 1; text-align: center;">${item.quantity}</div>
        <div style="flex: 1; text-align: right;">${parseFloat(item.total_amount).toLocaleString()}</div>
      </div>
    `).join('');

    const paymentMethod = currentSale.payments && currentSale.payments.length > 0 
      ? currentSale.payments[0].payment_method 
      : (currentSale.payment_status === 'PAID' ? 'Cash' : 'Credit');

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Receipt - ${currentSale.invoice_number}</title>
          <style>
            @page {
              margin: 0;
              size: 80mm 297mm;
            }
            body { 
              font-family: Arial, sans-serif;
              font-size: 14px; 
              color: #000; 
              margin: 0; 
              padding: 0;
              display: flex;
              justify-content: center;
            }
            .receipt-container {
              width: 300px;
              padding: 10px;
              box-sizing: border-box;
            }
            .text-center { text-align: center; }
            .text-right { text-align: right; }
            .fw-bold { font-weight: bold; }
            .divider { text-align: center; margin: 5px 0; font-family: monospace; letter-spacing: -1px; overflow: hidden; white-space: nowrap; }
            
            h1 { font-size: 28px; font-weight: 900; margin: 5px 0; }
            p { margin: 2px 0; font-size: 14px; }
            .header-text { font-size: 12px; font-weight: bold; margin-bottom: 10px; }
            
            .flex-between { display: flex; justify-content: space-between; margin: 2px 0; }
          </style>
        </head>
        <body>
          <div class="receipt-container">
            <div class="text-center header-text" style="margin-top: 10px;">
              *** START OF SALES RECEIPT ***
            </div>
            
            <div class="text-center">
              <h1>AMAS FARM</h1>
              <p>Dar es Salaam</p>
              <p>Tel: 0712 345 678</p>
              <p>info@amasfarm.com</p>
            </div>
            
            <div class="divider">----------------------------------------------------</div>
            
            <div>
              <p>Receipt:<br/>${currentSale.invoice_number}</p>
              <p>Date: ${new Date(currentSale.sale_date).toLocaleString()}</p>
              <p>Cashier: Admin</p>
              <p>Customer: ${getCustomerName(currentSale.customer_id)}</p>
              <p>Payment: ${paymentMethod}</p>
            </div>
            
            <div class="divider">----------------------------------------------------</div>
            
            <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 5px;">
              <div style="flex: 2; text-align: left;">ITEM</div>
              <div style="flex: 1; text-align: center;">QTY</div>
              <div style="flex: 1; text-align: right;">AMOUNT</div>
            </div>
            
            ${itemsHtml}
            
            <div class="divider">----------------------------------------------------</div>
            
            <div class="flex-between">
              <span>SUBTOTAL</span>
              <span>TSh ${parseFloat(currentSale.subtotal).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>DISCOUNT</span>
              <span>TSh ${parseFloat(currentSale.discount).toLocaleString()}</span>
            </div>
            <div class="flex-between" style="font-size: 16px; font-weight: 900; margin: 5px 0;">
              <span>TOTAL</span>
              <span>TSh ${parseFloat(currentSale.total_amount).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>CASH / PAID</span>
              <span>TSh ${parseFloat(currentSale.amount_paid).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>BALANCE</span>
              <span>TSh ${(parseFloat(currentSale.total_amount) - parseFloat(currentSale.amount_paid)).toLocaleString()}</span>
            </div>
            
            <br/>
            <div class="text-center">
              <p style="font-weight: bold;">RECEIPT VERIFICATION CODE</p>
              <p style="word-break: break-all;">${currentSale.invoice_number}</p>
            </div>
            
            <br/>
            
            <div class="text-center">
              <h2 style="margin: 0; font-size: 20px; font-weight: 900;">THANK YOU!</h2>
              <p>Glad to see you again!</p>
            </div>
            
            <div class="text-center header-text" style="margin-top: 15px;">
              *** END OF SALES RECEIPT ***
            </div>
          </div>
          
          <script>
            window.onload = function() { 
              setTimeout(function() {
                window.print(); 
                window.close(); 
              }, 300);
            }
          </script>
        </body>
      </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
  };

  const getStatusBadge = (status) => {
    if (status === 'PAID') return <Badge bg="success">PAID</Badge>;
    if (status === 'PARTIAL') return <Badge bg="warning">PARTIAL</Badge>;
    return <Badge bg="danger">UNPAID</Badge>;
  };

  const getCustomerName = (id) => {
    const c = customers.find(c => c.id === id);
    return c ? c.name : `ID: ${id}`;
  };
  
  const getProductName = (id) => {
      const p = products.find(p => p.id === id);
      return p ? p.name : `Product ID: ${id}`;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('sales', 'Sales & Invoices')}</h4>
          <p className="mb-0">Manage point of sale transactions, credit limits, and receipts.</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => setShowNewSaleModal(true)}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> New Sale
          </Button>
        </div>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">Invoice No</th>
                <th className="border-bottom">Customer</th>
                <th className="border-bottom">Date</th>
                <th className="border-bottom">Total Amount</th>
                <th className="border-bottom">Amount Paid</th>
                <th className="border-bottom">Status</th>
                <th className="border-bottom">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : sales.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No sales found.</td></tr>
              ) : (
                sales.map(s => (
                  <tr key={s.id}>
                    <td><span className="fw-bold">{s.invoice_number}</span></td>
                    <td><span className="fw-normal">{getCustomerName(s.customer_id)}</span></td>
                    <td><span className="fw-normal">{new Date(s.sale_date).toLocaleDateString()}</span></td>
                    <td><span className="fw-bold text-success">{parseFloat(s.total_amount).toLocaleString()}</span></td>
                    <td><span className="fw-bold">{parseFloat(s.amount_paid).toLocaleString()}</span></td>
                    <td>{getStatusBadge(s.payment_status)}</td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleViewSale(s.id)}>
                        <FontAwesomeIcon icon={faEye} /> View
                      </Button>
                      {s.payment_status !== 'PAID' && (
                        <Button variant="success" size="sm" onClick={() => handleAddPaymentClick(s)}>
                          <FontAwesomeIcon icon={faMoneyBillWave} /> Pay
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
          
          <Card.Footer className="px-3 border-0 d-lg-flex align-items-center justify-content-between">
            <Pagination className="mb-2 mb-lg-0">
              <Pagination.Prev onClick={() => handlePageChange(page - 1)} disabled={page === 1} />
              {[...Array(totalPages)].map((_, i) => (
                <Pagination.Item key={i + 1} active={i + 1 === page} onClick={() => handlePageChange(i + 1)}>
                  {i + 1}
                </Pagination.Item>
              ))}
              <Pagination.Next onClick={() => handlePageChange(page + 1)} disabled={page === totalPages || totalPages === 0} />
            </Pagination>
          </Card.Footer>
        </Card.Body>
      </Card>

      {/* NEW SALE MODAL */}
      <Modal as={Modal.Dialog} size="lg" centered show={showNewSaleModal} onHide={() => setShowNewSaleModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Point of Sale Checkout</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row>
            <Col md={12} className="mb-3">
              <Form.Group>
                <Form.Label>Customer *</Form.Label>
                <Form.Select 
                  value={newSale.customer_id} 
                  onChange={(e) => setNewSale({...newSale, customer_id: e.target.value})}
                >
                  <option value="">-- Select Customer --</option>
                  {customers.map(c => (
                    <option key={c.id} value={c.id}>{c.name} ({c.business_type || 'Retail'}) - Limit: {parseFloat(c.credit_limit).toLocaleString()}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <Card border="light" className="mb-3 p-3 bg-light">
            <h6 className="mb-3">Add Items to Cart</h6>
            <Row className="align-items-end">
              <Col md={5}>
                <Form.Group>
                  <Form.Label>Product</Form.Label>
                  <Form.Select value={cartInput.product_id} onChange={handleProductSelect}>
                    <option value="">-- Select Product --</option>
                    {products.filter(p => p.is_active).map(p => (
                      <option key={p.id} value={p.id}>{p.name} (Stock: {p.current_stock})</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={2}>
                <Form.Group>
                  <Form.Label>Qty</Form.Label>
                  <Form.Control type="number" step="0.01" min="0.01" value={cartInput.quantity} onChange={(e) => setCartInput({...cartInput, quantity: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Unit Price</Form.Label>
                  <Form.Control type="number" step="0.01" value={cartInput.unit_price} readOnly disabled />
                </Form.Group>
              </Col>
              <Col md={2}>
                <Button variant="secondary" className="w-100" onClick={addToCart}>Add</Button>
              </Col>
            </Row>
          </Card>

          <Table size="sm" bordered hover className="mb-3">
            <thead className="thead-light">
              <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Total</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cartItems.length === 0 ? (
                <tr><td colSpan="5" className="text-center text-muted">Cart is empty</td></tr>
              ) : (
                cartItems.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.product_name}</td>
                    <td>{item.quantity}</td>
                    <td>{item.unit_price.toLocaleString()}</td>
                    <td>{(item.quantity * item.unit_price).toLocaleString()}</td>
                    <td>
                      <Button variant="link" className="text-danger p-0" onClick={() => removeFromCart(idx)}>
                        <FontAwesomeIcon icon={faTrash} />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>

          <Row>
            <Col md={6}></Col>
            <Col md={6}>
              <Card border="light" className="p-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Subtotal:</span>
                  <span className="fw-bold">{cartSubtotal.toLocaleString()}</span>
                </div>
                <Form.Group className="d-flex justify-content-between align-items-center mb-2">
                  <span className="me-2">Discount:</span>
                  <Form.Control type="number" step="0.01" size="sm" style={{ width: '120px' }} value={newSale.discount} onChange={(e) => setNewSale({...newSale, discount: e.target.value})} />
                </Form.Group>
                <div className="d-flex justify-content-between mb-3 border-bottom pb-2">
                  <span className="fw-bold h5">Total Due:</span>
                  <span className="fw-bold h5 text-danger">{cartTotal.toLocaleString()}</span>
                </div>
                <Form.Group className="d-flex justify-content-between align-items-center mb-2">
                  <span className="me-2">Amount Paid:</span>
                  <Form.Control type="number" step="0.01" size="sm" style={{ width: '120px' }} value={newSale.amount_paid} onChange={(e) => setNewSale({...newSale, amount_paid: e.target.value})} />
                </Form.Group>
                <Form.Group className="d-flex justify-content-between align-items-center mb-2">
                  <span className="me-2">Payment Method:</span>
                  <Form.Select size="sm" style={{ width: '120px' }} value={newSale.payment_method} onChange={(e) => setNewSale({...newSale, payment_method: e.target.value})}>
                    <option value="Cash">Cash</option>
                    <option value="Mobile Money">Mobile Money</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                  </Form.Select>
                </Form.Group>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewSaleModal(false)}>Cancel</Button>
          <Button variant="success" onClick={submitNewSale}>Confirm Sale</Button>
        </Modal.Footer>
      </Modal>

      {/* VIEW INVOICE/RECEIPT MODAL */}
      <Modal as={Modal.Dialog} size="lg" centered show={showViewModal} onHide={() => setShowViewModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Invoice Details</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-light p-4" style={{ fontFamily: 'monospace' }}>
          {currentSale && (
            <div className="bg-white p-4 border shadow-sm">
              <div className="text-center mb-4">
                <h4 className="mb-0">AMAS FARM</h4>
                {currentSale.payment_status === 'PAID' ? <h5>SALES RECEIPT</h5> : <h5>INVOICE</h5>}
                <small>Receipt/Invoice #: {currentSale.invoice_number}</small>
              </div>
              <Row className="mb-4">
                <Col>
                  <strong>Customer:</strong> {getCustomerName(currentSale.customer_id)}<br/>
                  <strong>Date:</strong> {new Date(currentSale.sale_date).toLocaleString()}<br/>
                  <strong>Payment Status:</strong> {currentSale.payment_status}
                </Col>
              </Row>
              <Table bordered size="sm">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {currentSale.items?.map((item, idx) => (
                    <tr key={idx}>
                      <td>{getProductName(item.product_id)}</td>
                      <td>{item.quantity}</td>
                      <td>{parseFloat(item.unit_price).toLocaleString()}</td>
                      <td>{parseFloat(item.total_amount).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <Row className="text-end mt-3">
                <Col>
                  <p className="mb-1">Subtotal: <strong>{parseFloat(currentSale.subtotal).toLocaleString()}</strong></p>
                  <p className="mb-1">Discount: <strong>{parseFloat(currentSale.discount).toLocaleString()}</strong></p>
                  <h5 className="mt-2 text-danger">TOTAL DUE: {parseFloat(currentSale.total_amount).toLocaleString()}</h5>
                </Col>
              </Row>

              {/* Payments Section */}
              {currentSale.payments && currentSale.payments.length > 0 && (
                <div className="mt-4 border-top pt-3">
                  <h6>Payment History</h6>
                  <Table size="sm" className="text-muted">
                    <thead>
                      <tr>
                        <th>Receipt No</th>
                        <th>Date</th>
                        <th>Method</th>
                        <th>Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentSale.payments.map((p, idx) => (
                        <tr key={idx}>
                          <td>{p.receipt_number}</td>
                          <td>{new Date(p.payment_date).toLocaleString()}</td>
                          <td>{p.payment_method}</td>
                          <td className="fw-bold">{parseFloat(p.amount).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                  <h6 className="text-end text-success mt-2">Total Paid: {parseFloat(currentSale.amount_paid).toLocaleString()}</h6>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          {currentSale && currentSale.payment_status !== 'PAID' && (
            <Button variant="success" onClick={() => handleAddPaymentClick(currentSale)}>
              <FontAwesomeIcon icon={faMoneyBillWave} className="me-2" /> Add Payment
            </Button>
          )}
          <Button variant="secondary" onClick={() => setShowViewModal(false)}>Close</Button>
          <Button variant="info" onClick={handlePrintReceipt}>Print Receipt (Small)</Button>
          <Button variant="primary" onClick={() => window.print()}>Print Invoice (A4)</Button>
        </Modal.Footer>
      </Modal>

      {/* ADD PAYMENT MODAL */}
      <Modal as={Modal.Dialog} centered show={showPaymentModal} onHide={() => setShowPaymentModal(false)}>
        <Form onSubmit={submitPayment}>
          <Modal.Header closeButton>
            <Modal.Title>Add Payment</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {currentSale && (
              <div className="mb-3 text-muted">
                Invoice: <strong>{currentSale.invoice_number}</strong><br/>
                Total Due: <strong>{parseFloat(currentSale.total_amount).toLocaleString()}</strong><br/>
                Remaining Balance: <strong className="text-danger">
                  {(parseFloat(currentSale.total_amount) - parseFloat(currentSale.amount_paid)).toLocaleString()}
                </strong>
              </div>
            )}
            <Form.Group className="mb-3">
              <Form.Label>Payment Amount *</Form.Label>
              <Form.Control type="number" step="0.01" value={paymentInput.amount} onChange={(e) => setPaymentInput({...paymentInput, amount: e.target.value})} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Payment Method *</Form.Label>
              <Form.Select value={paymentInput.payment_method} onChange={(e) => setPaymentInput({...paymentInput, payment_method: e.target.value})} required>
                <option value="Cash">Cash</option>
                <option value="Mobile Money">Mobile Money</option>
                <option value="Bank Transfer">Bank Transfer</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>Cancel</Button>
            <Button variant="primary" type="submit">Save Payment</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};




