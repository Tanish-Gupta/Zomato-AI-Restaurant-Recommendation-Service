"""Streamlit web interface for restaurant recommendations.

Run from project root with:
    PYTHONPATH=. streamlit run src/phase4_ui/streamlit_app.py
Or:
    python -m scripts.run_streamlit
"""

# Ensure repo root is on path (required for Streamlit Cloud and direct script run)
import sys
from pathlib import Path

def _find_repo_root() -> Path:
    """Walk up from this file until we find the repo root (directory containing 'src')."""
    d = Path(__file__).resolve().parent
    for _ in range(5):
        if (d / "src" / "phase4_ui" / "recommend_logic.py").exists():
            return d
        d = d.parent
    return Path(__file__).resolve().parent.parent.parent  # fallback

_REPO_ROOT = _find_repo_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from src.phase4_ui.recommend_logic import get_cuisines, get_locations, recommend

st.set_page_config(
    page_title="AI Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
)

st.title("🍽️ AI Restaurant Recommendations")
st.caption("Set your preferences and get personalized restaurant suggestions powered by the Zomato dataset and Groq LLM.")

# Load cuisines once (cached per session)
@st.cache_data(ttl=300)
def _get_cuisines():
    return get_cuisines()

cuisines = _get_cuisines()

with st.form("preferences_form"):
    col1, col2 = st.columns(2)
    with col1:
        cuisine = st.selectbox("Cuisine", options=cuisines, index=0)
        locations = get_locations(cuisine=None if (cuisine == "Any" or not cuisine) else cuisine)
        location = st.selectbox("Location", options=locations, index=0)
    with col2:
        price_range = st.selectbox(
            "Price range",
            options=["Any", "low", "medium", "high", "very_high"],
            index=0,
        )
        min_rating = st.number_input(
            "Min rating (0–5)",
            min_value=0.0,
            max_value=5.0,
            value=None,
            step=0.5,
            format="%.1f",
            placeholder="Any",
        )
    num_recommendations = st.slider("Number of results", min_value=1, max_value=50, value=10, step=1)
    additional_preferences = st.text_input(
        "Additional preferences (optional)",
        placeholder="e.g. vegetarian, outdoor seating",
    )
    submitted = st.form_submit_button("Get recommendations")

if submitted:
    with st.spinner("Finding restaurants…"):
        results_md, summary = recommend(
            cuisine=cuisine,
            location=location,
            price_range=price_range,
            min_rating=min_rating,
            num_recommendations=num_recommendations,
            additional_preferences=additional_preferences or "",
        )
    if summary:
        st.info(summary)
    st.markdown(results_md)
