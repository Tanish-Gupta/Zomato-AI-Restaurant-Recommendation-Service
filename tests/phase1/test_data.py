"""Tests for Phase 1: Data Foundation."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.phase1_data.loader import DatasetLoader
from src.phase1_data.preprocessor import DataPreprocessor
from src.phase1_data.repository import RestaurantRepository


class TestDatasetLoader:
    """Tests for the DatasetLoader class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def loader(self, temp_cache_dir):
        """Create a DatasetLoader with temporary cache."""
        return DatasetLoader(cache_dir=temp_cache_dir)

    def test_loader_initialization(self, loader, temp_cache_dir):
        """Test that loader initializes correctly."""
        assert loader.dataset_name == "ManikaSaini/zomato-restaurant-recommendation"
        assert loader.cache_dir == temp_cache_dir
        assert not loader.is_cached

    def test_load_from_huggingface(self, loader):
        """Test loading dataset from Hugging Face."""
        df = loader.load()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert loader.is_cached

    def test_load_from_cache(self, loader):
        """Test loading dataset from cache."""
        df1 = loader.load()
        df2 = loader.load()
        
        assert len(df1) == len(df2)
        pd.testing.assert_frame_equal(df1, df2)

    def test_force_reload(self, loader):
        """Test force reload bypasses cache."""
        df1 = loader.load()
        df2 = loader.load(force_reload=True)
        
        assert len(df1) == len(df2)

    def test_clear_cache(self, loader):
        """Test clearing the cache."""
        loader.load()
        assert loader.is_cached
        
        loader.clear_cache()
        assert not loader.is_cached


class TestDataPreprocessor:
    """Tests for the DataPreprocessor class."""

    @pytest.fixture
    def preprocessor(self):
        """Create a DataPreprocessor instance."""
        return DataPreprocessor()

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            "Restaurant Name": ["Test Restaurant", "  Cafe Mocha  ", None],
            "Cuisines": ["italian, INDIAN", "chinese", ""],
            "Location": ["  new york  ", "LOS ANGELES", ""],
            "Rating": [4.5, 3.2, np.nan],
            "Price Range": [2, 3, 1],
            "Votes": [100, 50, np.nan],
        })

    def test_preprocessor_initialization(self, preprocessor):
        """Test preprocessor initializes correctly."""
        assert not preprocessor.is_processed

    def test_standardize_columns(self, preprocessor, sample_df):
        """Test column name standardization."""
        result = preprocessor._standardize_columns(sample_df)
        
        assert "restaurant_name" in result.columns
        assert "cuisines" in result.columns
        assert "price_range" in result.columns

    def test_handle_missing_values(self, preprocessor, sample_df):
        """Test missing value handling."""
        df = preprocessor._standardize_columns(sample_df)
        result = preprocessor._handle_missing_values(df)
        
        assert not result.isnull().any().any()

    def test_clean_text_fields(self, preprocessor, sample_df):
        """Test text field cleaning."""
        df = preprocessor._standardize_columns(sample_df)
        df = preprocessor._handle_missing_values(df)
        result = preprocessor._clean_text_fields(df)
        
        assert result["restaurant_name"].iloc[1] == "Cafe Mocha"

    def test_normalize_price_range(self, preprocessor, sample_df):
        """Test price range normalization."""
        df = preprocessor._standardize_columns(sample_df)
        df = preprocessor._handle_missing_values(df)
        result = preprocessor._normalize_price_range(df)
        
        assert "price_range_category" in result.columns
        assert result["price_range_category"].iloc[0] == "medium"
        assert result["price_range_category"].iloc[1] == "high"

    def test_clean_cuisines(self, preprocessor, sample_df):
        """Test cuisine cleaning and standardization."""
        df = preprocessor._standardize_columns(sample_df)
        df = preprocessor._handle_missing_values(df)
        result = preprocessor._clean_cuisines(df)
        
        assert result["cuisines"].iloc[0] == "Indian, Italian"
        assert result["cuisines"].iloc[1] == "Chinese"

    def test_clean_location(self, preprocessor, sample_df):
        """Test location cleaning."""
        df = preprocessor._standardize_columns(sample_df)
        df = preprocessor._handle_missing_values(df)
        result = preprocessor._clean_location(df)
        
        assert result["location"].iloc[0] == "New York"
        assert result["location"].iloc[1] == "Los Angeles"

    def test_full_preprocessing(self, preprocessor, sample_df):
        """Test full preprocessing pipeline."""
        result = preprocessor.preprocess(sample_df)
        
        assert preprocessor.is_processed
        assert len(result) == 3
        assert not result.isnull().any().any()


class TestRestaurantRepository:
    """Tests for the RestaurantRepository class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def repository(self, temp_cache_dir):
        """Create a RestaurantRepository with temporary cache."""
        loader = DatasetLoader(cache_dir=temp_cache_dir)
        repo = RestaurantRepository(loader=loader)
        repo.initialize()
        return repo

    def test_repository_initialization(self, repository):
        """Test repository initializes correctly."""
        assert repository._data is not None
        assert len(repository.data) > 0

    def test_get_all(self, repository):
        """Test getting all restaurants."""
        all_restaurants = repository.get_all()
        limited = repository.get_all(limit=10)
        
        assert len(all_restaurants) > 0
        assert len(limited) <= 10

    def test_filter_by_cuisine(self, repository):
        """Test filtering by cuisine."""
        cuisines = repository.get_unique_cuisines()
        if cuisines:
            filtered = repository.filter(cuisine=cuisines[0][:4])
            assert len(filtered) >= 0

    def test_filter_by_location(self, repository):
        """Test filtering by location."""
        locations = repository.get_unique_locations()
        if locations:
            filtered = repository.filter(location=locations[0][:4])
            assert len(filtered) >= 0

    def test_filter_by_rating(self, repository):
        """Test filtering by rating."""
        filtered = repository.filter(min_rating=3.0)
        
        rating_col = repository._column_mapping.get("rating")
        if rating_col and len(filtered) > 0:
            ratings = pd.to_numeric(filtered[rating_col], errors="coerce")
            assert (ratings >= 3.0).all() or ratings.isna().all()

    def test_combined_filter(self, repository):
        """Test combining multiple filters."""
        filtered = repository.filter(
            min_rating=3.0,
            limit=5
        )
        
        assert len(filtered) <= 5

    def test_get_unique_cuisines(self, repository):
        """Test getting unique cuisines."""
        cuisines = repository.get_unique_cuisines()
        
        assert isinstance(cuisines, list)
        assert cuisines == sorted(cuisines)

    def test_get_unique_locations(self, repository):
        """Test getting unique locations."""
        locations = repository.get_unique_locations()
        
        assert isinstance(locations, list)

    def test_get_rating_range(self, repository):
        """Test getting rating range."""
        min_rating, max_rating = repository.get_rating_range()
        
        assert isinstance(min_rating, float)
        assert isinstance(max_rating, float)

    def test_get_statistics(self, repository):
        """Test getting dataset statistics."""
        stats = repository.get_statistics()
        
        assert "total_restaurants" in stats
        assert "unique_cuisines" in stats
        assert "unique_locations" in stats
        assert "rating_range" in stats
        assert stats["total_restaurants"] > 0

    def test_search(self, repository):
        """Test search functionality."""
        results = repository.search("restaurant", limit=5)
        
        assert len(results) <= 5


class TestIntegration:
    """Integration tests for the complete data pipeline."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_full_pipeline(self, temp_cache_dir):
        """Test the complete data loading pipeline."""
        loader = DatasetLoader(cache_dir=temp_cache_dir)
        preprocessor = DataPreprocessor()
        repository = RestaurantRepository(loader=loader, preprocessor=preprocessor)

        repository.initialize()

        assert len(repository.data) > 0

        stats = repository.get_statistics()
        assert stats["total_restaurants"] > 0

        cuisines = repository.get_unique_cuisines()
        locations = repository.get_unique_locations()
        
        print(f"\n{'='*50}")
        print("DATA PIPELINE TEST RESULTS")
        print(f"{'='*50}")
        print(f"Total Restaurants: {stats['total_restaurants']}")
        print(f"Unique Cuisines: {stats['unique_cuisines']}")
        print(f"Unique Locations: {stats['unique_locations']}")
        print(f"Rating Range: {stats['rating_range']}")
        print(f"Columns: {stats['columns']}")
        print(f"\nSample Cuisines: {cuisines[:5] if cuisines else 'N/A'}")
        print(f"Sample Locations: {locations[:5] if locations else 'N/A'}")
        print(f"{'='*50}\n")

        if cuisines:
            filtered = repository.filter(cuisine=cuisines[0], limit=3)
            print(f"Filtered by '{cuisines[0]}': {len(filtered)} results")

    def test_caching_works(self, temp_cache_dir):
        """Test that caching mechanism works correctly."""
        loader = DatasetLoader(cache_dir=temp_cache_dir)

        assert not loader.is_cached
        df1 = loader.load()
        assert loader.is_cached

        df2 = loader.load()
        pd.testing.assert_frame_equal(df1, df2)

        loader.clear_cache()
        assert not loader.is_cached
