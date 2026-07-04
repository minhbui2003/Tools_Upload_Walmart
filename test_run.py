import sys
import os
import shutil

sys.path.append(r"d:\POD\Tools\POD_Marketplace\Upload-Toni")
from upload_toni import ProductProfileManager, rename_images, process_getlinks_template, generate_walmart_xlsx_from_getlinks_df
import pandas as pd

input_folder = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\Nas\Win\080626TA4"
output_folder = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\test_output"

if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

sku_prefix = "080626TA4"
product_type = "SWE"
mapping_path = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Tshirt_mapping_config.xlsx"
getlinks_template = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\templates\swe_template.xlsx"
seller_template = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\sample-files\Tshirt-walmart-template-220626.xlsx"
update_file = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\Nas\Win\080626TA4\Tshirt_update_file_080626TA4.xlsx"
cloud_folder = "test-batch-001"
env_path = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\.env"

mapping_df = pd.read_excel(mapping_path, sheet_name=None)
profile_df = pd.read_excel(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\Product_Profiles_Template.xlsx", sheet_name="Product Profiles")

# Add missing color mappings to profile_df that are used in the update file
profile_df.loc[len(profile_df)] = {"Product Type": "SWE", "Color Name": "GREY", "Image Suffix": "GREY", "SKUWA Letter": "H", "Base SKU Shift": "", "Base SKU": ""}
profile_df.loc[len(profile_df)] = {"Product Type": "SWE", "Color Name": "GREEN", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "", "Base SKU": ""}

with pd.ExcelWriter(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\test_mapping.xlsx") as writer:
    for sheet_name, df in mapping_df.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    profile_df.to_excel(writer, sheet_name="Product Profiles", index=False)

test_mapping_path = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\test_mapping.xlsx"
profile_manager = ProductProfileManager(test_mapping_path)

def log_cb(msg):
    pass

renamed_folder = os.path.join(output_folder, "renamed_images")
print("1. Renaming images...")
rename_images(input_folder, renamed_folder, sku_prefix, product_type, profile_manager, log_callback=log_cb)

print("2. Processing Getlinks...")
process_getlinks_template(
    getlinks_template,
    renamed_folder,
    output_folder,
    env_path,
    sku_prefix,
    cloud_folder,
    product_type,
    profile_manager,
    log_callback=log_cb
)

getlinks_csv = None
for f in os.listdir(output_folder):
    if f.startswith("getlinks_output") and f.endswith(".csv"):
        getlinks_csv = os.path.join(output_folder, f)

if getlinks_csv:
    print(f"Found getlinks csv: {getlinks_csv}")
    print("3. Generating Walmart XLSX...")
    generate_walmart_xlsx_from_getlinks_df(
        seller_template,
        pd.read_csv(getlinks_csv, dtype=str).fillna(""),
        test_mapping_path,
        update_file,
        output_folder,
        sku_prefix,
        product_type,
        profile_manager,
        log_callback=log_cb
    )
    print("DONE! Check the test_output folder.")
else:
    print("Error: Getlinks CSV not found!")
