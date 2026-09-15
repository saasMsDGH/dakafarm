with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Fix the broken state variable names
code = code.replace("show{t('view_sale')}Modal", "showViewModal")
code = code.replace("setShow{t('view_sale')}Modal", "setShowViewModal")
code = code.replace("handle{t('view_sale')}Sale", "handleViewSale")

# But we do want it in the button text!
# Let's check where it should be.
# It was <Button variant="info" size="sm" onClick={() => handleViewSale(sale.id)} className="me-2">
#                   <FontAwesomeIcon icon={faEye} className="me-1" /> View
#                 </Button>
# Wait, my replacement probably changed `View` inside the button to `{t('view_sale')}`.
# Let's fix just the JS variables.

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
