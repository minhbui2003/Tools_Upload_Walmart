import pandas as pd
import os

out_dir = r'd:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Update'
os.makedirs(out_dir, exist_ok=True)

sizes = ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

columns = [
    'SKU', 'COLOR', 'SIZE', 'SKUWA', 'Product Name', 'Selling Price', 
    'Site Description', 'Key Features (+)', 'Key Features 1 (+)', 
    'Key Features 2 (+)', 'Key Features 3 (+)', 'Key Features 4 (+)', 
    'Brand Name', 'Color', 'Color Category (+)', 'Swatch Image URL', 
    'Site Start Date', 'Site End Date', 'Variant Group ID'
]

# Color Category Mapping
color_cat_map = {
    'Black': 'Black',
    'Grey': 'Gray',
    'Sport Grey': 'Gray',
    'Sand': 'Beige',
    'White': 'White',
    'Antique Cherry Red': 'Red',
    'Military Green': 'Green',
    'Navy': 'Blue'
}

# SKUWA Letter Mapping
skuwa_letter_map = {
    'Black': 'B',
    'Grey': 'H',
    'Sand': 'S',
    'White': 'W',
    'Antique Cherry Red': 'R',
    'Military Green': 'F',
    'Navy': 'N',
    'Sport Grey': 'H'
}

def get_skuwa_suffix(size):
    if size in ['S', 'M', 'L']:
        return f"00{size}"
    elif size == 'XL':
        return "0XL"
    return size

feature1 = "Premium Mid-Weight Comfort: Expertly spun from ultra-soft cotton for a structured, classic look. Keeps your loved ones entirely cool and comfortable during any family squad getaway."
feature2 = "Advanced Flex-Fiber Printing: Vibrant inks fuse directly into fabric layers. The high-contrast graphic remains completely flexible, stretchable, and crack-free through countless wash cycles."
start_date = '2026-06-23'
end_date = '2056-12-18'

def create_template(filename, colors):
    data = []
    for c in colors:
        for s in sizes:
            row = {col: '' for col in columns}
            row['COLOR'] = c
            row['SIZE'] = s
            
            # Fill the requested columns
            letter = skuwa_letter_map.get(c, '')
            row['SKUWA'] = f"{letter}{get_skuwa_suffix(s)}"
            row['Key Features 1 (+)'] = feature1
            row['Key Features 2 (+)'] = feature2
            row['Color'] = c
            row['Color Category (+)'] = color_cat_map.get(c, '')
            row['Site Start Date'] = start_date
            row['Site End Date'] = end_date
            
            data.append(row)

    df = pd.DataFrame(data)
    path = os.path.join(out_dir, filename)
    df.to_excel(path, index=False)
    print(f"Created {path}")

create_template('TSH_W_update_file_template.xlsx', ['Black', 'Grey', 'Sand', 'White'])
create_template('SWE_update_file_template.xlsx', ['Antique Cherry Red', 'Black', 'Military Green', 'Navy', 'Sport Grey'])
