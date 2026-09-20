import re

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/HomePage.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all reports imports
import_pattern = re.compile(r'// reports\n.*// components', re.DOTALL)
content = import_pattern.sub('// reports\nimport FarmOperationsReport from \"./reports/FarmOperationsReport\";\n\n// components', content)

# Replace all reports routes
routes_pattern = re.compile(r'\{/\* reports pages \*/\}.*?(?=<Redirect)', re.DOTALL)
content = routes_pattern.sub('{/* reports pages */}\n    <RouteWithSidebar exact path={Routes.ReportsOverview.path} component={FarmOperationsReport} />\n\n    ', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("HomePage.jsx updated")
