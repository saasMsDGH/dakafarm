import re

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Import Select
if "import Select from 'react-select';" not in code:
    code = code.replace("import React, { useState, useEffect } from \"react\";", "import React, { useState, useEffect } from \"react\";\nimport Select from 'react-select';")

# 2. Add product search state
if "const [productSearch, setProductSearch] = useState('');" not in code:
    code = code.replace("const [cartItems, setCartItems] = useState([]);", "const [cartItems, setCartItems] = useState([]);\n  const [productSearch, setProductSearch] = useState('');")

# 3. Create handleAddToCart function instead of the dropdown change
new_funcs = """  const handleAddToCart = (product) => {
    if (product.current_stock <= 0) {
      Swal.fire('Error', 'Out of stock!', 'error');
      return;
    }
    const existing = cartItems.find(item => item.product_id === product.id);
    if (existing) {
      if (existing.quantity + 1 > product.current_stock) {
        Swal.fire('Warning', 'Cannot exceed current stock limit.', 'warning');
        return;
      }
      setCartItems(cartItems.map(item => 
        item.product_id === product.id ? {...item, quantity: item.quantity + 1} : item
      ));
    } else {
      setCartItems([...cartItems, {
        product_id: product.id,
        name: product.name,
        quantity: 1,
        unit_price: parseFloat(product.selling_price)
      }]);
    }
  };

  const filteredProducts = products.filter(p => p.name.toLowerCase().includes(productSearch.toLowerCase()));

  const customerOptions = customers.map(c => ({
    value: c.id,
    label: `${c.name} (${c.business_type || 'Retail'}) - Limit: ${parseFloat(c.credit_limit).toLocaleString()}`
  }));
"""
if "const filteredProducts =" not in code:
    code = code.replace("const handleProductSelect = (e) => {", new_funcs + "\n  const handleProductSelect = (e) => {")

# 4. Replace the Customer dropdown
old_customer_dropdown = """<Form.Select 
                      value={newSale.customer_id} 
                      onChange={(e) => setNewSale({...newSale, customer_id: e.target.value})}
                    >
                      <option value="">{t('select_customer')}</option>
                      {customers.map(c => (
                        <option key={c.id} value={c.id}>{c.name} ({c.business_type || 'Retail'}) - Limit: {parseFloat(c.credit_limit).toLocaleString()}</option>
                      ))}
                    </Form.Select>"""

new_customer_dropdown = """<Select
                      options={customerOptions}
                      placeholder={t('search_customers')}
                      isClearable
                      onChange={(selected) => setNewSale({...newSale, customer_id: selected ? selected.value : ''})}
                      value={customerOptions.find(o => o.value === newSale.customer_id) || null}
                    />"""

code = code.replace(old_customer_dropdown, new_customer_dropdown)

# 5. Replace Add Items Section
# We need to completely rewrite the New Sale layout to have a side-by-side or top-bottom layout for cards and cart.
# Because it's a size="xl" Modal, side-by-side works well: left side Product Grid, right side Cart & Summary.

old_modal_body_regex = re.compile(r'<Modal\.Body>.*?</Modal\.Body>', re.DOTALL)

new_modal_body = """<Modal.Body style={{ backgroundColor: '#f8f9fa' }}>
              <Row>
                {/* LEFT SIDE: PRODUCT CARDS */}
                <Col md={7}>
                  <Card className="border-0 shadow-sm mb-3">
                    <Card.Body>
                      <InputGroup className="mb-3">
                        <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
                        <Form.Control 
                          placeholder="Search products..." 
                          value={productSearch}
                          onChange={(e) => setProductSearch(e.target.value)}
                        />
                      </InputGroup>
                      
                      <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '5px' }}>
                        <Row>
                          {filteredProducts.map(p => (
                            <Col xs={6} lg={4} className="mb-3" key={p.id}>
                              <Card 
                                className={`h-100 product-card shadow-sm ${p.current_stock <= 0 ? 'opacity-50' : ''}`}
                                style={{ cursor: p.current_stock > 0 ? 'pointer' : 'not-allowed', transition: 'transform 0.1s' }}
                                onClick={() => handleAddToCart(p)}
                                onMouseOver={(e) => { if (p.current_stock > 0) e.currentTarget.style.transform = 'scale(1.02)'; }}
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

                {/* RIGHT SIDE: CART & CHECKOUT */}
                <Col md={5}>
                  <Card className="border-0 shadow-sm h-100">
                    <Card.Body className="d-flex flex-column">
                      <Form.Group className="mb-3">
                        <Form.Label className="fw-bold">Customer</Form.Label>
                        <Select
                          options={customerOptions}
                          placeholder={t('search_customers')}
                          isClearable
                          onChange={(selected) => setNewSale({...newSale, customer_id: selected ? selected.value : ''})}
                          value={customerOptions.find(o => o.value === newSale.customer_id) || null}
                        />
                      </Form.Group>

                      <div className="flex-grow-1" style={{ maxHeight: '35vh', overflowY: 'auto', border: '1px solid #eee', borderRadius: '5px' }}>
                        <Table hover size="sm" className="mb-0">
                          <thead className="bg-light sticky-top">
                            <tr>
                              <th>Item</th>
                              <th className="text-center">Qty</th>
                              <th className="text-right">Total</th>
                              <th></th>
                            </tr>
                          </thead>
                          <tbody>
                            {cartItems.map((item, idx) => (
                              <tr key={idx}>
                                <td className="align-middle fw-bold">{item.name}</td>
                                <td className="align-middle text-center">
                                  <div className="d-flex align-items-center justify-content-center">
                                    <Button variant="light" size="sm" className="px-2 py-0" 
                                      onClick={() => {
                                        const newQty = Math.max(1, item.quantity - 1);
                                        const newCart = [...cartItems];
                                        newCart[idx].quantity = newQty;
                                        setCartItems(newCart);
                                      }}>-</Button>
                                    <span className="mx-2">{item.quantity}</span>
                                    <Button variant="light" size="sm" className="px-2 py-0"
                                      onClick={() => {
                                        const prod = products.find(p => p.id === item.product_id);
                                        if (item.quantity + 1 > prod.current_stock) {
                                          Swal.fire('Warning', 'Stock limit reached', 'warning');
                                          return;
                                        }
                                        const newCart = [...cartItems];
                                        newCart[idx].quantity = item.quantity + 1;
                                        setCartItems(newCart);
                                      }}>+</Button>
                                  </div>
                                </td>
                                <td className="align-middle text-right">{(item.quantity * item.unit_price).toLocaleString()}</td>
                                <td className="align-middle text-center">
                                  <Button variant="link" className="text-danger p-0" onClick={() => removeCartItem(idx)}>
                                    <FontAwesomeIcon icon={faTrash} />
                                  </Button>
                                </td>
                              </tr>
                            ))}
                            {cartItems.length === 0 && (
                              <tr><td colSpan="4" className="text-center text-muted py-4">Cart is empty</td></tr>
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
                            value={newSale.discount} onChange={(e) => setNewSale({...newSale, discount: e.target.value})} />
                        </div>
                        <div className="d-flex justify-content-between mb-3 p-2 bg-light rounded">
                          <span className="fw-bold h5 mb-0 text-dark">{t('total_due')}:</span>
                          <span className="fw-bold h5 mb-0 text-danger">{cartTotal.toLocaleString()} TSh</span>
                        </div>
                        
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span className="text-muted">{t('amount_paid')}:</span>
                          <Form.Control type="number" step="0.01" size="sm" style={{ width: '120px', textAlign: 'right' }} 
                            value={newSale.amount_paid} onChange={(e) => setNewSale({...newSale, amount_paid: e.target.value})} />
                        </div>
                        <Form.Group className="mb-3">
                          <Form.Label className="text-muted small mb-1">{t('payment_method')}</Form.Label>
                          <Form.Select size="sm" value={newSale.payment_method} onChange={(e) => setNewSale({...newSale, payment_method: e.target.value})}>
                            <option value="Cash">{t('cash')}</option>
                            <option value="Mobile Money">{t('mobile_money')}</option>
                            <option value="Bank Transfer">{t('bank_transfer')}</option>
                          </Form.Select>
                        </Form.Group>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Modal.Body>"""

code = old_modal_body_regex.sub(new_modal_body, code, count=1) # only replace the first Modal.Body which is New Sale

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
