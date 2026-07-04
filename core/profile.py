"""
ProductProfileManager: loads color/SKU rules from Excel or defaults.
"""
import os

import pandas as pd

from core.utils import clean_text


def _normalize_color_key(value):
    return "".join(ch for ch in clean_text(value).upper() if ch.isalnum())


def _color_key_aliases(value):
    color_key = _normalize_color_key(value)
    aliases = [color_key]
    alias_map = {
        "GREY": ["SPORTGREY"],
        "SPORTGREY": ["GREY"],
        "GREEN": ["MILITARYGREEN"],
        "MILITARYGREEN": ["GREEN"],
        "ANTIQUECHERRYRED": ["ANTIQUECHERRY"],
        "ANTIQUECHERRY": ["ANTIQUECHERRYRED"],
    }
    aliases.extend(alias_map.get(color_key, []))
    return aliases


class ProductProfileManager:
    def __init__(self, mapping_path=None):
        self.profiles = {}
        self.load_profiles(mapping_path)

    def load_profiles(self, mapping_path):
        if not mapping_path or not os.path.exists(mapping_path):
            self._load_defaults()
            return

        try:
            df = pd.read_excel(mapping_path, sheet_name="Product Profiles", dtype=str).fillna("")
            for _, row in df.iterrows():
                ptype = clean_text(row.get("Product Type")).upper()
                if not ptype:
                    continue

                rule = {
                    "Color Name": clean_text(row.get("Color Name")).upper(),
                    "Image Suffix": clean_text(row.get("Image Suffix")),
                    "SKUWA Letter": clean_text(row.get("SKUWA Letter")),
                    "Base SKU Shift": clean_text(row.get("Base SKU Shift")),
                    "Base SKU": clean_text(row.get("Base SKU")),
                }

                if ptype not in self.profiles:
                    self.profiles[ptype] = []
                self.profiles[ptype].append(rule)

            if not self.profiles:
                self._load_defaults()
            else:
                self._apply_known_profile_defaults()
        except Exception:
            self._load_defaults()

    def _apply_known_profile_defaults(self):
        tsh_defaults = {
            "BLACK": {"SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            "NAVY": {"SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            "GREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            "SPORTGREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            "GREEN": {"SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGT1"},
            "MILITARYGREEN": {"SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGT1"},
        }
        for rule in self.profiles.get("TSH", []):
            defaults = tsh_defaults.get(_normalize_color_key(rule.get("Color Name")))
            if defaults:
                rule.update(defaults)

        tsh_w_defaults = {
            "BLACK": {"SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            "GREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            "SPORTGREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            "SAND": {"SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            "WHITE": {"SKUWA Letter": "W", "Base SKU Shift": "", "Base SKU": "UNGT1"},
        }
        for rule in self.profiles.get("TSH_W", []):
            defaults = tsh_w_defaults.get(_normalize_color_key(rule.get("Color Name")))
            if defaults:
                rule.update(defaults)

        swe_defaults = {
            "BLACK": {"SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            "NAVY": {"SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            "SPORTGREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
            "ANTIQUECHERRYRED": {"SKUWA Letter": "S", "Base SKU Shift": "7", "Base SKU": "UNGS1"},
            "MILITARYGREEN": {"SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGS1"},
        }
        for rule in self.profiles.get("SWE", []):
            defaults = swe_defaults.get(_normalize_color_key(rule.get("Color Name")))
            if defaults:
                rule.update(defaults)

        swe_w_defaults = {
            "BLACK": {"SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            "NAVY": {"SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            "SPORTGREY": {"SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
            "ANTIQUECHERRYRED": {"SKUWA Letter": "S", "Base SKU Shift": "7", "Base SKU": "UNGS1"},
            "SAND": {"SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
        }
        for rule in self.profiles.get("SWE_W", []):
            defaults = swe_w_defaults.get(_normalize_color_key(rule.get("Color Name")))
            if defaults:
                rule.update(defaults)

    def _load_defaults(self):
        self.profiles["TSH"] = [
            {"Color Name": "BLACK", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            {"Color Name": "NAVY", "Image Suffix": "2", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            {"Color Name": "GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            {"Color Name": "GREEN", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGT1"},
            {"Color Name": "MILITARY GREEN", "Image Suffix": "4", "SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGT1"},
        ]

        self.profiles["TSH_W"] = [
            {"Color Name": "BLACK", "Image Suffix": "1", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGT1"},
            {"Color Name": "SAND", "Image Suffix": "2", "SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "3", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGT1"},
            {"Color Name": "WHITE", "Image Suffix": "4", "SKUWA Letter": "W", "Base SKU Shift": "", "Base SKU": "UNGT1"},
        ]

        self.profiles["SWE"] = [
            {"Color Name": "BLACK", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            {"Color Name": "NAVY", "Image Suffix": "Navy", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "SportGrey", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
            {"Color Name": "ANTIQUE CHERRY RED", "Image Suffix": "AntiqueCherryRed", "SKUWA Letter": "S", "Base SKU Shift": "7", "Base SKU": "UNGS1"},
            {"Color Name": "MILITARY GREEN", "Image Suffix": "MilitaryGreen", "SKUWA Letter": "F", "Base SKU Shift": "3", "Base SKU": "UNGS1"},
        ]

        self.profiles["SWE_W"] = [
            {"Color Name": "BLACK", "Image Suffix": "Black", "SKUWA Letter": "B", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            {"Color Name": "NAVY", "Image Suffix": "Navy", "SKUWA Letter": "N", "Base SKU Shift": "", "Base SKU": "UNGS1"},
            {"Color Name": "SPORT GREY", "Image Suffix": "SportGrey", "SKUWA Letter": "H", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
            {"Color Name": "ANTIQUE CHERRY RED", "Image Suffix": "AntiqueCherryRed", "SKUWA Letter": "S", "Base SKU Shift": "7", "Base SKU": "UNGS1"},
            {"Color Name": "SAND", "Image Suffix": "Sand", "SKUWA Letter": "Y", "Base SKU Shift": "4", "Base SKU": "UNGS1"},
        ]

    def get_rules_for_type(self, product_type):
        ptype = clean_text(product_type).upper()
        if not ptype:
            ptype = "TSH"
        return self.profiles.get(ptype, self.profiles.get("TSH", []))

    def get_base_sku(self, product_type):
        rules = self.get_rules_for_type(product_type)
        if rules and "Base SKU" in rules[0]:
            return rules[0]["Base SKU"]
        return ""

    def get_color_rule(self, product_type, color_name):
        rules = self.get_rules_for_type(product_type)
        color_upper = clean_text(color_name).upper()
        color_keys = _color_key_aliases(color_name)

        for rule in rules:
            if _normalize_color_key(rule["Color Name"]) in color_keys:
                return rule

        suffix = clean_text(color_name).replace(" ", "")
        fallback_base_sku = "UNGT1"
        if rules:
            fallback_base_sku = clean_text(rules[0].get("Base SKU")) or fallback_base_sku
        return {"Color Name": color_upper, "Image Suffix": suffix, "SKUWA Letter": "", "Base SKU Shift": "", "Base SKU": fallback_base_sku}

    def detect_color_rule_from_filename(self, product_type, filename_without_ext):
        normalized = _normalize_color_key(filename_without_ext)
        rules = self.get_rules_for_type(product_type)

        for rule in sorted(rules, key=lambda x: len(x["Color Name"]), reverse=True):
            if any(color_key in normalized for color_key in _color_key_aliases(rule["Color Name"])):
                return rule
        return None
