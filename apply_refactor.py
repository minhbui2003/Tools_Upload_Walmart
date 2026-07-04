import re
import sys

def apply_refactor():
    with open('upload_toni.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_block_1 = """
class ProductProfileManager:
    def __init__(self, mapping_path=None):
        self.profiles = {}
        self.load_profiles(mapping_path)

    def load_profiles(self, mapping_path):
        import os
        import pandas as pd
        if not mapping_path or not os.path.exists(mapping_path):
            self._load_defaults()
            return
        
        try:
            df = pd.read_excel(mapping_path, sheet_name="Product Profiles", dtype=str).fillna("")
            for _, row in df.iterrows():
                ptype = clean_text(row.get("Product Type")).upper()
                if not ptype: continue
                
                rule = {
                    "Color Name": clean_text(row.get("Color Name")).upper(),
                    "Image Suffix": clean_text(row.get("Image Suffix")),
                    "SKUWA Letter": clean_text(row.get("SKUWA Letter")),
                    "Base SKU Shift": clean_text(row.get("Base SKU Shift"))
                }
                
                if ptype not in self.profiles:
                    self.profiles[ptype] = []
                self.profiles[ptype].append(rule)
                
            if not self.profiles:
                self._load_defaults()
        except Exception:
            self._load_defaults()
            
    def _load_defaults(self):
        self.profiles["TSH"] = [
            {"Color Name": "BLACK", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": ""},
            {"Color Name": "NAVY", "Image Suffix": "2", "SKUWA Letter": "N", "Base SKU Shift": ""},
            {"Color Name": "GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4"},
            {"Color Name": "SPORT GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4"},
            {"Color Name": "GREEN", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3"},
            {"Color Name": "MILITARY GREEN", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3"},
        ]

    def get_rules_for_type(self, product_type):
        ptype = clean_text(product_type).upper()
        if not ptype:
            ptype = "TSH"
        return self.profiles.get(ptype, self.profiles.get("TSH", []))

    def get_color_rule(self, product_type, color_name):
        rules = self.get_rules_for_type(product_type)
        color_upper = clean_text(color_name).upper()
        
        for rule in rules:
            if rule["Color Name"] == color_upper:
                return rule
                
        suffix = clean_text(color_name).replace(" ", "")
        return {"Color Name": color_upper, "Image Suffix": suffix, "SKUWA Letter": "", "Base SKU Shift": ""}

    def detect_color_rule_from_filename(self, product_type, filename_without_ext):
        normalized = filename_without_ext.upper().replace("_", " ").replace("-", " ")
        rules = self.get_rules_for_type(product_type)
        
        for rule in sorted(rules, key=lambda x: len(x["Color Name"]), reverse=True):
            if rule["Color Name"] in normalized:
                return rule
        return None

def apply_sku_shift(sku_prefix, shift):
    if shift and ("UNGT1" in sku_prefix or "UGNT1" in sku_prefix):
        return sku_prefix.replace("UNGT1", f"UNGT{shift}").replace("UGNT1", f"UGNT{shift}")
    return sku_prefix

def get_sku_by_color(sku_prefix, color, product_type, profile_manager):
    rule = profile_manager.get_color_rule(product_type, color)
    return apply_sku_shift(sku_prefix, rule["Base SKU Shift"])

def color_to_skuwa_letter(color, product_type, profile_manager):
    rule = profile_manager.get_color_rule(product_type, color)
    return rule["SKUWA Letter"]

def size_to_skuwa_code(size):
    size_text = clean_text(size).upper().replace(" ", "")
    size_map = {
        "S": "00S", "M": "00M", "L": "00L", "XL": "0XL",
        "2XL": "2XL", "3XL": "3XL", "4XL": "4XL", "5XL": "5XL",
    }
    return size_map.get(size_text, size_text)

def build_skuwa_suffix(color, size, product_type, profile_manager):
    color_code = color_to_skuwa_letter(color, product_type, profile_manager)
    size_code = size_to_skuwa_code(size)
    if not color_code or not size_code:
        return ""
    return f"{color_code}{size_code}"

def looks_like_full_skuwa(value):
    text = clean_text(value).upper()
    return "UGNT" in text or "UNGT" in text

def get_sku_by_image_code(sku_prefix, image_code, product_type, profile_manager):
    code = clean_text(image_code)
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        if rule["Image Suffix"]:
            suffix = f"-{rule['Image Suffix']}"
            if code.upper().endswith(suffix.upper()):
                return apply_sku_shift(sku_prefix, rule["Base SKU Shift"])
    return sku_prefix

def get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):
    variants = [sku_prefix]
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        shifted = apply_sku_shift(sku_prefix, rule["Base SKU Shift"])
        if shifted not in variants:
            variants.append(shifted)
    return variants

def build_base_mockup_code(filename_without_ext, product_type, profile_manager):
    name = clean_text(filename_without_ext)
    rules = profile_manager.get_rules_for_type(product_type)
    
    for rule in rules:
        if rule["Image Suffix"]:
            suffix = f"-{rule['Image Suffix']}"
            if name.upper().endswith(suffix.upper()):
                return name

    rule = profile_manager.detect_color_rule_from_filename(product_type, filename_without_ext)
    if not rule:
        return None
        
    base_name = name
    import re
    if rule["Color Name"]:
        base_name = re.sub(re.escape(rule["Color Name"]), "", base_name, flags=re.IGNORECASE)
    base_name = base_name.strip()
    base_name = base_name.rstrip("-_ ")
    base_name = base_name.strip()
    
    if not base_name or not rule["Image Suffix"]:
        return None
        
    return f"{base_name}-{rule['Image Suffix']}"

def is_already_full_image_code(value):
    text = clean_text(value).upper()
    return ("UNGT" in text or "UGNT" in text) and ("MK" in text or "IN" in text or "SW" in text)

def build_full_image_code(sku_prefix, short_code, color, product_type, profile_manager):
    code = clean_text(short_code)
    if code == "":
        return ""
    if is_already_full_image_code(code):
        return code
    adjusted_sku = get_sku_by_color(sku_prefix, color, product_type, profile_manager)
    return f"{adjusted_sku}{code}"

def get_unique_output_path(output_folder, new_filename):"""
    
    content = re.sub(
        r'def replace_variant_code\(sku_prefix, target_number\):.*?def get_unique_output_path\(output_folder, new_filename\):',
        new_block_1,
        content,
        flags=re.DOTALL
    )

    # rename_images
    content = content.replace("def rename_images(input_folder, output_folder, sku_prefix, log_callback=None):", "def rename_images(input_folder, output_folder, sku_prefix, product_type, profile_manager, log_callback=None):")
    content = content.replace("mockup_code = build_base_mockup_code(filename_without_ext)", "mockup_code = build_base_mockup_code(filename_without_ext, product_type, profile_manager)")
    content = content.replace("for sku_variant in get_sku_variants_for_common_asset(sku_prefix):", "for sku_variant in get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):")
    content = content.replace("adjusted_sku = get_sku_by_image_code(sku_prefix, mockup_code)", "adjusted_sku = get_sku_by_image_code(sku_prefix, mockup_code, product_type, profile_manager)")

    # build_full_skuwa_from_row
    content = content.replace("def build_full_skuwa_from_row(row, fallback_prefix):", "def build_full_skuwa_from_row(row, fallback_prefix, product_type, profile_manager):")
    content = content.replace("adjusted_sku = get_sku_by_color(base_prefix, color)", "adjusted_sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)")
    content = content.replace("suffix = build_skuwa_suffix(color, size)", "suffix = build_skuwa_suffix(color, size, product_type, profile_manager)")

    # prepare_update_df
    content = content.replace("def prepare_update_df(update_df, sku_prefix, log_callback=None):", "def prepare_update_df(update_df, sku_prefix, product_type, profile_manager, log_callback=None):")
    content = content.replace("adjusted_sku = get_sku_by_color(base_prefix, color)", "adjusted_sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)")
    content = content.replace("full_skuwa = build_full_skuwa_from_row(row, sku_prefix)", "full_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)")

    # process_getlinks_template
    content = content.replace("def process_getlinks_template(\n    template_path,\n    image_folder,\n    output_folder,\n    env_path,\n    sku_prefix,\n    cloud_folder,\n    log_callback=None\n):", "def process_getlinks_template(\n    template_path,\n    image_folder,\n    output_folder,\n    env_path,\n    sku_prefix,\n    cloud_folder,\n    product_type,\n    profile_manager,\n    log_callback=None\n):")
    content = content.replace("sku = get_sku_by_color(base_prefix, color)", "sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)")
    content = content.replace("final_skuwa = build_full_skuwa_from_row(row, sku_prefix)", "final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)")
    content = content.replace("full_image_code = build_full_image_code(sku_prefix, short_code, color)", "full_image_code = build_full_image_code(sku_prefix, short_code, color, product_type, profile_manager)")

    # generate_walmart_xlsx_from_getlinks_df
    content = content.replace("def generate_walmart_xlsx_from_getlinks_df(\n    seller_template_path,\n    getlinks_df,\n    mapping_path,\n    update_file_path,\n    output_folder,\n    sku_prefix,\n    log_callback=None\n):", "def generate_walmart_xlsx_from_getlinks_df(\n    seller_template_path,\n    getlinks_df,\n    mapping_path,\n    update_file_path,\n    output_folder,\n    sku_prefix,\n    product_type,\n    profile_manager,\n    log_callback=None\n):")
    content = content.replace("update_df = prepare_update_df(update_df, sku_prefix, log_callback=log_callback)", "update_df = prepare_update_df(update_df, sku_prefix, product_type, profile_manager, log_callback=log_callback)")

    # UI updates
    new_ui_entry = """        ttk.Label(main_frame, text="2. SKU Prefix:").pack(anchor="w", pady=(8, 4))
        self.sku_var = tk.StringVar()
        self.sku_entry = ttk.Entry(main_frame, textvariable=self.sku_var)
        self.sku_entry.pack(fill="x")
        
        ttk.Label(main_frame, text="2.5. Product Type ID:").pack(anchor="w", pady=(8, 4))
        self.product_type_var = tk.StringVar(value="TSH")
        self.product_type_entry = ttk.Entry(main_frame, textvariable=self.product_type_var)
        self.product_type_entry.pack(fill="x")"""
    content = content.replace('        ttk.Label(main_frame, text="2. SKU Prefix:").pack(anchor="w", pady=(8, 4))\n        self.sku_var = tk.StringVar()\n        self.sku_entry = ttk.Entry(main_frame, textvariable=self.sku_var)\n        self.sku_entry.pack(fill="x")', new_ui_entry)

    # validate_inputs
    content = content.replace("cloud_folder = self.batch_var.get().strip()", "cloud_folder = self.batch_var.get().strip()\n        product_type = self.product_type_var.get().strip()")
    content = content.replace("return sku_prefix, cloud_folder", "return sku_prefix, cloud_folder, product_type")

    # preview
    content = content.replace("sku_prefix, cloud_folder = result", "sku_prefix, cloud_folder, product_type = result\n        profile_manager = ProductProfileManager(self.mapping_path)")
    content = content.replace("sku = get_sku_by_color(sku_prefix, color)", "sku = get_sku_by_color(sku_prefix, color, product_type, profile_manager)")
    content = content.replace("final_skuwa = build_full_skuwa_from_row(row, sku_prefix)", "final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)")

    # run_all
    content = content.replace("thread = threading.Thread(target=self.run_all, args=(sku_prefix, cloud_folder))", "thread = threading.Thread(target=self.run_all, args=(sku_prefix, cloud_folder, product_type))")
    content = content.replace("def run_all(self, sku_prefix, cloud_folder):", "def run_all(self, sku_prefix, cloud_folder, product_type):\n        profile_manager = ProductProfileManager(self.mapping_path)")
    
    content = content.replace(
        "sku_prefix=sku_prefix,\n                    log_callback=self.write_log",
        "sku_prefix=sku_prefix,\n                    product_type=product_type,\n                    profile_manager=profile_manager,\n                    log_callback=self.write_log"
    )
    content = content.replace(
        "cloud_folder=cloud_folder,\n                log_callback=self.write_log",
        "cloud_folder=cloud_folder,\n                product_type=product_type,\n                profile_manager=profile_manager,\n                log_callback=self.write_log"
    )
    content = content.replace(
        "sku_prefix=sku_prefix,\n                log_callback=self.write_log",
        "sku_prefix=sku_prefix,\n                product_type=product_type,\n                profile_manager=profile_manager,\n                log_callback=self.write_log"
    )

    with open('upload_toni_new.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Refactoring applied to upload_toni_new.py")

if __name__ == "__main__":
    apply_refactor()
