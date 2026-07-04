import pandas as pd

def append_swe_to_profiles(excel_path):
    try:
        # Read the file
        xls = pd.ExcelFile(excel_path)
        if "Product Profiles" not in xls.sheet_names:
            print(f"'Product Profiles' sheet not found in {excel_path}.")
            return
        
        # Read existing data
        df = pd.read_excel(excel_path, sheet_name="Product Profiles")
        
        # Check if SWE is already there
        print("Unique Product Types:", df["Product Type"].unique())
        if (df["Product Type"] == "SWE").any():
            print(f"SWE already exists in {excel_path}.")
            return
            
        # Create new rows
        new_rows = pd.DataFrame([
            {"Product Type": "SWE", "Color Name": "Antique Cherry Red", "Image Suffix": "AntiqueCherryRed", "SKUWA Letter": "R", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Product Type": "SWE", "Color Name": "Black", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Product Type": "SWE", "Color Name": "Military Green", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Product Type": "SWE", "Color Name": "Navy", "Image Suffix": "Navy", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Product Type": "SWE", "Color Name": "Sport Grey", "Image Suffix": "SportGrey", "SKUWA Letter": "H", "Base SKU Shift": "", "Base SKU": "UNGS"},
        ])
        
        # Concatenate and save back to excel while preserving other sheets
        df_new = pd.concat([df, new_rows], ignore_index=True)
        
        with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_new.to_excel(writer, sheet_name="Product Profiles", index=False)
            
        print(f"Updated {excel_path} successfully.")
    except Exception as e:
        print(f"Error updating {excel_path}: {e}")

append_swe_to_profiles(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\Product_Profiles_Template.xlsx")
append_swe_to_profiles(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Sweatshirt_mapping_config_fixed.xlsx")
