import os

docs_dir = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/docs'
output_path = os.path.join(docs_dir, 'frontend.md')

with open(output_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace box characters
text = text.replace('+--', '|--')
text = text.replace('+--', '--')
text = text.replace('¦', '|')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(text)
