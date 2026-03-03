"""Prompt templates for restaurant recommendations via Groq LLM."""

SYSTEM_PROMPT = """You are a restaurant recommendation assistant. Based on the user's preferences and the available restaurant data, provide personalized recommendations with clear explanations.

Always respond in the following JSON format only, with no extra text before or after:
{
  "recommendations": [
    {
      "name": "Restaurant name",
      "cuisine": "Cuisine type",
      "location": "Location/area",
      "rating": 4.5,
      "price_range": "low|medium|high|very_high",
      "reason": "Brief explanation why this fits the user"
    }
  ],
  "summary": "One or two sentences summarizing your top picks for the user."
}

Rules:
- Return exactly the number of recommendations requested (or fewer if not enough match).
- Use only restaurants from the provided list; do not invent any.
- Keep reasons concise (1-2 sentences).
- If no restaurants match well, say so in summary and return an empty recommendations array."""

USER_PROMPT_TEMPLATE = """User preferences:
- Cuisine: {cuisine}
- Location: {location}
- Price range: {price_range}
- Minimum rating: {min_rating}
- Additional notes: {additional_preferences}

Request: Recommend the top {num_recommendations} restaurants from the list below.

Available restaurants (one per line, format: Name | Cuisine | Location | Rating | Price):
{formatted_restaurant_list}

Respond with valid JSON only."""


def build_user_prompt(
    cuisine: str = "Any",
    location: str = "Any",
    price_range: str = "Any",
    min_rating: str = "Any",
    num_recommendations: int = 5,
    additional_preferences: str = "",
    formatted_restaurant_list: str = "",
) -> str:
    """
    Build the user prompt with preferences and restaurant list.

    Args:
        cuisine: User's cuisine preference.
        location: User's location preference.
        price_range: User's price range (low/medium/high).
        min_rating: Minimum rating filter.
        num_recommendations: Number of recommendations to return.
        additional_preferences: Free-text extra preferences.
        formatted_restaurant_list: Pre-formatted list of restaurants for context.

    Returns:
        Formatted user prompt string.
    """
    return USER_PROMPT_TEMPLATE.format(
        cuisine=cuisine or "Any",
        location=location or "Any",
        price_range=price_range or "Any",
        min_rating=min_rating if min_rating is not None else "Any",
        num_recommendations=num_recommendations,
        additional_preferences=additional_preferences or "None",
        formatted_restaurant_list=formatted_restaurant_list or "No restaurants available.",
    )


def format_restaurants_for_prompt(
    restaurants_df,
    name_col: str,
    cuisine_col: str,
    location_col: str,
    rating_col: str,
    price_col: str,
    max_lines: int = 50,
) -> str:
    """
    Format a DataFrame of restaurants into a text block for the LLM prompt.

    Args:
        restaurants_df: DataFrame with restaurant rows.
        name_col: Column name for restaurant name.
        cuisine_col: Column name for cuisine.
        location_col: Column name for location.
        rating_col: Column name for rating.
        price_col: Column name for price (or price category column).
        max_lines: Maximum number of restaurants to include (to avoid token limits).

    Returns:
        Multi-line string, one restaurant per line.
    """
    import pandas as pd

    df = restaurants_df.head(max_lines)
    lines = []

    for _, row in df.iterrows():
        name = str(row.get(name_col, ""))[:60]
        cuisine = str(row.get(cuisine_col, ""))[:40]
        loc = str(row.get(location_col, ""))[:40]
        rating = row.get(rating_col, "")
        if pd.notna(rating):
            rating = f"{float(rating):.1f}"
        else:
            rating = "N/A"
        price = str(row.get(price_col, ""))
        price_cat = row.get(f"{price_col}_category", price)
        price_str = str(price_cat) if pd.notna(price_cat) else str(price)
        lines.append(f"{name} | {cuisine} | {loc} | {rating} | {price_str}")

    return "\n".join(lines) if lines else "No restaurants available."
