import os

file_path = "upload_toni.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update defaults
old_defaults = """        self.profiles["TSH_W"] = [
            {"Color Name": "BLACK", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "WUNGT1"},
            {"Color Name": "SAND", "Image Suffix": "2", "SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "WUNGT1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "WUNGT1"},
            {"Color Name": "WHITE", "Image Suffix": "4", "SKUWA Letter": "W", "Base SKU Shift": "", "Base SKU": "WUNGT1"},
        ]"""
new_defaults = """        self.profiles["TSH_W"] = [
            {"Color Name": "BLACK", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "WUNGT1"},
            {"Color Name": "SAND", "Image Suffix": "2", "SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "WUNGT1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "WUNGT1"},
            {"Color Name": "WHITE", "Image Suffix": "4", "SKUWA Letter": "W", "Base SKU Shift": "", "Base SKU": "WUNGT1"},
        ]
        
        self.profiles["SWE"] = [
            {"Color Name": "ANTIQUE CHERRY RED", "Image Suffix": "AntiqueCherryRed", "SKUWA Letter": "R", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Color Name": "BLACK", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Color Name": "MILITARY GREEN", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Color Name": "NAVY", "Image Suffix": "Navy", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS"},
            {"Color Name": "SPORT GREY", "Image Suffix": "SportGrey", "SKUWA Letter": "H", "Base SKU Shift": "", "Base SKU": "UNGS"},
        ]"""
content = content.replace(old_defaults, new_defaults)

# 2. apply_sku_shift
old_shift = """def apply_sku_shift(sku_prefix, shift):
    if shift:
        if "UNGT1" in sku_prefix or "UGNT1" in sku_prefix:
            return sku_prefix.replace("UNGT1", f"UNGT{shift}").replace("UGNT1", f"UGNT{shift}")
        elif "WUNGT1" in sku_prefix:
            return sku_prefix.replace("WUNGT1", f"WUNGT{shift}")
    return sku_prefix"""
new_shift = """def apply_sku_shift(sku_prefix, shift, base_sku=""):
    if not shift:
        return sku_prefix
        
    if base_sku and base_sku in sku_prefix:
        import re
        base_alpha = re.sub(r'\d+$', '', base_sku)
        return sku_prefix.replace(base_sku, f"{base_alpha}{shift}")

    if "UNGT1" in sku_prefix or "UGNT1" in sku_prefix:
        return sku_prefix.replace("UNGT1", f"UNGT{shift}").replace("UGNT1", f"UGNT{shift}")
    elif "WUNGT1" in sku_prefix:
        return sku_prefix.replace("WUNGT1", f"WUNGT{shift}")
    return sku_prefix"""
content = content.replace(old_shift, new_shift)

# 3. get_sku_by_color
old_get_sku_color = """def get_sku_by_color(sku_prefix, color, product_type, profile_manager):
    rule = profile_manager.get_color_rule(product_type, color)
    return apply_sku_shift(sku_prefix, rule["Base SKU Shift"])"""
new_get_sku_color = """def get_sku_by_color(sku_prefix, color, product_type, profile_manager):
    rule = profile_manager.get_color_rule(product_type, color)
    return apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))"""
content = content.replace(old_get_sku_color, new_get_sku_color)

# 4. get_sku_by_image_code
old_get_sku_image_code = """def get_sku_by_image_code(sku_prefix, image_code, product_type, profile_manager):
    code = clean_text(image_code)
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        if rule["Image Suffix"]:
            suffix = f"-{rule['Image Suffix']}"
            if code.upper().endswith(suffix.upper()):
                return apply_sku_shift(sku_prefix, rule["Base SKU Shift"])
    return sku_prefix"""
new_get_sku_image_code = """def get_sku_by_image_code(sku_prefix, image_code, product_type, profile_manager):
    code = clean_text(image_code)
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        if rule["Image Suffix"]:
            suffix = f"-{rule['Image Suffix']}"
            if code.upper().endswith(suffix.upper()):
                return apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))
    return sku_prefix"""
content = content.replace(old_get_sku_image_code, new_get_sku_image_code)

# 5. get_sku_variants_for_common_asset
old_variants = """def get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):
    variants = [sku_prefix]
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        shifted = apply_sku_shift(sku_prefix, rule["Base SKU Shift"])
        if shifted not in variants:
            variants.append(shifted)
    return variants"""
new_variants = """def get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):
    variants = [sku_prefix]
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        shifted = apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))
        if shifted not in variants:
            variants.append(shifted)
    return variants"""
content = content.replace(old_variants, new_variants)

# 6. looks_like_full_skuwa
old_looks_like = """def looks_like_full_skuwa(value):
    text = clean_text(value).upper()
    return "UGNT" in text or "UNGT" in text"""
new_looks_like = """def looks_like_full_skuwa(value, product_type, profile_manager):
    text = clean_text(value).upper()
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        base_sku = rule.get("Base SKU", "").upper()
        if base_sku:
            import re
            base_alpha = re.sub(r'\d+$', '', base_sku)
            if base_alpha and base_alpha in text:
                return True
    return "UGNT" in text or "UNGT" in text"""
content = content.replace(old_looks_like, new_looks_like)

# 7. is_already_full_image_code
old_already_full = """def is_already_full_image_code(value):
    text = clean_text(value).upper()
    return ("UNGT" in text or "UGNT" in text) and ("MK" in text or "IN" in text or "SW" in text)"""
new_already_full = """def is_already_full_image_code(value, product_type, profile_manager):
    text = clean_text(value).upper()
    has_sku = False
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        base_sku = rule.get("Base SKU", "").upper()
        if base_sku:
            import re
            base_alpha = re.sub(r'\d+$', '', base_sku)
            if base_alpha and base_alpha in text:
                has_sku = True
                break
                
    if not has_sku:
        has_sku = "UNGT" in text or "UGNT" in text
        
    return has_sku and ("MK" in text or "IN" in text or "SW" in text)"""
content = content.replace(old_already_full, new_already_full)

# 8. Callers
old_build_full = """    if is_already_full_image_code(code):"""
new_build_full = """    if is_already_full_image_code(code, product_type, profile_manager):"""
content = content.replace(old_build_full, new_build_full)

old_rename_call = """        if is_already_full_image_code(filename_without_ext):"""
new_rename_call = """        if is_already_full_image_code(filename_without_ext, product_type, profile_manager):"""
content = content.replace(old_rename_call, new_rename_call)

old_build_skuwa = """        if looks_like_full_skuwa(skuwa_value):"""
new_build_skuwa = """        if looks_like_full_skuwa(skuwa_value, product_type, profile_manager):"""
content = content.replace(old_build_skuwa, new_build_skuwa)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("upload_toni.py updated.")
