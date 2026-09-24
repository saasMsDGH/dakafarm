import codecs

file_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/pos/Sales.jsx'

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# Replace the wrong one back to empty th
bad_jsx = '''<th className="text-right">Total</th>
                                <th></th>
                              </tr>'''
good_jsx = '''<th className="text-right">Total</th>
                                <th></th>
                              </tr>'''

content = content.replace(bad_jsx, good_jsx)

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)
