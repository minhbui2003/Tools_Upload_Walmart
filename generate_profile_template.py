import pandas as pd
import os

def generate_template():
    data = [
        # T-Shirt (Hardcoded defaults translated to data)
        {"Product Type": "TSH", "Color Name": "Black", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UGNT1"},
        {"Product Type": "TSH", "Color Name": "Navy", "Image Suffix": "2", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UGNT1"},
        {"Product Type": "TSH", "Color Name": "Grey", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UGNT1"},
        {"Product Type": "TSH", "Color Name": "Sport Grey", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UGNT1"},
        {"Product Type": "TSH", "Color Name": "Green", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UGNT1"},
        {"Product Type": "TSH", "Color Name": "Military Green", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UGNT1"},
        
        # Women's T-Shirt examples
        {"Product Type": "TSH_W", "Color Name": "Black", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "WUGNT1"},
        {"Product Type": "TSH_W", "Color Name": "Grey", "Image Suffix": "Grey", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "WUGNT1"},
        {"Product Type": "TSH_W", "Color Name": "Sand", "Image Suffix": "Sand", "SKUWA Letter": "S", "Base SKU Shift": "", "Base SKU": "WUGNT1"},
        {"Product Type": "TSH_W", "Color Name": "White", "Image Suffix": "White", "SKUWA Letter": "W", "Base SKU Shift": "", "Base SKU": "WUGNT1"},
        
        # Sweatshirt examples
        {"Product Type": "SWE", "Color Name": "Antique Cherry Red", "Image Suffix": "AntiqueCherryRed", "SKUWA Letter": "R", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Black", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Military Green", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Green", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Navy", "Image Suffix": "Navy", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Sport Grey", "Image Suffix": "SportGrey", "SKUWA Letter": "H", "Base SKU Shift": "", "Base SKU": "SWE1"},
        {"Product Type": "SWE", "Color Name": "Grey", "Image Suffix": "Grey", "SKUWA Letter": "H", "Base SKU Shift": "", "Base SKU": "SWE1"},
    ]
    
    df = pd.DataFrame(data)
    output_path = "Product_Profiles_Template.xlsx"
    df.to_excel(output_path, sheet_name="Product Profiles", index=False)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_template()
