import pandas as pd

colors = [
    {'name': 'Antique Cherry Red', 's': 'AntiqueCherryRed'},
    {'name': 'Black', 's': 'Black'},
    {'name': 'Military Green', 's': 'MilitaryGreen'},
    {'name': 'Navy', 's': 'Navy'},
    {'name': 'Sport Grey', 's': 'SportGrey'}
]
sizes = ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']
cols = ['SKU', 'COLOR', 'SIZE', 'SKUWA', 'Main', 'Main Image_URL', 'Add 1', 'Add1 URL (+)', 'Add 2', 'Add2 URL (+)', 'Add 3', 'Add3 URL (+)', 'Add 4', 'Add4 URL (+)', 'Add 5', 'Add5 URL (+)', 'Swatch', 'Swatch URL']

data = []
for c in colors:
    for s in sizes:
        row = {col: '' for col in cols}
        row['COLOR'] = c['name']
        row['SIZE'] = s
        row['Main'] = f"MK3-{c['s']}"
        row['Add 1'] = 'In1'
        row['Add 2'] = f"MK4-{c['s']}"
        row['Add 3'] = f"MK2-{c['s']}"
        row['Add 4'] = 'In2'
        row['Add 5'] = 'In3'
        row['Swatch'] = f"sw-{c['s']}"
        data.append(row)

df = pd.DataFrame(data)
df.to_excel(r'd:\POD\Tools\POD_Marketplace\Upload-Toni\templates\swe_template.xlsx', index=False)
print("Created swe_template.xlsx")
