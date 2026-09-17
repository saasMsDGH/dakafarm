with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Simple renames
code = code.replace("Sale", "Purchase")
code = code.replace("sale", "purchase")
code = code.replace("SALE", "PURCHASE")
code = code.replace("Customer", "Supplier")
code = code.replace("customer", "supplier")
code = code.replace("CUSTOMERS", "SUPPLIERS")

# The Purchase cart needs a new_selling_price input.
# Let's find where cart is updated.
# In Sales.jsx, it adds to cart with:
# { product_id: product.id, name: product.name, price: product.selling_price, quantity: 1 }
# For purchases, we want price to be product.unit_price (cost)
code = code.replace("price: product.selling_price", "price: product.unit_price")
code = code.replace("price: product.selling_price || 0", "price: product.unit_price || 0")

# And we add new_selling_price to the cart item
code = code.replace("quantity: 1 }", "quantity: 1, new_selling_price: product.selling_price }")

# In the render cart section:
cart_row_search = """<td>
                              <div className="d-flex align-items-center">
                                <Button variant="outline-secondary" size="sm" onClick={() => updateCartItemQuantity(index, item.quantity - 1)}>-</Button>
                                <span className="mx-2">{item.quantity}</span>
                                <Button variant="outline-secondary" size="sm" onClick={() => updateCartItemQuantity(index, item.quantity + 1)}>+</Button>
                              </div>
                            </td>
                            <td>{parseFloat(item.price).toFixed(2)}</td>
                            <td>{(item.quantity * item.price).toFixed(2)}</td>"""

cart_row_replace = """<td>
                              <div className="d-flex align-items-center">
                                <Button variant="outline-secondary" size="sm" onClick={() => updateCartItemQuantity(index, item.quantity - 1)}>-</Button>
                                <span className="mx-2">{item.quantity}</span>
                                <Button variant="outline-secondary" size="sm" onClick={() => updateCartItemQuantity(index, item.quantity + 1)}>+</Button>
                              </div>
                            </td>
                            <td>
                              <Form.Control
                                type="number"
                                size="sm"
                                value={item.price}
                                onChange={(e) => {
                                  const newCart = [...cart];
                                  newCart[index].price = e.target.value;
                                  setCart(newCart);
                                }}
                                style={{ width: '80px' }}
                              />
                            </td>
                            <td>
                              <Form.Control
                                type="number"
                                size="sm"
                                value={item.new_selling_price || ''}
                                onChange={(e) => {
                                  const newCart = [...cart];
                                  newCart[index].new_selling_price = e.target.value;
                                  setCart(newCart);
                                }}
                                placeholder="New Price"
                                style={{ width: '80px' }}
                              />
                            </td>
                            <td>{(item.quantity * item.price).toFixed(2)}</td>"""

code = code.replace(cart_row_search, cart_row_replace)

code = code.replace("<th>{t('price')}</th>", "<th>{t('unit_price')}</th>\n                              <th>{t('new_selling_price', 'New Selling Price')}</th>")

# Payload mapping
payload_search = """items: cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.price
      }))"""
payload_replace = """items: cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_cost: parseFloat(item.price),
        new_selling_price: item.new_selling_price ? parseFloat(item.new_selling_price) : null
      }))"""
code = code.replace(payload_search, payload_replace)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
