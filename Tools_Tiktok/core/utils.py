"""
Utility functions: clean_text, normalize_columns, is_enabled.
"""
from datetime import datetime, date

import pandas as pd

from core.config import COLUMN_ALIASES


def clean_text(value):
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    return str(value).strip()


def is_enabled(value):
    text = clean_text(value).upper()
    return text in ["Y", "YES", "TRUE", "1", "ENABLE", "ENABLED"]


def normalize_columns(df):
    rename_map = {}

    for standard_name, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if str(col).strip() in aliases:
                rename_map[col] = standard_name
                break

    return df.rename(columns=rename_map)
