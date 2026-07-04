import pandas as pd
import os

template_dir = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\templates"

color_map = {
    "Navy": "Sand",
    "Grey": "Sport Grey",
    "Green": "White"
}

def convert_to_w(file_in, file_out):
    df = pd.read_excel(file_in)
    
    # Map colors
    df['COLOR'] = df['COLOR'].replace(color_map)
    
    # Map SKUWA letters if present
    if 'SKUWA' in df.columns:
        def replace_skuwa(x):
            if pd.isna(x): return x
            x = str(x)
            if x.startswith('N'): # Navy -> Sand (Y)
                return 'Y' + x[1:]
            if x.startswith('F'): # Green -> White (W)
                return 'W' + x[1:]
            return x
        df['SKUWA'] = df['SKUWA'].apply(replace_skuwa)
        
    df.to_excel(file_out, index=False)

for i in range(1, 5):
    file_in = os.path.join(template_dir, f"tshirt{i}_template.xlsx")
    file_out = os.path.join(template_dir, f"tshirt_w{i}_template.xlsx")
    convert_to_w(file_in, file_out)
    print(f"Created {file_out}")
