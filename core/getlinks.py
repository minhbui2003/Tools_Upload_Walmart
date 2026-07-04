"""
Getlinks template processing: fill SKU/SKUWA, upload images, generate CSV output.
"""
import os
import csv
from datetime import datetime

import pandas as pd

from core.config import IMAGE_PAIRS
from core.utils import clean_text, normalize_columns
from core.image import load_cloudinary_config, find_image_file, upload_image
from core.sku import (
    get_sku_by_color,
    build_full_skuwa_from_row,
    get_base_prefix_for_row,
    build_full_image_code,
)


def process_getlinks_template(
    template_path,
    image_folder,
    output_folder,
    env_path,
    sku_prefix,
    cloud_folder,
    product_type,
    profile_manager,
    log_callback=None,
):
    load_cloudinary_config(env_path)

    df = pd.read_excel(template_path, dtype=object, keep_default_na=False).fillna("")
    df = normalize_columns(df)

    if "COLOR" not in df.columns:
        raise ValueError("Getlinks template missing COLOR column.")

    if "SIZE" not in df.columns:
        raise ValueError("Getlinks template missing SIZE column.")

    if "SKU" not in df.columns:
        df["SKU"] = ""

    if "SKUWA" not in df.columns:
        df["SKUWA"] = ""

    df["SKU"] = df["SKU"].astype("object")
    df["SKUWA"] = df["SKUWA"].astype("object")

    for index, row in df.iterrows():
        color = row.get("COLOR")
        base_prefix = get_base_prefix_for_row(row, sku_prefix)
        sku = get_sku_by_color(base_prefix, color, product_type, profile_manager)
        final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)

        df.at[index, "SKU"] = sku
        df.at[index, "SKUWA"] = final_skuwa

    upload_cache = {}
    logs = []

    for source_col, url_col in IMAGE_PAIRS:
        if source_col not in df.columns:
            continue

        if url_col not in df.columns:
            df[url_col] = ""

        df[source_col] = df[source_col].astype("object")
        df[url_col] = df[url_col].astype("object")

        for index, row in df.iterrows():
            short_code = row.get(source_col)

            if clean_text(short_code) == "":
                continue

            color = row.get("COLOR")
            full_image_code = build_full_image_code(sku_prefix, short_code, color, product_type, profile_manager)

            df.at[index, source_col] = full_image_code

            if full_image_code in upload_cache:
                df.at[index, url_col] = upload_cache[full_image_code]

                logs.append({
                    "Template Column": source_col,
                    "URL Column": url_col,
                    "Short Code": clean_text(short_code),
                    "Full Image Code": full_image_code,
                    "File Name": "",
                    "Status": "Reused",
                    "URL": upload_cache[full_image_code],
                    "Note": "Used cached uploaded link",
                })

                continue

            image_path = find_image_file(image_folder, full_image_code)

            if image_path is None:
                logs.append({
                    "Template Column": source_col,
                    "URL Column": url_col,
                    "Short Code": clean_text(short_code),
                    "Full Image Code": full_image_code,
                    "File Name": "",
                    "Status": "Missing",
                    "URL": "",
                    "Note": "Image file not found",
                })

                if log_callback:
                    log_callback(f"Missing: {full_image_code}")

                continue

            try:
                if log_callback:
                    log_callback(f"Uploading: {os.path.basename(image_path)}")

                url = upload_image(image_path, cloud_folder)
                upload_cache[full_image_code] = url
                df.at[index, url_col] = url

                logs.append({
                    "Template Column": source_col,
                    "URL Column": url_col,
                    "Short Code": clean_text(short_code),
                    "Full Image Code": full_image_code,
                    "File Name": os.path.basename(image_path),
                    "Status": "Uploaded",
                    "URL": url,
                    "Note": "OK",
                })

                if log_callback:
                    log_callback(f"Uploaded: {full_image_code}")

            except Exception as e:
                logs.append({
                    "Template Column": source_col,
                    "URL Column": url_col,
                    "Short Code": clean_text(short_code),
                    "Full Image Code": full_image_code,
                    "File Name": os.path.basename(image_path),
                    "Status": "Error",
                    "URL": "",
                    "Note": str(e),
                })

                if log_callback:
                    log_callback(f"Error: {full_image_code} - {str(e)}")

    os.makedirs(output_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    getlinks_csv = os.path.join(output_folder, f"getlinks_output_{timestamp}.csv")
    upload_log_csv = os.path.join(output_folder, f"upload_log_{timestamp}.csv")

    df.to_csv(getlinks_csv, index=False, encoding="utf-8-sig")

    with open(upload_log_csv, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = [
            "Template Column",
            "URL Column",
            "Short Code",
            "Full Image Code",
            "File Name",
            "Status",
            "URL",
            "Note",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in logs:
            writer.writerow(item)

    return df, getlinks_csv, upload_log_csv
