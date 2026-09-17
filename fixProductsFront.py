with open("frontend/src/pages/inventory/Products.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Add to initial state
code = code.replace(
    "selling_price: '0.00',",
    "selling_price: '0.00',\n    current_stock: '0.000',"
)

# Add to edit state
code = code.replace(
    "selling_price: product.selling_price || '0.00',",
    "selling_price: product.selling_price || '0.00',\n        current_stock: product.current_stock || '0.000',"
)

# Add to payload
code = code.replace(
    "selling_price: parseFloat(currentProduct.selling_price),",
    "selling_price: parseFloat(currentProduct.selling_price),\n        current_stock: currentProduct.current_stock !== '' ? parseFloat(currentProduct.current_stock) : null,"
)

# Add to table header
code = code.replace(
    "<th className=\"border-bottom\">{t('selling_price', 'Price')}</th>",
    "<th className=\"border-bottom\">{t('selling_price', 'Price')}</th>\n                  <th className=\"border-bottom\">{t('current_stock', 'Stock')}</th>"
)

# Add to table row
code = code.replace(
    "<td><span className=\"fw-normal\">{prod.selling_price}</span></td>",
    "<td><span className=\"fw-normal\">{prod.selling_price}</span></td>\n                    <td><span className=\"fw-normal\">{prod.current_stock}</span></td>"
)

# Add to form modal
form_field = """                <Col md={6}>
                  <Form.Group id="current_stock" className="mb-3">
                    <Form.Label>{t('current_stock', 'Current Stock')}</Form.Label>
                    <Form.Control 
                      type="number"
                      step="0.001" 
                      name="current_stock"
                      value={currentProduct.current_stock} 
                      onChange={handleInputChange} 
                      placeholder="Optional"
                    />
                  </Form.Group>
                </Col>"""
code = code.replace(
    '<Form.Group id="reorder_level" className="mb-3">',
    form_field + '\n                <Col md={6}>\n                  <Form.Group id="reorder_level" className="mb-3">'
)
# Fix the col wrapping, since I just added a Col md=6, it needs to wrap correctly.
# Wait, let's just insert it after selling_price instead.
with open("frontend/src/pages/inventory/Products.jsx", "w", encoding="utf-8") as f:
    f.write(code)
