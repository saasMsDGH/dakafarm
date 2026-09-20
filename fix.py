
import os
with open(frontend/src/routes.js, r) as f:
    c = f.read()
if UsersManagement not in c:
    c = c.replace(};,  // Admin\n UsersManagement: { path: /admin/users },\n};\n)
    with open(frontend/src/routes.js, w) as f:
        f.write(c)

