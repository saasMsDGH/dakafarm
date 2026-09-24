import codecs
import re

file_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/components/Sidebar.jsx'

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

styles = '''
      <style>
        {
          .sidebar .nav-link {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .sidebar .sidebar-icon {
            font-size: 0.9rem !important;
            margin-right: 0.5rem !important;
          }
          .sidebar .accordion-button {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .sidebar .accordion-button::after {
            width: 0.75rem;
            height: 0.75rem;
            background-size: 0.75rem;
          }
          .sidebar .multi-level .nav-link {
            padding-left: 2.25rem !important;
            padding-top: 0.35rem !important;
            padding-bottom: 0.35rem !important;
          }
          .sidebar .sidebar-inner {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
          }
          .sidebar .nav-item {
            margin-bottom: 0.1rem;
          }
          .simplebar-content {
             overflow-x: hidden !important;
          }
        }
      </style>
'''

content = re.sub(r'(return\s*\(\s*<>)', r'\1' + styles, content)

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)
print("Regex replacement completed")
