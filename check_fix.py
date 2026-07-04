import sys
import os
import pandas as pd

sys.path.append(r"d:\POD\Tools\POD_Marketplace\Upload-Toni")
from core.profile import ProductProfileManager
from core.mapper import generate_walmart_xlsx_from_getlinks_df

fix_folder = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\Fix"
mapping_path = os.path.join(fix_folder, "mapping", "Tshirt_mapping_config_woman.xlsx")
getlinks_template = os.path.join(fix_folder, "templates", "tshirt_w1_template.xlsx")
update_file = os.path.join(fix_folder, "TSH_W_update_file_220626TA3.xlsx")
seller_template = os.path.join(fix_folder, "Tshirt-walmart-template-220626.xlsx")
output_folder = os.path.join(fix_folder, "output")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

profile_manager = ProductProfileManager(mapping_path)
sku_prefix = "220626TA3W"
product_type = "TSH_W"

print(f"Product Type: {product_type}")
print(f"Base SKU from profile: {profile_manager.get_base_sku(product_type)}")
print(f"SKU Prefix input: {sku_prefix}")

# Process getlinks manually to see SKUs
df = pd.read_excel(getlinks_template, dtype=object, keep_default_na=False).fillna("")

from core.utils import normalize_columns
from core.sku import get_base_prefix_for_row, get_sku_by_color, build_full_skuwa_from_row

df = normalize_columns(df)

if "SKU" not in df.columns: df["SKU"] = ""
if "SKUWA" not in df.columns: df["SKUWA"] = ""

for index, row in df.iterrows():
    color = row.get("COLOR")
    base_prefix = get_base_prefix_for_row(row, sku_prefix)
    sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)
    final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)
    
    df.at[index, "SKU"] = sku
    df.at[index, "SKUWA"] = final_skuwa

print("\n--- GENERATED SKUs (from getlinks template) ---")
print(df[["COLOR", "SIZE", "SKU", "SKUWA"]].head(10))

# Try Update file
if os.path.exists(update_file):
    print("\n--- UPDATE FILE SKUs ---")
    udf = pd.read_excel(update_file, dtype=object, keep_default_na=False).fillna("")
    udf = normalize_columns(udf)
    if "SKU" not in udf.columns: udf["SKU"] = ""
    if "SKUWA" not in udf.columns: udf["SKUWA"] = ""
    for index, row in udf.iterrows():
        color = row.get("COLOR")
        base_prefix = get_base_prefix_for_row(row, sku_prefix)
        sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)
        final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)
        udf.at[index, "SKU"] = sku
        udf.at[index, "SKUWA"] = final_skuwa
    print(udf[["COLOR", "SIZE", "SKU", "SKUWA"]].head(10))

print("\nDone!")
