"""
Image discovery and Cloudinary upload helpers for TikTok.
"""
import os
import re
from pathlib import Path

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from core.config import IMAGE_EXTENSIONS


def normalize_asset_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def load_cloudinary_config(env_path):
    load_dotenv(env_path)

    cloud_name = os.getenv("CLOUD_NAME")
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        raise ValueError(f"Missing Cloudinary config. Please check .env file: {env_path}")

    if cloud_name == "your_cloud_name" or api_key == "your_api_key" or api_secret == "your_api_secret":
        raise ValueError("Please replace placeholder Cloudinary values in .env.")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


class ImageResolver:
    def __init__(
        self,
        image_folder,
        cloud_folder,
        env_path,
        upload_enabled=True,
        log_callback=None,
    ):
        self.image_folder = image_folder
        self.cloud_folder = cloud_folder
        self.upload_enabled = upload_enabled
        self.log_callback = log_callback
        self._by_norm = {}
        self._all_images = []
        self._url_cache = {}

        if not os.path.isdir(image_folder):
            raise ValueError(f"Image folder does not exist: {image_folder}")

        self._scan()

        if upload_enabled:
            load_cloudinary_config(env_path)

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def _scan(self):
        valid_exts = {ext.lower() for ext in IMAGE_EXTENSIONS}
        for root, _, files in os.walk(self.image_folder):
            for filename in sorted(files):
                path = os.path.join(root, filename)
                stem, ext = os.path.splitext(filename)
                if ext.lower() not in valid_exts:
                    continue

                norm = normalize_asset_key(stem)
                self._by_norm.setdefault(norm, []).append(path)
                self._all_images.append(path)

        self._all_images.sort(key=lambda item: normalize_asset_key(Path(item).stem))

    @property
    def image_count(self):
        return len(self._all_images)

    def find_image(self, candidates, loose_tokens=None):
        normalized_candidates = [
            normalize_asset_key(candidate)
            for candidate in candidates
            if normalize_asset_key(candidate)
        ]

        for norm in normalized_candidates:
            paths = self._by_norm.get(norm)
            if paths:
                return paths[0]

        for norm in normalized_candidates:
            if len(norm) < 3:
                continue
            for path in self._all_images:
                stem_norm = normalize_asset_key(Path(path).stem)
                if norm in stem_norm:
                    return path

        token_norms = [
            normalize_asset_key(token)
            for token in (loose_tokens or [])
            if normalize_asset_key(token)
        ]

        if token_norms:
            for path in self._all_images:
                stem_norm = normalize_asset_key(Path(path).stem)
                if all(token in stem_norm for token in token_norms):
                    return path

        return None

    def get_url(self, candidates, label="", loose_tokens=None, required=False):
        image_path = self.find_image(candidates, loose_tokens=loose_tokens)

        if not image_path:
            if required:
                self._log(f"Missing required image: {label or candidates}")
            return ""

        if image_path in self._url_cache:
            return self._url_cache[image_path]

        if not self.upload_enabled:
            url = Path(image_path).resolve().as_uri()
            self._url_cache[image_path] = url
            return url

        file_stem = Path(image_path).stem
        self._log(f"Uploading: {Path(image_path).name}")
        result = cloudinary.uploader.upload(
            image_path,
            folder=self.cloud_folder,
            public_id=file_stem,
            overwrite=True,
            resource_type="image",
        )
        url = result.get("secure_url") or ""
        self._url_cache[image_path] = url
        self._log(f"Uploaded: {Path(image_path).name}")
        return url
