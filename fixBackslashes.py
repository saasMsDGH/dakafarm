with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()
import re
code = re.sub(
    r"cursor: \\'pointer\\', transition: \\'transform 0\.1s\\' ",
    r"cursor: 'pointer', transition: 'transform 0.1s'",
    code
)
code = re.sub(
    r"style=\{\{ cursor: \\'pointer\\', transition: \\'transform 0\.1s\\' \}\}",
    r"style={{ cursor: 'pointer', transition: 'transform 0.1s' }}",
    code
)
code = re.sub(
    r"e\.currentTarget\.style\.transform = \\'scale\(1\.02\)\\'",
    r"e.currentTarget.style.transform = 'scale(1.02)'",
    code
)
with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
