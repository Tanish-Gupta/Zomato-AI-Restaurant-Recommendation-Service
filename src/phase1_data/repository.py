"""Restaurant data repository with filtering capabilities."""

import logging
from typing import Optional, List

import pandas as pd

from .loader import DatasetLoader
from .preprocessor import DataPreprocessor

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """
    Repository for accessing and filtering restaurant data.
    
    Provides a clean interface for querying restaurants based on
    various criteria like cuisine, location, price, and rating.
    """

    def __init__(
        self,
        loader: Optional[DatasetLoader] = None,
        preprocessor: Optional[DataPreprocessor] = None,
    ):
        self.loader = loader or DatasetLoader()
        self.preprocessor = preprocessor or DataPreprocessor()
        self._data: Optional[pd.DataFrame] = None
        self._column_mapping: dict = {}

    def initialize(self, force_reload: bool = False) -> None:
        """
        Load and preprocess the dataset.

        Args:
            force_reload: If True, bypass cache and reload from source.
        """
        logger.info("Initializing restaurant repository")
        raw_data = self.loader.load(force_reload=force_reload)
        self._data = self.preprocessor.preprocess(raw_data)
        self._detect_columns()
        logger.info(f"Repository initialized with {len(self._data)} restaurants")

    def _detect_columns(self) -> None:
        """Detect and map relevant columns from the dataset."""
        if self._data is None:
            return

        columns = self._data.columns.tolist()

        self._column_mapping = {
            "name": self._find_column(columns, ["name", "restaurant_name", "rest_name"]),
            "cuisine": self._find_column(columns, ["cuisine", "cuisines", "cuisine_type"]),
            "location": self._find_column(columns, ["location", "city", "area", "locality"]),
            "rating": self._find_column(columns, ["rating", "rate", "aggregate_rating", "avg_rating"]),
            "price": self._find_column(columns, ["price_range", "price", "cost", "average_cost"]),
            "votes": self._find_column(columns, ["votes", "num_votes", "vote_count"]),
        }

        logger.info(f"Detected column mapping: {self._column_mapping}")

    def _find_column(self, columns: List[str], candidates: List[str]) -> Optional[str]:
        """Find a matching column from a list of candidates."""
        for candidate in candidates:
            for col in columns:
                if candidate in col.lower():
                    return col
        return None

    @property
    def data(self) -> pd.DataFrame:
        """Get the full dataset."""
        if self._data is None:
            self.initialize()
        return self._data

    @property
    def columns(self) -> List[str]:
        """Get list of available columns."""
        return self.data.columns.tolist()

    def get_all(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get all restaurants, optionally limited.

        Args:
            limit: Maximum number of results to return.

        Returns:
            DataFrame with restaurant data.
        """
        df = self.data
        if limit:
            df = df.head(limit)
        return df

    def filter(
        self,
        cuisine: Optional[str] = None,
        location: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        price_range: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Filter restaurants based on criteria.

        Args:
            cuisine: Filter by cuisine type (partial match).
            location: Filter by location (partial match).
            min_rating: Minimum rating threshold.
            max_rating: Maximum rating threshold.
            price_range: Filter by price range category.
            limit: Maximum number of results.

        Returns:
            Filtered DataFrame of restaurants.
        """
        df = self.data.copy()

        if cuisine and self._column_mapping.get("cuisine"):
            col = self._column_mapping["cuisine"]
            df = df[df[col].str.lower().str.contains(cuisine.lower(), na=False)]

        if location and self._column_mapping.get("location"):
            col = self._column_mapping["location"]
            df = df[df[col].str.lower().str.contains(location.lower(), na=False)]

        if min_rating is not None and self._column_mapping.get("rating"):
            col = self._column_mapping["rating"]
            rating_series = pd.to_numeric(df[col], errors="coerce")
            # Include rows with missing/NaN rating so "min 0" doesn't drop unrated restaurants
            df = df[(rating_series.isna()) | (rating_series >= min_rating)]

        if max_rating is not None and self._column_mapping.get("rating"):
            col = self._column_mapping["rating"]
            rating_series = pd.to_numeric(df[col], errors="coerce")
            df = df[(rating_series.isna()) | (rating_series <= max_rating)]

        if price_range and self._column_mapping.get("price"):
            col = self._column_mapping["price"]
            price_category_col = f"{col}_category"
            if price_category_col in df.columns:
                df = df[df[price_category_col].str.lower() == price_range.lower()]
            else:
                df = df[df[col].astype(str).str.lower().str.contains(price_range.lower(), na=False)]

        if limit:
            df = df.head(limit)

        return df

    def get_unique_cuisines(self) -> List[str]:
        """Get list of unique cuisines in the dataset."""
        if not self._column_mapping.get("cuisine"):
            return []

        col = self._column_mapping["cuisine"]
        cuisines = set()

        for value in self.data[col].dropna().unique():
            for cuisine in str(value).split(","):
                cuisine = cuisine.strip()
                if cuisine and cuisine != "Unknown":
                    cuisines.add(cuisine)

        return sorted(cuisines)

    def get_unique_locations(self) -> List[str]:
        """Get list of unique locations in the dataset."""
        if not self._column_mapping.get("location"):
            return []

        col = self._column_mapping["location"]
        locations = self.data[col].dropna().unique()
        return sorted([loc for loc in locations if loc and loc != "Unknown"])

    def get_rating_range(self) -> tuple:
        """Get the min and max rating values."""
        if not self._column_mapping.get("rating"):
            return (0.0, 5.0)

        col = self._column_mapping["rating"]
        ratings = pd.to_numeric(self.data[col], errors="coerce").dropna()
        
        if len(ratings) == 0:
            return (0.0, 5.0)
            
        return (float(ratings.min()), float(ratings.max()))

    def get_statistics(self) -> dict:
        """Get basic statistics about the dataset."""
        return {
            "total_restaurants": len(self.data),
            "unique_cuisines": len(self.get_unique_cuisines()),
            "unique_locations": len(self.get_unique_locations()),
            "rating_range": self.get_rating_range(),
            "columns": self.columns,
            "column_mapping": self._column_mapping,
        }

    def search(self, query: str, limit: Optional[int] = 10) -> pd.DataFrame:
        """
        Search restaurants by name or any text field.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            DataFrame of matching restaurants.
        """
        df = self.data

        text_cols = df.select_dtypes(include=["object"]).columns
        mask = pd.Series([False] * len(df))

        for col in text_cols:
            mask |= df[col].str.lower().str.contains(query.lower(), na=False)

        result = df[mask]

        if limit:
            result = result.head(limit)

        return result
