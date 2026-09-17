with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write("""
import React, { useState, useEffect } from "react";
import Select from 'react-select';
import CreatableSelect from 'react-select/creatable';
import { useAuth } from '../../context/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faTrash, faSave } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Form, Modal } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const [suppliers, setSuppliers] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  
  // Purchase Meta
  const [supplierId, setSupplierId] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("CASH");
  const [amountPaid, setAmountPaid] = useState("");
  const [discount, setDiscount] = useState("0");
  const [notes, setNotes] = useState("");

  // Cart
  const [cart, setCart] = useState([]);
  
  // Current Item Entry
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState('');
  const [unitCost, setUnitCost] = useState('');
  const [sellingPrice, setSellingPrice] = useState('');

  // Quick Product Modal
  const [showProductModal, setShowProductModal] = useState(false);
  const [newProductName, setNewProductName] = useState('');
  const [newProductCategory, setNewProductCategory] = useState('');
  const [newProductUnit, setNewProductUnit] = useState('');

  const fetchData = async () => {
    try {
      const [suppRes, prodRes, catRes] = await Promise.all([
        api.get('/api/v1/pos/suppliers/', { params: { limit: 100 } }),
        api.get('/api/v1/inventory/products/', { params: { limit: 1000 } }),
        api.get('/api/v1/inventory/product-categories/', { params: { limit: 100 } })
      ]);
      setSuppliers(suppRes.data.items || []);
      setProducts(prodRes.data.items || []);
      setCategories(catRes.data.items || []);
    } catch (error) {
      console.error("Failed to load initial data", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const productOptions = products.map(p => ({
    value: p.id,
    label: p.name,
    product: p
  }));

  const handleProductChange = (selected) => {
    setSelectedProduct(selected);
    if (selected && selected.product) {
      setUnitCost(selected.product.unit_price || 0);
      setSellingPrice(selected.product.selling_price || 0);
    } else {
      setUnitCost('');
      setSellingPrice('');
    }
  };

  const handleCreateProduct = (inputValue) => {
    setNewProductName(inputValue);
    setNewProductCategory('');
    setNewProductUnit('');
    setShowProductModal(true);
  };

  const submitNewProduct = async () => {
    if (!newProductCategory || !newProductUnit) {
      Swal.fire('Error', 'Please fill all required fields', 'error');
      return;
    }
    try {
      const payload = {
        name: newProductName,
        category_id: parseInt(newProductCategory),
        unit_of_measure: newProductUnit,
        unit_price: parseFloat(unitCost) || 0,
        selling_price: parseFloat(sellingPrice) || 0,
        current_stock: 0,
        is_active: true
      };
      const res = await api.post('/api/v1/inventory/products/', payload);
      const newProd = res.data;
      setProducts([...products, newProd]);
      
      const newOption = { value: newProd.id, label: newProd.name, product: newProd };
      setSelectedProduct(newOption);
      setShowProductModal(false);
      Swal.fire('Success', 'Product created successfully', 'success');
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create product', 'error');
    }
  };

  const handleAddToList = () => {
    if (!selectedProduct) return Swal.fire('Error', 'Select a product', 'error');
    if (!quantity || quantity <= 0) return Swal.fire('Error', 'Enter a valid quantity', 'error');
    if (unitCost === '' || unitCost < 0) return Swal.fire('Error', 'Enter a valid unit cost', 'error');

    setCart([...cart, {
      product_id: selectedProduct.value,
      name: selectedProduct.label,
      quantity: parseFloat(quantity),
      unit_cost: parseFloat(unitCost),
      new_selling_price: sellingPrice !== '' ? parseFloat(sellingPrice) : null
    }]);

    setSelectedProduct(null);
    setQuantity('');
    setUnitCost('');
    setSellingPrice('');
  };

  const removeCartItem = (index) => {
    const newCart = [...cart];
    newCart.splice(index, 1);
    setCart(newCart);
  };

  const submitPurchase = async () => {
    if (cart.length === 0) return Swal.fire('Error', 'Purchase list is empty', 'error');
    if (!supplierId) return Swal.fire('Error', 'Please select a supplier', 'error');

    const totalCost = cart.reduce((sum, item) => sum + (item.quantity * item.unit_cost), 0);
    const finalAmount = totalCost - parseFloat(discount || 0);

    const payload = {
      supplier_id: parseInt(supplierId),
      total_amount: finalAmount,
      amount_paid: parseFloat(amountPaid || 0),
      discount: parseFloat(discount || 0),
      payment_method: paymentMethod,
      notes: notes,
      items: cart
    };

    try {
      await api.post('/api/v1/pos/purchases/', payload);
      Swal.fire('Success', 'Purchase recorded successfully!', 'success');
      setCart([]);
      setSupplierId("");
      setAmountPaid("");
      setDiscount("0");
      setNotes("");
      fetchData(); // refresh products to update prices/stock locally
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to submit purchase', 'error');
    }
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.quantity * item.unit_cost), 0);

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('purchases', 'Purchases / Inventory Receiving')}</h4>
          <p className="mb-0">Record incoming goods from suppliers</p>
        </div>
      </div>

      <Row>
        <Col xs={12} xl={8}>
          <Card border="light" className="shadow-sm mb-4">
            <Card.Header>
              <h5 className="mb-0">Add Item to Purchase</h5>
            </Card.Header>
            <Card.Body>
              <Row className="align-items-end">
                <Col md={4} className="mb-3">
                  <Form.Label>Product</Form.Label>
                  <CreatableSelect
                    isClearable
                    onChange={handleProductChange}
                    onCreateOption={handleCreateProduct}
                    options={productOptions}
                    value={selectedProduct}
                    placeholder="Type to search or create..."
                  />
                </Col>
                <Col md={2} className="mb-3">
                  <Form.Label>Qty</Form.Label>
                  <Form.Control type="number" step="0.001" value={quantity} onChange={e => setQuantity(e.target.value)} />
                </Col>
                <Col md={2} className="mb-3">
                  <Form.Label>Unit Cost</Form.Label>
                  <Form.Control type="number" step="0.01" value={unitCost} onChange={e => setUnitCost(e.target.value)} />
                </Col>
                <Col md={2} className="mb-3">
                  <Form.Label>Selling Price</Form.Label>
                  <Form.Control type="number" step="0.01" value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} />
                </Col>
                <Col md={2} className="mb-3">
                  <Button variant="primary" className="w-100" onClick={handleAddToList}>
                    <FontAwesomeIcon icon={faPlus} className="me-2" /> Add
                  </Button>
                </Col>
              </Row>

              <div className="table-responsive mt-4">
                <Table className="table-centered table-nowrap rounded mb-0" hover>
                  <thead className="thead-light">
                    <tr>
                      <th className="border-0">Product</th>
                      <th className="border-0 text-center">Qty</th>
                      <th className="border-0 text-right">Unit Cost</th>
                      <th className="border-0 text-right">Selling Price</th>
                      <th className="border-0 text-right">Total</th>
                      <th className="border-0 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map((item, idx) => (
                      <tr key={idx}>
                        <td className="fw-bold">{item.name}</td>
                        <td className="text-center">{item.quantity}</td>
                        <td className="text-right">{item.unit_cost.toLocaleString()}</td>
                        <td className="text-right">{item.new_selling_price ? item.new_selling_price.toLocaleString() : '-'}</td>
                        <td className="text-right fw-bold">{(item.quantity * item.unit_cost).toLocaleString()}</td>
                        <td className="text-center">
                          <Button variant="link" className="text-danger p-0" onClick={() => removeCartItem(idx)}>
                            <FontAwesomeIcon icon={faTrash} />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {cart.length === 0 && (
                      <tr><td colSpan="6" className="text-center py-3">No items added yet.</td></tr>
                    )}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xs={12} xl={4}>
          <Card border="light" className="shadow-sm mb-4">
            <Card.Header>
              <h5 className="mb-0">Purchase Details</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Supplier</Form.Label>
                  <Form.Select value={supplierId} onChange={e => setSupplierId(e.target.value)}>
                    <option value="">-- Select Supplier --</option>
                    {suppliers.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <div className="d-flex justify-content-between mb-2">
                  <span className="fw-bold">Subtotal:</span>
                  <span>{cartTotal.toLocaleString()}</span>
                </div>
                
                <Form.Group className="mb-2 d-flex justify-content-between align-items-center">
                  <Form.Label className="mb-0">Discount:</Form.Label>
                  <Form.Control type="number" size="sm" style={{width: '100px', textAlign: 'right'}} value={discount} onChange={e => setDiscount(e.target.value)} />
                </Form.Group>

                <div className="d-flex justify-content-between mb-3 border-top pt-2">
                  <span className="fw-bold h5">Total:</span>
                  <span className="fw-bold h5 text-danger">{(cartTotal - parseFloat(discount || 0)).toLocaleString()}</span>
                </div>

                <Form.Group className="mb-3">
                  <Form.Label>Amount Paid</Form.Label>
                  <Form.Control type="number" step="0.01" value={amountPaid} onChange={e => setAmountPaid(e.target.value)} />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Payment Method</Form.Label>
                  <Form.Select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value)}>
                    <option value="CASH">Cash</option>
                    <option value="BANK">Bank</option>
                    <option value="MOBILE">Mobile Money</option>
                    <option value="CREDIT">Credit (Unpaid)</option>
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-4">
                  <Form.Label>Notes</Form.Label>
                  <Form.Control as="textarea" rows={2} value={notes} onChange={e => setNotes(e.target.value)} placeholder="Receipt number, remarks..." />
                </Form.Group>

                <Button variant="success" className="w-100" onClick={submitPurchase} disabled={cart.length === 0}>
                  <FontAwesomeIcon icon={faSave} className="me-2" /> Record Purchase
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Modal show={showProductModal} onHide={() => setShowProductModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Quick Create Product</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Product Name</Form.Label>
              <Form.Control type="text" value={newProductName} onChange={e => setNewProductName(e.target.value)} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Category *</Form.Label>
              <Form.Select value={newProductCategory} onChange={e => setNewProductCategory(e.target.value)}>
                <option value="">-- Select Category --</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Unit of Measure *</Form.Label>
              <Form.Control type="text" value={newProductUnit} onChange={e => setNewProductUnit(e.target.value)} placeholder="e.g. kg, pieces, trays" />
            </Form.Group>
            {/* We don't ask for price here, because they will enter it in the purchase form directly! */}
            <div className="text-muted small">
              Unit Cost and Selling Price will be updated automatically when you complete the purchase.
            </div>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowProductModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={submitNewProduct}>Save & Select</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};
""")
