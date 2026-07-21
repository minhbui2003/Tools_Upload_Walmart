"""
SKU and SKUWA logic: shifting, building, validation.
"""
import re

from core.profile import _color_key_aliases
from core.utils import clean_text


def _split_base_sku(base_sku):
    text = clean_text(base_sku)
    match = re.match(r"^(.*?)(\d+)$", text)
    if match:
        return match.group(1), match.group(2)
    return text, ""


def apply_sku_shift(sku_prefix, shift, base_sku=""):
    sku_prefix = clean_text(sku_prefix)
    shift = clean_text(shift)
    base_sku = clean_text(base_sku)

    if base_sku:
        base_alpha, default_shift = _split_base_sku(base_sku)
        target_shift = shift or default_shift
        target_base = f"{base_alpha}{target_shift}" if base_alpha else base_sku

        if base_sku in sku_prefix:
            return sku_prefix.replace(base_sku, target_base, 1)

        if base_alpha and base_alpha in sku_prefix:
            return re.sub(rf"{re.escape(base_alpha)}\d*", target_base, sku_prefix, count=1)

        if sku_prefix.upper().endswith("W") and target_base.upper().startswith("W"):
            return f"{sku_prefix[:-1]}{target_base}"

        return f"{sku_prefix}{target_base}"

    if not shift:
        return sku_prefix

    for base_alpha in ["WUNGT", "UNGT", "UGNT", "UNGS", "UNGH", "UNGL"]:
        if re.search(rf"{base_alpha}\d+", sku_prefix):
            return re.sub(rf"{base_alpha}\d+", f"{base_alpha}{shift}", sku_prefix, count=1)

    return sku_prefix


def get_sku_by_color(sku_prefix, color, product_type, profile_manager):
    rule = profile_manager.get_color_rule(product_type, color)
    return apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))


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


def looks_like_full_skuwa(value, product_type, profile_manager):
    text = clean_text(value).upper()
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        base_sku = rule.get("Base SKU", "").upper()
        if base_sku:
            base_alpha = re.sub(r'\d+$', '', base_sku)
            if base_alpha and base_alpha in text:
                return True
    return any(token in text for token in ["UGNT", "UNGT", "WUNGT", "UNGS", "UNGH", "UNGL"])


def get_sku_by_image_code(sku_prefix, image_code, product_type, profile_manager):
    code = clean_text(image_code)
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        if rule["Image Suffix"]:
            suffix = f"-{rule['Image Suffix']}"
            if code.upper().endswith(suffix.upper()):
                return apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))
    return sku_prefix


def get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):
    variants = [sku_prefix]
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        shifted = apply_sku_shift(sku_prefix, rule["Base SKU Shift"], rule.get("Base SKU", ""))
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
    image_suffix = clean_text(rule.get("Image Suffix", ""))
    color_tokens = [rule.get("Color Name", "")]
    if image_suffix and not image_suffix.isdigit():
        color_tokens.append(image_suffix)
    color_tokens.extend(_color_key_aliases(rule.get("Color Name", "")))

    for token in sorted(set(clean_text(item) for item in color_tokens if clean_text(item)), key=len, reverse=True):
        spaced_token = re.escape(token)
        compact_token = re.escape(token.replace(" ", ""))
        base_name = re.sub(spaced_token, "", base_name, flags=re.IGNORECASE)
        base_name = re.sub(compact_token, "", base_name, flags=re.IGNORECASE)

    base_name = base_name.strip()
    base_name = base_name.rstrip("-_ ")
    base_name = base_name.strip()

    if not base_name or not rule["Image Suffix"]:
        return None

    return f"{base_name}-{rule['Image Suffix']}"


def is_already_full_image_code(value, product_type, profile_manager):
    text = clean_text(value).upper()
    has_sku = False
    rules = profile_manager.get_rules_for_type(product_type)
    for rule in rules:
        base_sku = rule.get("Base SKU", "").upper()
        if base_sku:
            base_alpha = re.sub(r'\d+$', '', base_sku)
            if base_alpha and base_alpha in text:
                has_sku = True
                break

    if not has_sku:
        has_sku = any(token in text for token in ["UNGT", "UGNT", "WUNGT", "UNGS", "UNGH", "UNGL"])

    return has_sku and ("MK" in text or "IN" in text or "SW" in text)


def build_full_image_code(sku_prefix, short_code, color, product_type, profile_manager):
    code = clean_text(short_code)
    if code == "":
        return ""
    if is_already_full_image_code(code, product_type, profile_manager):
        return code
    adjusted_sku = get_sku_by_color(sku_prefix, color, product_type, profile_manager)
    return f"{adjusted_sku}{code}"


def get_base_prefix_for_row(row, fallback_prefix):
    row_sku = clean_text(row.get("SKU"))
    row_prefix = clean_text(row.get("PREFIX"))

    if row_sku:
        return row_sku

    if row_prefix:
        return row_prefix

    return fallback_prefix


def build_full_skuwa_from_row(row, fallback_prefix, product_type, profile_manager):
    color = row.get("COLOR")
    size = row.get("SIZE")
    skuwa_value = clean_text(row.get("SKUWA"))

    base_prefix = get_base_prefix_for_row(row, fallback_prefix)
    adjusted_sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)
    suffix = build_skuwa_suffix(color, size, product_type, profile_manager)

    if skuwa_value:
        if looks_like_full_skuwa(skuwa_value, product_type, profile_manager):
            return skuwa_value

        size_code = size_to_skuwa_code(size)
        if suffix and size_code and skuwa_value.upper().endswith(size_code.upper()):
            skuwa_value = suffix

        return f"{adjusted_sku}{skuwa_value}"

    if suffix:
        return f"{adjusted_sku}{suffix}"

    return adjusted_sku
