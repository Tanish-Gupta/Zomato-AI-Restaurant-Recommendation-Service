"""Command-line interface for restaurant recommendations."""

import argparse
import json
import sys
from typing import Optional

from src.phase3_api.recommendation import RecommendationService
from src.phase3_api.schemas import RecommendationRequest


def main(args: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Get restaurant recommendations")
    parser.add_argument("--cuisine", type=str, default=None, help="Cuisine filter")
    parser.add_argument("--location", type=str, default=None, help="Location filter")
    parser.add_argument("--price", type=str, default=None, choices=["low", "medium", "high", "very_high"])
    parser.add_argument("--min-rating", type=float, default=None, help="Minimum rating 0-5")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of recommendations (default 5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--preferences", type=str, default="", help="Additional preferences")
    parsed = parser.parse_args(args)

    req = RecommendationRequest(
        cuisine=parsed.cuisine,
        location=parsed.location,
        price_range=parsed.price,
        min_rating=parsed.min_rating,
        num_recommendations=parsed.num,
        additional_preferences=parsed.preferences or "",
    )
    try:
        svc = RecommendationService()
        svc._repo.initialize()
        resp = svc.get_recommendations(req)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if parsed.json:
        out = {
            "recommendations": [r.model_dump() for r in resp.recommendations],
            "summary": resp.summary,
            "query_context": resp.query_context,
        }
        print(json.dumps(out, indent=2))
        return 0

    print(resp.summary)
    print()
    for i, r in enumerate(resp.recommendations, 1):
        print(f"{i}. {r.name}")
        print(f"   {r.cuisine} | {r.location} | Rating: {r.rating} | Price: {r.price_range}")
        if r.reason:
            print(f"   {r.reason}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
