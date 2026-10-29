import React, { useState, useEffect } from "react";
import Select from 'react-select';
import { useAuth } from '../../context/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEye, faMoneyBillWave, faSearch, faTrash } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [showProductModal, setShowProductModal] = useState(false);
  const [categories, setCategories] = useState([]);
  const [newProduct, setNewProduct] = useState({
    name: '',
    category_id: '',
    unit_of_measure: '',
    unit_price: 0,
    selling_price: 0,
    current_stock: 0,
    is_active: true
  });

  const handleCreateProduct = async () => {
    if (!newProduct.name || !newProduct.category_id || !newProduct.unit_of_measure) {
      Swal.fire('Error', 'Please fill all required fields', 'error');
      return;
    }
    try {
      const payload = {
        ...newProduct,
        category_id: parseInt(newProduct.category_id),
        unit_price: parseFloat(newProduct.unit_price) || 0,
        selling_price: parseFloat(newProduct.selling_price) || 0,
      };
      const response = await api.post('/api/v1/inventory/products/', payload);
      setProducts([response.data, ...products]);
      setShowProductModal(false);
      setNewProduct({ name: '', category_id: '', unit_of_measure: '', unit_price: 0, selling_price: 0, current_stock: 0, is_active: true });
      Swal.fire('Success', 'Product created successfully', 'success');
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create product', 'error');
    }
  };
  const [totalPages, setTotalPages] = useState(1);
  
  // Modals state
  const [showNewPurchaseModal, setShowNewPurchaseModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  
  const [currentPurchase, setCurrentPurchase] = useState(null);
  
  // New Purchase State
  const [newPurchase, setNewPurchase] = useState({
    supplier_id: '',
    discount: '', amount_paid: '',
    payment_method: 'Cash',
    account_id: ''
  });
  const [cartItems, setCartItems] = useState([]);
  const [productSearch, setProductSearch] = useState('');
  const [cartInput, setCartInput] = useState({
    product_id: '',
    quantity: 1,
    unit_price: 0
  });

  // Payment State
  const [paymentInput, setPaymentInput] = useState({
    amount: 0,
    payment_method: 'Cash',
    account_id: ''
  });

  const [accounts, setAccounts] = useState([]);

  const fetchPurchases = async (currentPage = page) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/pos/purchases/?page=${currentPage}&limit=10`);
      setPurchases(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error(error);
      Swal.fire('Error', 'Failed to load purchases', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchDependencies = async () => {
    try {
      const suppRes = await api.get(`/api/v1/pos/suppliers/?limit=1000`);
      setSuppliers(suppRes.data.items);
      const prodRes = await api.get(`/api/v1/inventory/products/?limit=1000`);
      setProducts(prodRes.data.items);
      const catRes = await api.get('/api/v1/inventory/product-categories/?limit=100');
      setCategories(catRes.data.items || catRes.data);
      const accRes = await api.get(`/api/v1/finance/accounts/?limit=1000`);
      setAccounts(accRes.data.items || accRes.data);
    } catch (error) {
      console.error("Failed to load dependencies", error);
    }
  };

  useEffect(() => {
    fetchPurchases();
    fetchDependencies();
  }, []);

  const handlePageChange = (newPage) => {
    fetchPurchases(newPage);
  };

  // ----- NEW PURCHASE LOGIC -----
    const handleAddToCart = (product) => {
    
    const existing = cartItems.find(item => item.product_id === product.id);
    if (existing) {
      
      setCartItems(cartItems.map(item => 
        item.product_id === product.id ? {...item, quantity: (parseFloat(item.quantity) || 0) + 1} : item
      ));
    } else {
      setCartItems([...cartItems, {
        product_id: product.id,
        name: product.name,
        quantity: 1,
        unit_price: parseFloat(product.unit_price || 0),
        new_selling_price: parseFloat(product.selling_price || 0)
      }]);
    }
  };

  const filteredProducts = products.filter(p => p.name.toLowerCase().includes(productSearch.toLowerCase()));

  const supplierOptions = suppliers.map(c => ({
    value: c.id,
    label: c.name
  }));

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
  const cartTotal = cartSubtotal - (parseFloat(newPurchase.discount) || 0);

  const submitNewPurchase = async (e) => {
    e.preventDefault();
    if (cartItems.length === 0) {
      Swal.fire('Error', 'Cart is empty!', 'error');
      return;
    }
    if (!newPurchase.supplier_id) {
      Swal.fire('Error', 'Select a supplier!', 'error');
      return;
    }

    const amountPaid = parseFloat(newPurchase.amount_paid) || 0;
    if (amountPaid > 0 && !newPurchase.account_id) {
      Swal.fire('Error', 'Please select a Payment Account for the amount paid.', 'error');
      return;
    }

    try {
      const payload = {
        supplier_id: parseInt(newPurchase.supplier_id),
        discount: parseFloat(newPurchase.discount) || 0,
        amount_paid: amountPaid,
        payment_method: newPurchase.payment_method,
        account_id: amountPaid > 0 ? parseInt(newPurchase.account_id) : null,
        items: cartItems.map(item => ({
          product_id: item.product_id,
          quantity: parseFloat(item.quantity) || 0,
          unit_cost: item.unit_price,
          new_selling_price: item.new_selling_price
        }))
      };

      const res = await api.post(`/api/v1/pos/purchases/`, payload);
      Swal.fire('Success', 'Purchase created successfully!', 'success');
      setShowNewPurchaseModal(false);
      setCartItems([]);
      setNewPurchase({ supplier_id: '', discount: '', amount_paid: '', payment_method: 'Cash' });
      fetchPurchases();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create purchase', 'error');
    }
  };

  // ----- VIEW PURCHASE LOGIC -----
  const handleViewPurchase = async (purchaseId) => {
    try {
      const res = await api.get(`/api/v1/pos/purchases/${purchaseId}`);
      setCurrentPurchase(res.data);
      setShowViewModal(true);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch purchase details', 'error');
    }
  };

  // ----- ADD PAYMENT LOGIC -----
  const handleAddPaymentClick = (purchase) => {
    setCurrentPurchase(purchase);
    const balance = parseFloat(purchase.total_amount) - parseFloat(purchase.amount_paid);
    setPaymentInput({ amount: balance, payment_method: 'Cash' });
    setShowPaymentModal(true);
  };

  const handlePrintInvoice = () => {
    if (!currentPurchase) return;
    
    const printWindow = window.open('', '_blank', 'width=800,height=1000');
    
    const itemsHtml = currentPurchase.items.map(item => `
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;">${getProductName(item.product_id)}</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${item.quantity}</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${parseFloat(item.unit_price).toLocaleString()}</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${parseFloat(item.total_amount).toLocaleString()}</td>
      </tr>
    `).join('');

    let paymentsHtml = '';
    if (currentPurchase.payments && currentPurchase.payments.length > 0) {
      const paymentRows = currentPurchase.payments.map(p => `
        <tr>
          <td style="padding: 8px; border-bottom: 1px solid #eee;">${p.receipt_number}</td>
          <td style="padding: 8px; border-bottom: 1px solid #eee;">${new Date(p.payment_date).toLocaleString()}</td>
          <td style="padding: 8px; border-bottom: 1px solid #eee;">${p.payment_method}</td>
          <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">${parseFloat(p.amount).toLocaleString()}</td>
        </tr>
      `).join('');
      
      paymentsHtml = `
        <div style="margin-top: 30px;">
          <h4 style="color: #333; border-bottom: 2px solid #333; padding-bottom: 5px;">Payment History</h4>
          <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px;">
            <thead>
              <tr>
                <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd; color: #666;">RECEIPT NO</th>
                <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd; color: #666;">DATE</th>
                <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd; color: #666;">METHOD</th>
                <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd; color: #666;">AMOUNT</th>
              </tr>
            </thead>
            <tbody>
              ${paymentRows}
            </tbody>
          </table>
          <div style="text-align: right; margin-top: 15px; font-size: 16px; font-weight: bold; color: #28a745;">
            {t("total_paid", "Total Paid:")} ${parseFloat(currentPurchase.amount_paid).toLocaleString()}
          </div>
        </div>
      `;
    }

    const docTitle = currentPurchase.invoice_number;
    const titleType = currentPurchase.payment_status === 'PAID' ? '{t("purchases_receipt", "PURCHASES RECEIPT")}' : '{t("invoice", "INVOICE")}';

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${docTitle}</title>
          <style>
            @page {
              margin: 0; /* This removes the about:blank browser footer */
              size: A4 portrait;
            }
            body { 
              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
              font-size: 14px; 
              color: #333; 
              margin: 0; 
              padding: 20mm; /* Added padding here instead of @page margin */
            }
            .invoice-box {
              max-width: 800px;
              margin: auto;
              padding: 30px;
              border: 1px solid #eee;
              box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
            }
            @media print {
              .invoice-box {
                border: none;
                box-shadow: none;
                padding: 0;
              }
            }
            table { width: 100%; border-collapse: collapse; }
            .header-table td { padding-bottom: 20px; }
            .title { font-size: 45px; line-height: 45px; color: #333; font-weight: bold; }
            .invoice-details { text-align: right; }
            .invoice-details h2 { margin: 0; color: #555; }
            .item-table th { background: #f8f9fa; padding: 10px; text-align: left; border: 1px solid #ddd; color: #333; }
            .totals-box { width: 300px; float: right; margin-top: 20px; }
            .totals-box table td { padding: 5px 10px; border: none; text-align: right; }
            .totals-box table tr.total-row td { border-top: 2px solid #333; font-weight: bold; font-size: 18px; color: #d9534f; }
            .clear { clear: both; }
          </style>
        </head>
        <body>
          <div class="invoice-box">
            <table class="header-table">
              <tr>
                <td>
                  <div class="title">DAKAFARM</div>
                  <div style="color: #777; margin-top: 5px;">
                    Dar es Salaam<br>
                    Tel: 0712 345 678<br>
                    info@amasfarm.com
                  </div>
                </td>
                <td class="invoice-details">
                  <h2>${titleType}</h2>
                  <div style="margin-top: 10px; color: #555;">
                    <b>Invoice #:</b> ${currentPurchase.invoice_number}<br>
                    <b>Date:</b> ${new Date(currentPurchase.purchase_date).toLocaleString()}<br>
                    <b>Supplier:</b> ${getSupplierName(currentPurchase.supplier_id)}<br>
                    <b>Status:</b> ${currentPurchase.payment_status}
                  </div>
                </td>
              </tr>
            </table>

            <table class="item-table" style="margin-top: 20px;">
              <thead>
                <tr>
                  <th>{t("item", "ITEM")}</th>
                  <th style="text-align: center;">QTY</th>
                  <th style="text-align: right;">PRICE</th>
                  <th style="text-align: right;">TOTAL</th>
                </tr>
              </thead>
              <tbody>
                ${itemsHtml}
              </tbody>
            </table>

            <div class="totals-box">
              <table>
                <tr>
                  <td>Subtotal:</td>
                  <td>${parseFloat(currentPurchase.subtotal).toLocaleString()}</td>
                </tr>
                <tr>
                  <td>Discount:</td>
                  <td>${parseFloat(currentPurchase.discount).toLocaleString()}</td>
                </tr>
                <tr class="total-row">
                  <td>{t("total_due", "TOTAL DUE:")}</td>
                  <td>${parseFloat(currentPurchase.total_amount).toLocaleString()}</td>
                </tr>
              </table>
            </div>
            <div class="clear"></div>
            
            ${paymentsHtml}
            
            <div style="margin-top: 50px; text-align: center; color: #777; font-size: 12px; border-top: 1px solid #ddd; padding-top: 20px;">
              Thank you for doing business with DAKAFARM.
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

  const submitPayment = async (e) => {
    e.preventDefault();
    if (!paymentInput.account_id) {
      Swal.fire('Error', 'Please select a Payment Account.', 'error');
      return;
    }
    try {
      const payload = {
        purchase_id: currentPurchase.id,
        amount: parseFloat(paymentInput.amount),
        payment_method: paymentInput.payment_method,
        account_id: parseInt(paymentInput.account_id)
      };
      await api.post(`/api/v1/pos/purchases/${currentPurchase.id}/payments`, payload);
      Swal.fire('Success', 'Payment recorded successfully!', 'success');
      setShowPaymentModal(false);
      fetchPurchases();
      // Update current purchase if view modal is open
      if (showViewModal) {
          handleViewPurchase(currentPurchase.id);
      }
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to add payment', 'error');
    }
  };

  const handlePrintReceipt = () => {
    if (!currentPurchase) return;
    
    const printWindow = window.open('', '_blank', 'width=400,height=600');
    
    const itemsHtml = currentPurchase.items.map(item => `
      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
        <div style="flex: 2; text-align: left; padding-right: 5px;">
          <div>${getProductName(item.product_id)}</div>
          <div style="color: #555; font-size: 12px;">@ TSh ${parseFloat(item.unit_price).toLocaleString()}</div>
        </div>
        <div style="flex: 1; text-align: center;">${item.quantity}</div>
        <div style="flex: 1; text-align: right;">${parseFloat(item.total_amount).toLocaleString()}</div>
      </div>
    `).join('');

    const paymentMethod = currentPurchase.payments && currentPurchase.payments.length > 0 
      ? currentPurchase.payments[0].payment_method 
      : (currentPurchase.payment_status === 'PAID' ? 'Cash' : 'Credit');

    const receiptNumber = currentPurchase.payments && currentPurchase.payments.length > 0 
      ? currentPurchase.payments[currentPurchase.payments.length - 1].receipt_number 
      : currentPurchase.invoice_number;

    const cashierName = user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email.split('@')[0] : 'System';

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Receipt - ${receiptNumber}</title>
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
              *** START OF ${t("purchases_receipt", "PURCHASES RECEIPT")} ***
            </div>
            
            <div class="text-center">
              <h1>DAKAFARM</h1>
              <p>Dar es Salaam</p>
              <p>Tel: 0712 345 678</p>
              <p>info@amasfarm.com</p>
            </div>
            
            <div class="divider">----------------------------------------------------</div>
            
            <div>
              <p>Receipt:<br/>${receiptNumber}</p>
              <p>Date: ${new Date(currentPurchase.purchase_date).toLocaleString()}</p>
              <p>Cashier: ${cashierName}</p>
              <p>Supplier: ${getSupplierName(currentPurchase.supplier_id)}</p>
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
              <span>TSh ${parseFloat(currentPurchase.subtotal).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>DISCOUNT</span>
              <span>TSh ${parseFloat(currentPurchase.discount).toLocaleString()}</span>
            </div>
            <div class="flex-between" style="font-size: 16px; font-weight: 900; margin: 5px 0;">
              <span>TOTAL</span>
              <span>TSh ${parseFloat(currentPurchase.total_amount).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>CASH / PAID</span>
              <span>TSh ${parseFloat(currentPurchase.amount_paid).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>BALANCE</span>
              <span>TSh ${(parseFloat(currentPurchase.total_amount) - parseFloat(currentPurchase.amount_paid)).toLocaleString()}</span>
            </div>
            
            <br/>
            <div class="text-center">
              <p style="font-weight: bold;">RECEIPT VERIFICATION CODE</p>
              <p style="word-break: break-all;">${receiptNumber}</p>
            </div>
            
            <br/>
            
            <div class="text-center">
              <h2 style="margin: 0; font-size: 20px; font-weight: 900;">THANK YOU!</h2>
              <p>Glad to see you again!</p>
            </div>
            
            <div class="text-center header-text" style="margin-top: 15px;">
              *** END OF ${t("purchases_receipt", "PURCHASES RECEIPT")} ***
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

  const getSupplierName = (id) => {
    const c = suppliers.find(c => c.id === id);
    return c ? c.name : `ID: ${id}`;
  };
  
  const getProductName = (id) => {
      const p = products.find(p => p.id === id);
      return p ? p.name : `Product ID: ${id}`;
  };


  return (
    <>
      <style>{`
        .modal-90w {
          max-width: 90% !important;
        }
      `}</style>

      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('purchases', 'Purchases & Invoices')}</h4>
          <p className="mb-0">{t('profile_description')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => setShowNewPurchaseModal(true)}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('new_purchase')}
          </Button>
        </div>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">{t('invoice_no')}</th>
                <th className="border-bottom">Supplier</th>
                <th className="border-bottom">Date</th>
                <th className="border-bottom">Total Amount</th>
                <th className="border-bottom">{t('amount_paid')}</th>
                <th className="border-bottom">Status</th>
                <th className="border-bottom">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : purchases.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No purchases found.</td></tr>
              ) : (
                purchases.map(s => (
                  <tr key={s.id}>
                    <td><span className="fw-bold">{s.invoice_number}</span></td>
                    <td><span className="fw-normal">{getSupplierName(s.supplier_id)}</span></td>
                    <td><span className="fw-normal">{new Date(s.purchase_date).toLocaleDateString()}</span></td>
                    <td><span className="fw-bold text-success">{parseFloat(s.total_amount).toLocaleString()}</span></td>
                    <td><span className="fw-bold">{parseFloat(s.amount_paid).toLocaleString()}</span></td>
                    <td>{getStatusBadge(s.payment_status)}</td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleViewPurchase(s.id)}>
                        <FontAwesomeIcon icon={faEye} /> {t('view_purchase')}
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

      {/* NEW PURCHASE MODAL */}
      <Modal size="xl" dialogClassName="modal-90w" centered show={showNewPurchaseModal} onHide={() => setShowNewPurchaseModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{t("pop_checkout", "Point of Purchase Checkout")}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: '#f8f9fa' }}>
              <Row>
                {/* LEFT SIDE: PRODUCT CARDS (2 per row) */}
                <Col md={5}>
                  <Card className="border-0 shadow-sm mb-3">
                    <Card.Body>
                      <div className="d-flex mb-3 gap-2">
                        <InputGroup>
                          <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
                          <Form.Control 
                            type="text" 
                            placeholder="Search products..." 
                            value={productSearch}
                            onChange={(e) => setProductSearch(e.target.value)}
                          />
                        </InputGroup>
                        <Button variant="outline-primary" style={{ whiteSpace: 'nowrap' }} onClick={() => setShowProductModal(true)}>
                          <FontAwesomeIcon icon={faPlus} className="me-2" /> New Product
                        </Button>
                      </div>
                      
                      <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '5px' }}>
                        <Row>
                          {filteredProducts.map(p => (
                            <Col xs={6} md={6} lg={6} className="mb-3" key={p.id}>
                              <Card 
                                className="h-100 product-card shadow-sm"
                                style={{ cursor: 'pointer', transition: 'transform 0.1s'}}
                                onClick={() => handleAddToCart(p)}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                              >
                                <Card.Body className="p-3 text-center">
                                  <div className="fw-bold text-dark" style={{ fontSize: '15px' }}>{p.name}</div>
                                  <div className="text-muted small mb-2">{p.category_name || 'Item'}</div>
                                  <Badge bg={p.current_stock > 10 ? 'success' : (p.current_stock > 0 ? 'warning' : 'danger')} className="mb-2">
                                    Stock: {p.current_stock}
                                  </Badge>
                                  <div className="fw-bolder text-primary" style={{ fontSize: '16px' }}>
                                    TSh {parseFloat(p.selling_price).toLocaleString()}
                                  </div>
                                </Card.Body>
                              </Card>
                            </Col>
                          ))}
                          {filteredProducts.length === 0 && (
                            <div className="text-center text-muted w-100 py-4">No products found.</div>
                          )}
                        </Row>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>

                {/* RIGHT SIDE: CART & CHECKOUT (Expanded for comfortable inputs) */}
                <Col md={7}>
                  <Card className="border-0 shadow-sm h-100">
                    <Card.Body className="d-flex flex-column">
                      <Form.Group className="mb-3" style={{ position: 'relative', zIndex: 50 }}>
                        <Form.Label className="fw-bold">Supplier</Form.Label>
                        <Select
                          options={supplierOptions}
                          placeholder={t('search_suppliers')}
                          isClearable
                          menuPortalTarget={document.body}
                          styles={{ menuPortal: base => ({ ...base, zIndex: 9999 }) }}
                          onChange={(selected) => setNewPurchase({...newPurchase, supplier_id: selected ? selected.value : ''})}
                          value={supplierOptions.find(o => o.value === newPurchase.supplier_id) || null}
                        />
                      </Form.Group>

                      <div className="flex-grow-1" style={{ maxHeight: '35vh', overflowY: 'auto', border: '1px solid #eee', borderRadius: '5px' }}>
                        <Table hover size="sm" className="mb-0">
                          <thead className="bg-light sticky-top">
                            <tr>
                              <th>{t("item", "Item / Bidhaa")}</th>
                              <th className="text-center" style={{ minWidth: '95px' }}>Cost</th>
                              <th className="text-center" style={{ minWidth: '105px' }}>Price (New)</th>
                              <th className="text-center" style={{ minWidth: '85px' }}>Qty</th>
                              <th style={{ width: '35px' }}></th>
                            </tr>
                          </thead>
                          <tbody>
                            {cartItems.map((item, idx) => (
                              <tr key={idx}>
                                <td className="align-middle fw-bold">{item.name}</td>
                                <td className="align-middle text-center">
                                  <Form.Control type="number" size="sm" value={item.unit_price} onChange={(e) => {
                                      const newCart = [...cartItems];
                                      newCart[idx].unit_price = e.target.value;
                                      setCartItems(newCart);
                                  }} style={{ width: '95px', padding: '0.375rem 0.5rem', fontSize: '0.875rem', margin: '0 auto' }}/>
                                </td>
                                <td className="align-middle text-center">
                                  <Form.Control type="number" size="sm" value={item.new_selling_price || ''} onChange={(e) => {
                                      const newCart = [...cartItems];
                                      newCart[idx].new_selling_price = e.target.value;
                                      setCartItems(newCart);
                                  }} style={{ width: '105px', padding: '0.375rem 0.5rem', fontSize: '0.875rem', margin: '0 auto' }}/>
                                </td>
                                <td className="align-middle text-center">
                                    <Form.Control type="number" size="sm" min="0.01" step="any" value={item.quantity} onChange={(e) => {
                                        const val = e.target.value;
                                        const newCart = [...cartItems];
                                        newCart[idx].quantity = val;
                                        setCartItems(newCart);
                                    }} style={{ width: '85px', padding: '0.375rem 0.5rem', fontSize: '0.875rem', margin: '0 auto' }}/>
                                  </td>
                                
                                <td className="align-middle text-center">
                                  <Button variant="link" className="text-danger p-0" onClick={() => removeFromCart(idx)}>
                                    <FontAwesomeIcon icon={faTrash} />
                                  </Button>
                                </td>
                              </tr>
                            ))}
                            {cartItems.length === 0 && (
                              <tr><td colSpan="5" className="text-center text-muted py-4">Cart is empty</td></tr>
                            )}
                          </tbody>
                        </Table>
                      </div>

                      <div className="mt-3 pt-3 border-top">
                        <div className="d-flex justify-content-between mb-2">
                          <span className="text-muted">{t('subtotal')}:</span>
                          <span className="fw-bold">{cartSubtotal.toLocaleString()}</span>
                        </div>
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span className="text-muted">{t('discount')}:</span>
                          <Form.Control type="number" step="0.01" size="sm" style={{ width: '120px', textAlign: 'right' }} 
                            value={newPurchase.discount} onChange={(e) => setNewPurchase({...newPurchase, discount: e.target.value})} />
                        </div>
                        <div className="d-flex justify-content-between mb-3 p-2 bg-light rounded">
                          <span className="fw-bold h5 mb-0 text-dark">{t('total_due')}:</span>
                          <span className="fw-bold h5 mb-0 text-danger">{cartTotal.toLocaleString()} TSh</span>
                        </div>
                        
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span className="text-muted">{t('amount_paid')}:</span>
                          <Form.Control type="number" step="0.01" size="sm" style={{ width: '120px', textAlign: 'right' }} 
                            value={newPurchase.amount_paid} onChange={(e) => setNewPurchase({...newPurchase, amount_paid: e.target.value})} />
                        </div>
                        <Form.Group className="mb-3">
                          <Form.Label className="text-muted small mb-1">{t('payment_method')}</Form.Label>
                          <Form.Select size="sm" value={newPurchase.payment_method} onChange={(e) => setNewPurchase({...newPurchase, payment_method: e.target.value})}>
                            <option value="Cash">{t('cash')}</option>
                            <option value="Mobile Money">{t('mobile_money')}</option>
                            <option value="Bank Transfer">{t('bank_transfer')}</option>
                          </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label className="text-muted small mb-1">Payment Account {parseFloat(newPurchase.amount_paid) > 0 && '*'}</Form.Label>
                          <Form.Select size="sm" value={newPurchase.account_id} onChange={(e) => setNewPurchase({...newPurchase, account_id: e.target.value})}>
                            <option value="">-- Select Account --</option>
                            {accounts.map(acc => (
                              <option key={acc.id} value={acc.id}>{acc.name} ({acc.account_type})</option>
                            ))}
                          </Form.Select>
                        </Form.Group>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewPurchaseModal(false)}>Cancel</Button>
          <Button variant="success" onClick={submitNewPurchase}>Confirm Purchase</Button>
        </Modal.Footer>
      </Modal>

      {/* VIEW {t("invoice", "INVOICE")}/RECEIPT MODAL */}
      <Modal size="lg" centered show={showViewModal} onHide={() => setShowViewModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{t("invoice_details", "Invoice Details")}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-light p-4" style={{ fontFamily: 'monospace' }}>
          {currentPurchase && (
            <div className="bg-white p-4 border shadow-sm">
              <div className="text-center mb-4">
                <h4 className="mb-0">DAKAFARM</h4>
                {currentPurchase.payment_status === 'PAID' ? <h5>{t("purchases_receipt", "PURCHASES RECEIPT")}</h5> : <h5>{t("invoice", "INVOICE")}</h5>}
                <small>Receipt/Invoice #: {currentPurchase.invoice_number}</small>
              </div>
              <Row className="mb-4">
                <Col>
                  <strong>Supplier:</strong> {getSupplierName(currentPurchase.supplier_id)}<br/>
                  <strong>Date:</strong> {new Date(currentPurchase.purchase_date).toLocaleString()}<br/>
                  <strong>{t('payment_status')}:</strong> {currentPurchase.payment_status}
                </Col>
              </Row>
              <Table bordered size="sm">
                <thead>
                  <tr>
                    <th>{t("item", "Item")}</th>
                    <th>{t("qty", "Qty")}</th>
                    <th>{t("price", "Price")}</th>
                    <th>{t("total", "Total")}</th>
                  </tr>
                </thead>
                <tbody>
                  {currentPurchase.items?.map((item, idx) => (
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
                  <p className="mb-1">{t('subtotal')}: <strong>{parseFloat(currentPurchase.subtotal).toLocaleString()}</strong></p>
                  <p className="mb-1">{t('discount')}: <strong>{parseFloat(currentPurchase.discount).toLocaleString()}</strong></p>
                  <h5 className="mt-2 text-danger">{t("total_due", "TOTAL DUE:")} {parseFloat(currentPurchase.total_amount).toLocaleString()}</h5>
                </Col>
              </Row>

              {/* Payments Section */}
              {currentPurchase.payments && currentPurchase.payments.length > 0 && (
                <div className="mt-4 border-top pt-3">
                  <h6>{t("payment_history", "Payment History")}</h6>
                  <Table size="sm" className="text-muted">
                    <thead>
                      <tr>
                        <th>{t("receipt_no", "Receipt No")}</th>
                        <th>Date</th>
                        <th>{t("method", "Method")}</th>
                        <th>{t("amount", "Amount")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentPurchase.payments.map((p, idx) => (
                        <tr key={idx}>
                          <td>{p.receipt_number}</td>
                          <td>{new Date(p.payment_date).toLocaleString()}</td>
                          <td>{p.payment_method}</td>
                          <td className="fw-bold">{parseFloat(p.amount).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                  <h6 className="text-end text-success mt-2">{t("total_paid", "Total Paid:")} {parseFloat(currentPurchase.amount_paid).toLocaleString()}</h6>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          {currentPurchase && currentPurchase.payment_status !== 'PAID' && (
            <Button variant="success" onClick={() => handleAddPaymentClick(currentPurchase)}>
              <FontAwesomeIcon icon={faMoneyBillWave} className="me-2" /> {t('add_payment')}
            </Button>
          )}
          <Button variant="secondary" onClick={() => setShowViewModal(false)}>Close</Button>
          <Button variant="info" onClick={handlePrintReceipt}>{t('print_receipt_small')}</Button>
          <Button variant="primary" onClick={handlePrintInvoice}>{t('print_invoice_a4')}</Button>
        </Modal.Footer>
      </Modal>

      {/* ADD PAYMENT MODAL */}
      <Modal centered show={showPaymentModal} onHide={() => setShowPaymentModal(false)}>
        <Form onSubmit={submitPayment}>
          <Modal.Header closeButton>
            <Modal.Title>{t('add_payment')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {currentPurchase && (
              <div className="mb-3 text-muted">
                Invoice: <strong>{currentPurchase.invoice_number}</strong><br/>
                {t('total_due')}: <strong>{parseFloat(currentPurchase.total_amount).toLocaleString()}</strong><br/>
                Remaining Balance: <strong className="text-danger">
                  {(parseFloat(currentPurchase.total_amount) - parseFloat(currentPurchase.amount_paid)).toLocaleString()}
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
            <Form.Group className="mb-3">
              <Form.Label>Payment Account *</Form.Label>
              <Form.Select value={paymentInput.account_id} onChange={(e) => setPaymentInput({...paymentInput, account_id: e.target.value})} required>
                <option value="">-- Select Account --</option>
                {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>{acc.name} ({acc.account_type})</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>Cancel</Button>
            <Button variant="primary" type="submit">Save Payment</Button>
          </Modal.Footer>
        </Form>
      </Modal>
      <Modal show={showProductModal} onHide={() => setShowProductModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{t("create_new_product", "Create New Product")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Product Name *</Form.Label>
              <Form.Control type="text" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Category *</Form.Label>
              <Form.Select value={newProduct.category_id} onChange={e => setNewProduct({...newProduct, category_id: e.target.value})} required>
                <option value="">-- Select Category --</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Unit of Measure *</Form.Label>
              <Form.Control type="text" placeholder="e.g. kg, trays" value={newProduct.unit_of_measure} onChange={e => setNewProduct({...newProduct, unit_of_measure: e.target.value})} required />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowProductModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleCreateProduct}>Create Product</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};




