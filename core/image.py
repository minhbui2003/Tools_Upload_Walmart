"""
Image operations: rename, find, upload to Cloudinary.
"""
import os
import csv
import shutil
from datetime import datetime

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from core.config import IMAGE_EXTENSIONS
from core.utils import clean_text
from core.sku import (
    is_already_full_image_code,
    build_base_mockup_code,
    get_sku_variants_for_common_asset,
    get_sku_by_image_code,
)


def load_cloudinary_config(env_path):
    load_dotenv(env_path)

    cloud_name = os.getenv("CLOUD_NAME")
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        raise ValueError("Missing Cloudinary config. Please check .env file.")

    if cloud_name == "your_cloud_name" or api_key == "your_api_key" or api_secret == "your_api_secret":
        raise ValueError("Please replace placeholder values in .env with real Cloudinary keys.")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


def get_unique_output_path(output_folder, new_filename):
    output_path = os.path.join(output_folder, new_filename)

    if not os.path.exists(output_path):
        return output_path

    name, ext = os.path.splitext(new_filename)
    counter = 1

    while True:
        candidate = os.path.join(output_folder, f"{name}_copy{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def rename_images(input_folder, output_folder, sku_prefix, product_type, profile_manager, log_callback=None):
    if not os.path.isdir(input_folder):
        raise ValueError("Input image folder does not exist.")

    os.makedirs(output_folder, exist_ok=True)

    logs = []
    renamed_count = 0
    skipped_count = 0

    for file in os.listdir(input_folder):
        source_path = os.path.join(input_folder, file)

        if not os.path.isfile(source_path):
            continue

        filename_without_ext, ext = os.path.splitext(file)

        if ext.lower() not in IMAGE_EXTENSIONS:
            continue

        if is_already_full_image_code(filename_without_ext, product_type, profile_manager):
            new_filename = f"{filename_without_ext}{ext.lower()}"
            output_path = get_unique_output_path(output_folder, new_filename)
            shutil.copy2(source_path, output_path)

            logs.append({
                "Old File": file,
                "New File": os.path.basename(output_path),
                "Status": "Copied",
                "Note": "Already full image code",
            })

            renamed_count += 1

            if log_callback:
                log_callback(f"{file} → {os.path.basename(output_path)}")

            continue

        mockup_code = build_base_mockup_code(filename_without_ext, product_type, profile_manager)

        if not mockup_code:
            stem = clean_text(filename_without_ext)

            if stem == "":
                skipped_count += 1
                logs.append({
                    "Old File": file,
                    "New File": "",
                    "Status": "Skipped",
                    "Note": "Empty file name",
                })
                continue

            for sku_variant in get_sku_variants_for_common_asset(sku_prefix, product_type, profile_manager):
                image_code = f"{sku_variant}{stem}"
                new_filename = f"{image_code}{ext.lower()}"
                output_path = get_unique_output_path(output_folder, new_filename)
                shutil.copy2(source_path, output_path)

                logs.append({
                    "Old File": file,
                    "New File": os.path.basename(output_path),
                    "Status": "Renamed",
                    "Note": "Common asset copied for SKU variant",
                })

                renamed_count += 1

                if log_callback:
                    log_callback(f"{file} → {os.path.basename(output_path)}")

            continue

        adjusted_sku = get_sku_by_image_code(sku_prefix, mockup_code, product_type, profile_manager)
        image_code = f"{adjusted_sku}{mockup_code}"
        new_filename = f"{image_code}{ext.lower()}"
        output_path = get_unique_output_path(output_folder, new_filename)

        shutil.copy2(source_path, output_path)

        logs.append({
            "Old File": file,
            "New File": os.path.basename(output_path),
            "Status": "Renamed",
            "Note": "OK",
        })

        renamed_count += 1

        if log_callback:
            log_callback(f"{file} → {os.path.basename(output_path)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rename_log_csv = os.path.join(output_folder, f"rename_log_{timestamp}.csv")

    with open(rename_log_csv, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["Old File", "New File", "Status", "Note"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in logs:
            writer.writerow(item)

    return renamed_count, skipped_count, rename_log_csv


def find_image_file(image_folder, image_code):
    if not image_code:
        return None

    code_clean = clean_text(image_code)

    # Try exact match first
    for ext in IMAGE_EXTENSIONS:
        file_path = os.path.join(image_folder, code_clean + ext)
        if os.path.exists(file_path):
            return file_path

    # Fallback to fuzzy match (ignore case, spaces, dashes, underscores)
    target_norm = code_clean.lower().replace(" ", "").replace("-", "").replace("_", "")
    try:
        for f in os.listdir(image_folder):
            name, ext = os.path.splitext(f)
            if ext.lower() in [e.lower() for e in IMAGE_EXTENSIONS]:
                f_norm = name.lower().replace(" ", "").replace("-", "").replace("_", "")
                if f_norm == target_norm:
                    return os.path.join(image_folder, f)
    except Exception:
        pass

    return None


def upload_image(image_path, cloud_folder):
    file_name = os.path.splitext(os.path.basename(image_path))[0]

    result = cloudinary.uploader.upload(
        image_path,
        folder=cloud_folder,
        public_id=file_name,
        overwrite=True,
        resource_type="image",
    )

    return result.get("secure_url")
