"""
Extensive testing of recommendation API with multiple filter combinations.
Uses RecommendationService directly (no HTTP). With GROQ_API_KEY unset, uses fallback by rating.
Run from project root: python3 -m scripts.test_recommendations
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("HF_DATASETS_CACHE", str(PROJECT_ROOT / "data" / "hf_cache"))

def main():
    from src.phase1_data import RestaurantRepository
    from src.phase3_api.recommendation import RecommendationService
    from src.phase3_api.schemas import RecommendationRequest

    print("Initializing repository and service...")
    repo = RestaurantRepository()
    repo.initialize(force_reload=False)
    service = RecommendationService(repository=repo)

    cuisines = repo.get_unique_cuisines()
    locations = repo.get_unique_locations()
    # Use a few real values for combo tests
    sample_cuisines = [c for c in cuisines if c and c != "Unknown"][:8]
    sample_locations = [l for l in locations if l and l != "Unknown"][:8]
    if not sample_cuisines:
        sample_cuisines = ["North Indian", "Chinese"]  # fallback names
    if not sample_locations:
        sample_locations = ["Koramangala", "Indiranagar"]

    # Define test cases: (description, RecommendationRequest kwargs, expect_results=True/False)
    # expect_results=True means we expect at least 1 recommendation (or a clear empty message)
    cases = []

    # No filters
    cases.append(("No filters", {"num_recommendations": 3}, True))
    cases.append(("No filters, 10 results", {"num_recommendations": 10}, True))

    # min_rating only (0 = no filter)
    cases.append(("min_rating=0 (no minimum)", {"min_rating": 0.0, "num_recommendations": 3}, True))
    cases.append(("min_rating=3", {"min_rating": 3.0, "num_recommendations": 3}, True))
    cases.append(("min_rating=4", {"min_rating": 4.0, "num_recommendations": 3}, True))
    cases.append(("min_rating=4.5", {"min_rating": 4.5, "num_recommendations": 3}, True))

    # Single filter: cuisine
    for c in sample_cuisines[:3]:
        cases.append((f"cuisine={c}", {"cuisine": c, "num_recommendations": 3}, True))
    # Partial cuisine match
    cases.append(("cuisine=Indian (partial)", {"cuisine": "Indian", "num_recommendations": 3}, True))

    # Single filter: location
    for loc in sample_locations[:3]:
        cases.append((f"location={loc}", {"location": loc, "num_recommendations": 3}, True))

    # Single filter: price_range
    for pr in ["low", "medium", "high", "very_high"]:
        cases.append((f"price_range={pr}", {"price_range": pr, "num_recommendations": 3}, True))

    # Two filters
    cases.append(("cuisine + location", {
        "cuisine": sample_cuisines[0] if sample_cuisines else "North Indian",
        "location": sample_locations[0] if sample_locations else "Koramangala",
        "num_recommendations": 3,
    }, True))
    cases.append(("cuisine + min_rating", {
        "cuisine": sample_cuisines[0] if sample_cuisines else "North Indian",
        "min_rating": 3.5,
        "num_recommendations": 3,
    }, True))
    cases.append(("location + price_range=medium", {
        "location": sample_locations[0] if sample_locations else "Koramangala",
        "price_range": "medium",
        "num_recommendations": 3,
    }, True))
    cases.append(("min_rating + price_range", {
        "min_rating": 3.0,
        "price_range": "medium",
        "num_recommendations": 3,
    }, True))

    # Three filters
    cases.append(("cuisine + location + min_rating", {
        "cuisine": sample_cuisines[0] if sample_cuisines else "North Indian",
        "location": sample_locations[0] if sample_locations else "Koramangala",
        "min_rating": 3.0,
        "num_recommendations": 3,
    }, True))
    cases.append(("cuisine + location + price_range", {
        "cuisine": sample_cuisines[0] if sample_cuisines else "North Indian",
        "location": sample_locations[0] if sample_locations else "Koramangala",
        "price_range": "low",
        "num_recommendations": 3,
    }, True))

    # Four filters
    cases.append(("all filters", {
        "cuisine": sample_cuisines[0] if sample_cuisines else "North Indian",
        "location": sample_locations[0] if sample_locations else "Koramangala",
        "price_range": "medium",
        "min_rating": 3.0,
        "num_recommendations": 3,
    }, True))

    # Edge: very strict (might get 0 results – we still expect valid response)
    cases.append(("strict: high rating + very_high price", {
        "min_rating": 4.8,
        "price_range": "very_high",
        "num_recommendations": 5,
    }, None))  # None = don't require results, just no crash
    cases.append(("strict: niche cuisine + location", {
        "cuisine": sample_cuisines[-1] if len(sample_cuisines) >= 2 else "North Indian",
        "location": sample_locations[-1] if len(sample_locations) >= 2 else "Koramangala",
        "min_rating": 4.5,
        "num_recommendations": 5,
    }, None))

    # Optional extra preferences
    cases.append(("no filters + additional_preferences", {
        "additional_preferences": "vegetarian",
        "num_recommendations": 3,
    }, True))

    passed = 0
    failed = 0
    errors = []

    for desc, kwargs, expect_results in cases:
        req = RecommendationRequest(**kwargs)
        try:
            resp = service.get_recommendations(req)
            n = len(resp.recommendations)
            if expect_results is True and n == 0 and not resp.summary:
                failed += 1
                errors.append(f"  [{desc}] expected some result or summary, got 0 recs and no summary")
            elif expect_results is True and n > 0:
                passed += 1
                print(f"  OK  {desc} -> {n} recommendations")
            elif expect_results is True and n == 0 and resp.summary:
                passed += 1
                print(f"  OK  {desc} -> 0 recommendations (summary: {resp.summary[:50]}...)")
            elif expect_results is None:
                passed += 1
                print(f"  OK  {desc} -> {n} recommendations (strict combo)")
            else:
                passed += 1
                print(f"  OK  {desc} -> {n} recommendations")
        except Exception as e:
            failed += 1
            errors.append(f"  [{desc}] {type(e).__name__}: {e}")
            print(f"  FAIL {desc} -> {type(e).__name__}: {e}")

    print()
    print(f"Result: {passed} passed, {failed} failed")
    if errors:
        print("Errors:")
        for e in errors:
            print(e)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
