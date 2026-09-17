with open("frontend/src/pages/inventory/Products.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# State 1
code = code.replace(
    "selling_price: '0.00',",
    "selling_price: '0.00',\n    current_stock: '0.000',"
)
# State 2
code = code.replace(
    "selling_price: product.selling_price || '0.00',",
    "selling_price: product.selling_price || '0.00',\n          current_stock: product.current_stock || '0.000',"
)
# Payload
code = code.replace(
    "selling_price: parseFloat(currentProduct.selling_price),",
    "selling_price: parseFloat(currentProduct.selling_price),\n          current_stock: currentProduct.current_stock !== '' ? parseFloat(currentProduct.current_stock) : null,"
)
# Table header
code = code.replace(
    "<th className=\"border-bottom\">{t('selling_price', 'Price')}</th>",
    "<th className=\"border-bottom\">{t('selling_price', 'Price')}</th>\n                  <th className=\"border-bottom\">{t('current_stock', 'Stock')}</th>"
)
# Table row
code = code.replace(
    "<td><span className=\"fw-normal\">{prod.selling_price}</span></td>",
    "<td><span className=\"fw-normal\">{prod.selling_price}</span></td>\n                      <td><span className=\"fw-normal\">{prod.current_stock}</span></td>"
)

# Modal Form
form_field = """              <Col md={6}>
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
              
# Insert before the reorder level Col
reorder_col = """              <Col md={6}>
                <Form.Group id="reorder_level" className="mb-3">"""
                
code = code.replace(reorder_col, form_field + "\n" + reorder_col)

with open("frontend/src/pages/inventory/Products.jsx", "w", encoding="utf-8") as f:
    f.write(code)
