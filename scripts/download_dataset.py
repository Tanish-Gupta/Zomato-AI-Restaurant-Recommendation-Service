"""
Download and cache the Zomato restaurant dataset from Hugging Face.
Run this once before starting the API to avoid slow or failed first requests.

Usage (from project root):
    python -m scripts.download_dataset
"""
import os
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use project-local HuggingFace cache so download works without extra permissions
HF_CACHE = PROJECT_ROOT / "data" / "hf_cache"
HF_CACHE.mkdir(parents=True, exist_ok=True)
os.environ["HF_DATASETS_CACHE"] = str(HF_CACHE)


def main():
    print("Downloading Zomato restaurant dataset from Hugging Face...")
    from src.phase1_data.loader import DatasetLoader
    from src.config import DATA_CACHE_DIR

    DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    loader = DatasetLoader()
    df = loader.load(force_reload=False)
    print(f"Done. Cached {len(df)} rows to {loader._cache_file}")
    # Warm repository (load + preprocess) to verify pipeline
    from src.phase1_data.repository import RestaurantRepository
    repo = RestaurantRepository()
    repo.initialize(force_reload=False)
    stats = repo.get_statistics()
    print(f"Repository ready: {stats['total_restaurants']} restaurants, "
          f"{stats['unique_cuisines']} cuisines, {stats['unique_locations']} locations.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
