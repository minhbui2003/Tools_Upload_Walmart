import pandas as pd
import sys
from openpyxl.utils.cell import column_index_from_string

def validate_mapping(mapping_path, update_path, template_path):
    print(f"--- Validating Set ---")
    print(f"Mapping: {mapping_path}")
    print(f"Update: {update_path}")
    print(f"Template: {template_path}")
    
    try:
        # Load mapping
        map_df = pd.read_excel(mapping_path, sheet_name="Mapping")
        map_df = map_df[map_df["Enabled"].str.upper().isin(["Y", "YES", "TRUE", "1", "ENABLE", "ENABLED"])]
        
        # Load Update file headers
        try:
            update_df = pd.read_excel(update_path)
            update_cols = [str(c).strip() for c in update_df.columns]
        except Exception as e:
            print(f"  [ERROR] Cannot load update file: {e}")
            return

        # Load Template headers
        try:
            # We assume sheet is 'Product Content And Site Exp' and header row is 4, as per existing logic
            # Let's read the first row of the mapping to find the sheet and header row
            first_mapping = map_df.iloc[0]
            sheet_name = first_mapping.get("Seller Sheet", "Product Content And Site Exp")
            header_row = int(first_mapping.get("Seller Header Row", 4))
            
            template_df = pd.read_excel(template_path, sheet_name=sheet_name, header=header_row-1, nrows=0)
            template_cols = list(template_df.columns)
            # template_cols is a list of header strings. But Mapping uses 'Seller Excel Col' (A, B, C...)
            # We don't strictly need to check template column names, but we can verify the Excel Col index doesn't exceed template width.
        except Exception as e:
            print(f"  [ERROR] Cannot load template file: {e}")
            return
            
        # Check mapping logic
        errors = []
        for idx, row in map_df.iterrows():
            source_type = str(row.get("Source Type")).strip()
            source_value = str(row.get("Source Value")).strip()
            excel_col = str(row.get("Seller Excel Col")).strip()
            seller_column_name = str(row.get("Seller Column")).strip()
            
            # Check excel col
            try:
                col_idx = column_index_from_string(excel_col)
                if col_idx > len(template_cols) + 50: # just a generous boundary
                    pass
            except:
                errors.append(f"Invalid Excel Col '{excel_col}' for '{seller_column_name}'")
                
            if source_type == "update_file":
                # Check if source_value is in update_cols
                if source_value not in update_cols and source_value != "nan":
                    # Let's normalize strings to be safe
                    norm_update_cols = [c.lower().replace(" ", "") for c in update_cols]
                    norm_val = source_value.lower().replace(" ", "")
                    if norm_val not in norm_update_cols:
                        errors.append(f"Missing column '{source_value}' in Update file (mapped to {excel_col}: {seller_column_name})")
        
        if errors:
            for e in errors:
                print(f"  [ERROR] {e}")
        else:
            print("  [OK] Mapping -> Update File is consistent.")
            
    except Exception as e:
        print(f"  [ERROR] Validation crashed: {e}")
    print()

validate_mapping(
    "sample-files/Sweatshirt_mapping_config_fixed.xlsx",
    "sample-files/Update/SWE_update_file_template.xlsx",
    "sample-files/Sweatshirt-walmart-template-0626.xlsx"
)

validate_mapping(
    "sample-files/Tshirt_mapping_config_220626.xlsx",
    "sample-files/Update/Tshirt_update_file_130526TA5W.xlsx",
    "sample-files/Tshirt-walmart-template-220626.xlsx"
)

validate_mapping(
    "sample-files/Tshirt_mapping_config_220626.xlsx",
    "sample-files/Update/TSH_W_update_file_template.xlsx",
    "sample-files/Tshirt-walmart-template-220626.xlsx"
)
