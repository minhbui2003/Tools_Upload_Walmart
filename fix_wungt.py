import os

files_to_fix = [
    r'd:\POD\Tools\POD_Marketplace\Upload-Toni\core\profile.py',
    r'd:\POD\Tools\POD_Marketplace\Upload-Toni\upload_toni.py',
    r'd:\POD\Tools\POD_Marketplace\Upload-Toni\core\sku.py'
]

for fpath in files_to_fix:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace "WUNGT1" with "UNGT1"
    new_content = content.replace('"WUNGT1"', '"UNGT1"')
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Fixed {fpath}')
