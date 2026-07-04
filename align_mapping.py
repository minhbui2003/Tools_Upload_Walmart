import pandas as pd
from openpyxl.utils.cell import get_column_letter
import os

template_file = r'd:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Sweatshirt-walmart-template-1706-1130526TA3.xlsx'
mapping_file = r'd:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Sweatshirt_mapping_config.xlsx'

# Read template headers
df_template = pd.read_excel(template_file, sheet_name='Product Content And Site Exp', header=None, nrows=5)
headers = df_template.iloc[3].fillna('').astype(str).tolist()

# Build a map of header -> list of column letters
header_to_cols = {}
for i, h in enumerate(headers):
    if not h: continue
    h_clean = h.strip()
    if h_clean not in header_to_cols:
        header_to_cols[h_clean] = []
    header_to_cols[h_clean].append(get_column_letter(i + 1))

# Read mapping
df_mapping = pd.read_excel(mapping_file, sheet_name='Mapping')

# We need to keep track of how many times we've seen a header (like Additional Image URL (+))
# so we can assign the next available column
usage_count = {}

for i, row in df_mapping.iterrows():
    seller_col = str(row.get('Seller Column')).strip()
    if not seller_col or seller_col == 'nan':
        continue
        
    if seller_col in header_to_cols:
        count = usage_count.get(seller_col, 0)
        cols = header_to_cols[seller_col]
        
        if count < len(cols):
            new_col = cols[count]
            df_mapping.at[i, 'Seller Excel Col'] = new_col
            usage_count[seller_col] = count + 1
        else:
            # If mapping asks for more columns than template has, just map to the last one or leave as is
            df_mapping.at[i, 'Seller Excel Col'] = cols[-1]

df_mapping.to_excel(r'd:\POD\Tools\POD_Marketplace\Upload-Toni\Sweatshirt_mapping_aligned.xlsx', sheet_name='Mapping', index=False)
print("Aligned mapping saved to Sweatshirt_mapping_aligned.xlsx")
