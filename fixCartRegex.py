with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# 1. setCartItems inside handleAddToCart
code = re.sub(
    r'setCartItems\(\[\.\.\.cartItems,\s*\{\s*product_id:\s*product\.id,\s*name:\s*product\.name,\s*quantity:\s*1,\s*unit_price:\s*parseFloat\(product\.selling_price\)\s*\}\]\);',
    """setCartItems([...cartItems, {
        product_id: product.id,
        name: product.name,
        quantity: 1,
        unit_price: parseFloat(product.unit_price || 0),
        new_selling_price: parseFloat(product.selling_price || 0)
      }]);""",
    code
)

# 2. Table Headers
headers_search = r'<tr>\s*<th>Item</th>\s*<th className="text-center">Qty</th>\s*<th className="text-right">Total</th>\s*<th></th>\s*</tr>'
headers_replace = """<tr>
                              <th>Item</th>
                              <th className="text-center">Cost</th>
                              <th className="text-center">Price (New)</th>
                              <th className="text-center">Qty</th>
                              <th></th>
                            </tr>"""
code = re.sub(headers_search, headers_replace, code)

# 3. Table Rows
row_search = r'<td className="align-middle fw-bold">\{item\.name\}</td>\s*<td className="align-middle text-center">\s*<div className="d-flex align-items-center justify-content-center">'
row_replace = """<td className="align-middle fw-bold">{item.name}</td>
                                <td className="align-middle text-center">
                                  <Form.Control type="number" size="sm" value={item.unit_price} onChange={(e) => {
                                      const newCart = [...cartItems];
                                      newCart[idx].unit_price = parseFloat(e.target.value) || 0;
                                      setCartItems(newCart);
                                  }} style={{width: '60px', padding: '0.25rem', fontSize: '0.8rem'}}/>
                                </td>
                                <td className="align-middle text-center">
                                  <Form.Control type="number" size="sm" value={item.new_selling_price || ''} onChange={(e) => {
                                      const newCart = [...cartItems];
                                      newCart[idx].new_selling_price = parseFloat(e.target.value) || 0;
                                      setCartItems(newCart);
                                  }} style={{width: '60px', padding: '0.25rem', fontSize: '0.8rem'}}/>
                                </td>
                                <td className="align-middle text-center">
                                  <div className="d-flex align-items-center justify-content-center">"""
code = re.sub(row_search, row_replace, code)

# 4. Remove Stock Limits checks
code = re.sub(r'if \(!prod \|\| item\.quantity \+ 1 > prod\.current_stock\) \{[\s\S]*?return;\s*\}', '', code)
code = re.sub(r'if \(product\.current_stock <= 0\) \{[\s\S]*?return;\s*\}', '', code)
code = re.sub(r'if \(existing\.quantity \+ 1 > product\.current_stock\) \{[\s\S]*?return;\s*\}', '', code)

# 5. Remove Total col
code = re.sub(r'<td className="align-middle text-right">\{\(item\.quantity \* item\.unit_price\)\.toLocaleString\(\)\}</td>', '', code)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
