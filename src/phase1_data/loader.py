"""Hugging Face dataset loader with local caching."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from datasets import load_dataset

from src.config import DATA_CACHE_DIR, DATASET_NAME

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads and caches the Zomato restaurant dataset from Hugging Face."""

    def __init__(
        self,
        dataset_name: str = DATASET_NAME,
        cache_dir: Optional[Path] = None,
    ):
        self.dataset_name = dataset_name
        self.cache_dir = cache_dir or DATA_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self.cache_dir / "restaurants.parquet"

    def load(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load the dataset, using cache if available.

        Args:
            force_reload: If True, bypass cache and reload from Hugging Face.

        Returns:
            DataFrame containing the restaurant data.
        """
        if not force_reload and self._cache_file.exists():
            logger.info(f"Loading dataset from cache: {self._cache_file}")
            return pd.read_parquet(self._cache_file)

        logger.info(f"Loading dataset from Hugging Face: {self.dataset_name}")
        dataset = load_dataset(self.dataset_name)

        if "train" in dataset:
            df = dataset["train"].to_pandas()
        else:
            first_split = list(dataset.keys())[0]
            df = dataset[first_split].to_pandas()

        self._save_to_cache(df)
        return df

    def _save_to_cache(self, df: pd.DataFrame) -> None:
        """Save DataFrame to local cache."""
        logger.info(f"Saving dataset to cache: {self._cache_file}")
        df.to_parquet(self._cache_file, index=False)

    def clear_cache(self) -> None:
        """Remove cached dataset file."""
        if self._cache_file.exists():
            self._cache_file.unlink()
            logger.info("Cache cleared")

    @property
    def is_cached(self) -> bool:
        """Check if dataset is cached locally."""
        return self._cache_file.exists()
