"""Data preprocessing and cleaning utilities."""

import logging
import re
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses and cleans restaurant data."""

    PRICE_MAPPING = {
        1: "low",
        2: "medium",
        3: "high",
        4: "very_high",
    }

    def __init__(self):
        self._processed = False

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all preprocessing steps to the dataset.

        Args:
            df: Raw DataFrame from the dataset loader.

        Returns:
            Cleaned and normalized DataFrame.
        """
        logger.info(f"Preprocessing dataset with {len(df)} records")

        df = df.copy()

        df = self._standardize_columns(df)
        df = self._handle_missing_values(df)
        df = self._clean_text_fields(df)
        df = self._normalize_price_range(df)
        df = self._normalize_rating(df)
        df = self._clean_cuisines(df)
        df = self._clean_location(df)

        self._processed = True
        logger.info(f"Preprocessing complete. {len(df)} records remaining")

        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase with underscores."""
        df.columns = [
            col.lower().strip().replace(" ", "_").replace("-", "_")
            for col in df.columns
        ]
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        text_columns = df.select_dtypes(include=["object"]).columns
        for col in text_columns:
            df[col] = df[col].fillna("Unknown")

        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if "rating" in col.lower():
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(df[col].median())

        return df

    def _clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize text fields."""
        text_columns = df.select_dtypes(include=["object"]).columns

        for col in text_columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(["", "nan", "None", "N/A", "n/a"], "Unknown")

        return df

    def _normalize_price_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize price range to categorical values."""
        price_cols = [col for col in df.columns if "price" in col.lower()]

        for col in price_cols:
            if df[col].dtype in [np.int64, np.float64]:
                df[f"{col}_category"] = df[col].map(
                    lambda x: self.PRICE_MAPPING.get(int(x), "medium")
                    if pd.notna(x) and x > 0
                    else "medium"
                )

        return df

    def _normalize_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize ratings to 0-5 scale."""
        rating_cols = [col for col in df.columns if "rating" in col.lower()]

        for col in rating_cols:
            if df[col].dtype in [np.int64, np.float64]:
                max_rating = df[col].max()
                if max_rating > 5:
                    df[col] = (df[col] / max_rating) * 5
                df[col] = df[col].clip(0, 5).round(2)

        return df

    def _clean_cuisines(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize cuisine field."""
        cuisine_cols = [col for col in df.columns if "cuisine" in col.lower()]

        for col in cuisine_cols:
            df[col] = df[col].apply(self._standardize_cuisine)

        return df

    def _standardize_cuisine(self, value: str) -> str:
        """Standardize a single cuisine value."""
        if not value or value == "Unknown":
            return "Unknown"

        value = re.sub(r"[^\w\s,]", "", str(value))
        cuisines = [c.strip().title() for c in value.split(",")]
        cuisines = [c for c in cuisines if c and c != "Unknown"]

        return ", ".join(sorted(set(cuisines))) if cuisines else "Unknown"

    def _clean_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize location fields."""
        location_cols = [
            col for col in df.columns
            if any(loc in col.lower() for loc in ["location", "city", "area", "address"])
        ]

        for col in location_cols:
            df[col] = df[col].apply(self._standardize_location)

        return df

    def _standardize_location(self, value: str) -> str:
        """Standardize a single location value."""
        if not value or value == "Unknown":
            return "Unknown"

        value = str(value).strip().title()
        value = re.sub(r"\s+", " ", value)

        return value if value else "Unknown"

    @property
    def is_processed(self) -> bool:
        """Check if preprocessing has been applied."""
        return self._processed
