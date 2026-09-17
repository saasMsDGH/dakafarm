import re

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# basic replaces
code = code.replace("Sale", "Purchase")
code = code.replace("sale", "purchase")
code = code.replace("SALE", "PURCHASE")
code = code.replace("Customer", "Supplier")
code = code.replace("customer", "supplier")
code = code.replace("CUSTOMERS", "SUPPLIERS")

# The URL should be changed from /api/v1/pos/purchases/ to something else? Yes, Purchases.
# Actually I replaced "sale" -> "purchase", so `/api/v1/pos/sales/` became `/api/v1/pos/purchases/`.

# 1. Update the payload in addPurchase (was addSale)
# Sales payload used: items: cartItems.map(item => ({ product_id, quantity, unit_price }))
# Purchase payload needs: unit_cost and new_selling_price instead of unit_price
payload_search = """items: cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price
      }))"""
payload_replace = """items: cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_cost: item.unit_price,
        new_selling_price: item.new_selling_price
      }))"""
code = code.replace(payload_search, payload_replace)

# 2. When adding an item to the cart (handleAddToCart)
# Sales adds: { product_id: p.id, name: p.name, quantity: 1, unit_price: parseFloat(p.selling_price) }
add_to_cart_search = """setCartItems([...cartItems, { 
      product_id: p.id, 
      name: p.name, 
      quantity: 1, 
      unit_price: parseFloat(p.selling_price) 
    }]);"""
add_to_cart_replace = """setCartItems([...cartItems, { 
      product_id: p.id, 
      name: p.name, 
      quantity: 1, 
      unit_price: parseFloat(p.unit_price || 0),
      new_selling_price: parseFloat(p.selling_price || 0)
    }]);"""
code = code.replace(add_to_cart_search, add_to_cart_replace)

# 3. Cart Table Headers
headers_search = """<tr>
                                <th>Item</th>
                                <th className="text-center">Qty</th>
                                <th className="text-right">Total</th>
                                <th></th>
                              </tr>"""
headers_replace = """<tr>
                                <th>Item</th>
                                <th className="text-center">Cost</th>
                                <th className="text-center">Price (New)</th>
                                <th className="text-center">Qty</th>
                                <th></th>
                              </tr>"""
code = code.replace(headers_search, headers_replace)

# 4. Cart Table Rows
row_search = """<td className="align-middle fw-bold">{item.name}</td>
                                  <td className="align-middle text-center">
                                    <div className="d-flex align-items-center justify-content-center">"""
row_replace = """<td className="align-middle fw-bold">{item.name}</td>
                                  <td className="align-middle text-center">
                                    <Form.Control type="number" size="sm" value={item.unit_price} onChange={(e) => {
                                        const newCart = [...cartItems];
                                        newCart[idx].unit_price = parseFloat(e.target.value) || 0;
                                        setCartItems(newCart);
                                    }} style={{width: '60px'}}/>
                                  </td>
                                  <td className="align-middle text-center">
                                    <Form.Control type="number" size="sm" value={item.new_selling_price || ''} onChange={(e) => {
                                        const newCart = [...cartItems];
                                        newCart[idx].new_selling_price = parseFloat(e.target.value) || 0;
                                        setCartItems(newCart);
                                    }} style={{width: '60px'}}/>
                                  </td>
                                  <td className="align-middle text-center">
                                    <div className="d-flex align-items-center justify-content-center">"""
code = code.replace(row_search, row_replace)

# 5. Remove the stock limit check for purchases
stock_check_search = """if (item.quantity + 1 > prod.current_stock) {
                                            Swal.fire('Warning', 'Stock limit reached', 'warning');
                                            return;
                                          }"""
stock_check_replace = ""
code = code.replace(stock_check_search, stock_check_replace)

# 6. Remove the "Total" column entirely, or adjust it
total_col_search = """<td className="align-middle text-right">{(item.quantity * item.unit_price).toLocaleString()}</td>"""
total_col_replace = ""
code = code.replace(total_col_search, total_col_replace)


with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
