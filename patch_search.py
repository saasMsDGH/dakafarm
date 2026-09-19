import os
import glob

files = glob.glob('frontend/src/pages/**/*.jsx', recursive=True)

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Search for common patterns where searchTerm is updated without resetting page
    # In some files it's setSearchTerm, in others it's setCSearch / setRSearch etc.
    # But usually it's setPage(1) that is missing.
    
    # Standard searchTerm
    if 'onChange={(e) => setSearchTerm(e.target.value)}' in content:
        content = content.replace(
            'onChange={(e) => setSearchTerm(e.target.value)}', 
            'onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}'
        )
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed searchTerm in {path}")
        
    # rSearch and pSearch in Debts.jsx
    if 'onChange={(e) => setRSearch(e.target.value)}' in content:
        content = content.replace(
            'onChange={(e) => setRSearch(e.target.value)}', 
            'onChange={(e) => { setRSearch(e.target.value); setRPage(1); }}'
        )
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed rSearch in {path}")
        
    if 'onChange={(e) => setPSearch(e.target.value)}' in content:
        content = content.replace(
            'onChange={(e) => setPSearch(e.target.value)}', 
            'onChange={(e) => { setPSearch(e.target.value); setPPage(1); }}'
        )
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed pSearch in {path}")

print("Search patch complete!")
