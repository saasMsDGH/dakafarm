with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()
import re

search_purchases_qty = r'<td className="align-middle text-center">\s*<div className="d-flex align-items-center justify-content-center">\s*<Button variant="light" size="sm" className="px-2 py-0"\s*onClick=\{\(\) => \{\s*const newQty = Math\.max\(1, item\.quantity - 1\);\s*const newCart = \[\.\.\.cartItems\];\s*newCart\[idx\]\.quantity = newQty;\s*setCartItems\(newCart\);\s*\}\}>-</Button>\s*<span className="mx-2">\{item\.quantity\}</span>\s*<Button variant="light" size="sm" className="px-2 py-0"\s*onClick=\{\(\) => \{\s*const prod = products\.find\(p => p\.id === item\.product_id\);\s*if \(item\.quantity \+ 1 > prod\.current_stock\) \{\s*Swal\.fire\(\'Warning\', \'Stock limit reached\', \'warning\'\);\s*return;\s*\}\s*const newCart = \[\.\.\.cartItems\];\s*newCart\[idx\]\.quantity = item\.quantity \+ 1;\s*setCartItems\(newCart\);\s*\}\}>\+</Button>\s*</div>\s*</td>'

replace_purchases_qty = """<td className="align-middle text-center">
                                    <Form.Control type="number" size="sm" value={item.quantity} onChange={(e) => {
                                        const val = e.target.value;
                                        const newCart = [...cartItems];
                                        newCart[idx].quantity = val;
                                        setCartItems(newCart);
                                    }} style={{width: '60px', padding: '0.25rem', fontSize: '0.8rem', margin: '0 auto'}}/>
                                  </td>"""

code = re.sub(search_purchases_qty, replace_purchases_qty, code)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)

with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    sales_code = f.read()

search_sales_qty = r'<td className="align-middle text-center">\s*<div className="d-flex align-items-center justify-content-center">\s*<Button variant="light" size="sm" className="px-2 py-0"\s*onClick=\{\(\) => \{\s*const newQty = Math\.max\(1, item\.quantity - 1\);\s*const newCart = \[\.\.\.cartItems\];\s*newCart\[idx\]\.quantity = newQty;\s*setCartItems\(newCart\);\s*\}\}>-</Button>\s*<span className="mx-2">\{item\.quantity\}</span>\s*<Button variant="light" size="sm" className="px-2 py-0"\s*onClick=\{\(\) => \{\s*const prod = products\.find\(p => p\.id === item\.product_id\);\s*if \(item\.quantity \+ 1 > prod\.current_stock\) \{\s*Swal\.fire\(\'Warning\', \'Stock limit reached\', \'warning\'\);\s*return;\s*\}\s*const newCart = \[\.\.\.cartItems\];\s*newCart\[idx\]\.quantity = item\.quantity \+ 1;\s*setCartItems\(newCart\);\s*\}\}>\+</Button>\s*</div>\s*</td>'

replace_sales_qty = """<td className="align-middle text-center">
                                    <Form.Control type="number" size="sm" value={item.quantity} onChange={(e) => {
                                        let val = parseFloat(e.target.value);
                                        const prod = products.find(p => p.id === item.product_id);
                                        if (val > prod.current_stock) {
                                            Swal.fire('Warning', `Only ${prod.current_stock} in stock!`, 'warning');
                                            val = prod.current_stock;
                                        }
                                        const newCart = [...cartItems];
                                        newCart[idx].quantity = isNaN(val) ? e.target.value : val;
                                        setCartItems(newCart);
                                    }} style={{width: '60px', padding: '0.25rem', fontSize: '0.8rem', margin: '0 auto'}}/>
                                  </td>"""

sales_code = re.sub(search_sales_qty, replace_sales_qty, sales_code)

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(sales_code)
