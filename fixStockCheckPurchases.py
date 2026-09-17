with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Remove stock check from handleAddCartInput
code = re.sub(
    r'// Check stock\s*if \(cartInput\.quantity > prod\.current_stock\) \{\s*Swal\.fire\(\'Warning\', `Not enough stock! Only \$\{prod\.current_stock\} available\.`, \'warning\'\);\s*return;\s*\}',
    '',
    code
)

# Remove the disabled styling from the product cards (so you can click them even if stock is 0)
code = re.sub(
    r'className=\{\`h-100 product-card shadow-sm \$\{p\.current_stock <= 0 \? \'opacity-50\' : \'\'\}\`\}',
    r'className="h-100 product-card shadow-sm"',
    code
)

code = re.sub(
    r'style=\{\{ cursor: p\.current_stock > 0 \? \'pointer\' : \'not-allowed\', transition: \'transform 0\.1s\' \}\}',
    r'style={{ cursor: \'pointer\', transition: \'transform 0.1s\' }}',
    code
)

code = re.sub(
    r'onMouseOver=\{\(e\) => \{ if \(p\.current_stock > 0\) e\.currentTarget\.style\.transform = \'scale\(1\.02\)\'; \}\}',
    r'onMouseOver={(e) => e.currentTarget.style.transform = \'scale(1.02)\'}',
    code
)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
