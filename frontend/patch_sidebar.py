import re

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/components/Sidebar.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Reports accordion with a single NavItem
pattern = re.compile(r'<CollapsableNavItem eventKey=\"reports/\" title=\{t\(\"reports\"\)\} icon=\{faChartBar\}>.*?</CollapsableNavItem>', re.DOTALL)
replacement = '<NavItem title={t("reports") || "Reports"} link={Routes.ReportsOverview.path} icon={faChartBar} />'
new_content = pattern.sub(replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Sidebar updated")
