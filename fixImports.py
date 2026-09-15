with open("frontend/src/pages/pos/Sales.jsx", "r") as f:
    code = f.read()

if "useAuth } from" not in code:
    code = code.replace("import React, { useState, useEffect } from \"react\";", "import React, { useState, useEffect } from \"react\";\nimport { useAuth } from '../../context/AuthContext';")

with open("frontend/src/pages/pos/Sales.jsx", "w") as f:
    f.write(code)
