"""
Constants and configuration for Upload Toni tool.
"""
import os
import sys


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]

SUPPORTED_SOURCE_TYPES = ["getlinks", "update_file", "fixed", "blank", "skip"]

COLUMN_ALIASES = {
    "SKU": ["SKU", "Sku", "sku"],
    "PREFIX": ["PREFIX", "Prefix", "prefix"],
    "COLOR": ["COLOR", "Color", "color"],
    "SIZE": ["SIZE", "Size", "size"],
    "SKUWA": ["SKUWA", "Skuwa", "skuwa"],

    "Main": ["Main"],
    "Main_URL": ["Main_URL", "Main Image_URL", "Main Image URL", "Main URL"],

    "Add1": ["Add1", "Add 1"],
    "Add1_URL": ["Add1_URL", "Add1 URL (+)", "Add 1 URL (+)", "Additional Image URL (+)"],

    "Add2": ["Add2", "Add 2"],
    "Add2_URL": ["Add2_URL", "Add2 URL (+)", "Add 2 URL (+)"],

    "Add3": ["Add3", "Add 3"],
    "Add3_URL": ["Add3_URL", "Add3 URL (+)", "Add 3 URL (+)"],

    "Add4": ["Add4", "Add 4"],
    "Add4_URL": ["Add4_URL", "Add4 URL (+)", "Add 4 URL (+)"],

    "Add5": ["Add5", "Add 5"],
    "Add5_URL": ["Add5_URL", "Add5 URL (+)", "Add 5 URL (+)"],

    "Swatch": ["Swatch", "SWATCH", "swatch"],
    "Swatch_URL": ["Swatch_URL", "Swatch URL", "SWATCH URL", "swatch URL"],
}

IMAGE_PAIRS = [
    ("Main", "Main_URL"),
    ("Add1", "Add1_URL"),
    ("Add2", "Add2_URL"),
    ("Add3", "Add3_URL"),
    ("Add4", "Add4_URL"),
    ("Add5", "Add5_URL"),
    ("Swatch", "Swatch_URL"),
]


def get_project_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # When running as a module, go up one level from core/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
