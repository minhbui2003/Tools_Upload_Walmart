import pandas as pd
import os

mapping_file = r"sample-files\Sweatshirt_mapping_config.xlsx"
df = pd.read_excel(mapping_file)

def col2num(col):
    num = 0
    for c in str(col).strip():
        num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

def num2col(num):
    col = ""
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        col = chr(65 + remainder) + col
    return col

# Enable Key Features 3 and 4
kf3_idx = df[df['Seller Column'] == 'Key Features 3 (+)'].index
kf4_idx = df[df['Seller Column'] == 'Key Features 4 (+)'].index

if not kf3_idx.empty:
    df.loc[kf3_idx, 'Enabled'] = 'Y'
    df.loc[kf3_idx, 'Notes'] = 'From Update File bullet 4'
if not kf4_idx.empty:
    df.loc[kf4_idx, 'Enabled'] = 'Y'
    df.loc[kf4_idx, 'Notes'] = 'From Update File bullet 5'

# Shift all columns from Main Image URL onwards by 2
main_idx = df[df['Seller Column'] == 'Main Image URL'].index
if not main_idx.empty:
    start_idx = main_idx[0]
    for i in range(start_idx, len(df)):
        col_letter = df.loc[i, 'Seller Excel Col']
        if pd.notna(col_letter) and str(col_letter).strip() != "":
            # Check if it was already shifted (if it is V, we don't shift again!)
            # Wait, if it is T, we shift to V. 
            if i == start_idx and str(col_letter).strip().upper() == 'V':
                print("Already shifted.")
                break
            
            new_col = num2col(col2num(str(col_letter)) + 2)
            df.loc[i, 'Seller Excel Col'] = new_col

df.to_excel(mapping_file, index=False)
print("Updated mapping config.")
