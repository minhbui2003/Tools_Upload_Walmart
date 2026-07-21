"""
Constants and path helpers for the TikTok upload tool.
"""
import os
import sys


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]

SUPPORTED_SOURCE_TYPES = ["auto", "getlinks", "update_file", "fixed", "blank", "skip"]

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
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return get_project_root()


def get_resource_path(*parts):
    return os.path.join(get_resource_root(), *parts)


def find_env_path():
    """Find the Cloudinary .env file from Tools_Tiktok or the parent app root."""
    project_root = get_project_root()
    resource_root = get_resource_root()
    candidates = [
        os.path.join(project_root, ".env"),
        os.path.join(os.path.dirname(project_root), ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.getcwd()), ".env"),
        os.path.join(resource_root, ".env"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return candidates[0]


def ensure_env_file():
    env_path = find_env_path()
    if os.path.exists(env_path):
        return env_path

    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w", encoding="utf-8") as file:
        file.write(
            "CLOUD_NAME=your_cloud_name\n"
            "API_KEY=your_api_key\n"
            "API_SECRET=your_api_secret\n"
        )
    return env_path
