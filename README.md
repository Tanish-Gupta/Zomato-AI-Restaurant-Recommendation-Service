# AI Restaurant Recommendation Service

An intelligent restaurant recommendation system using the Zomato dataset (Hugging Face) and Groq LLM for personalized suggestions.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # Add your GROQ_API_KEY
```

## Run tests

```bash
# Phase 1 (data layer)
pytest tests/phase1/ -v

# Phase 2 (LLM; set GROQ_API_KEY for integration test)
pytest tests/phase2/ -v
```

## Project structure

- `src/phase1_data/` — Data loading, preprocessing, repository
- `src/phase2_llm/` — Groq LLM service, prompts, response parsing
- `src/phase3_api/` — API (placeholder)
- `src/phase4_ui/` — UI (placeholder)
- `src/phase5_optimization/` — Optimizations (placeholder)

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design.

## Push to GitHub

If you haven't linked this repo to GitHub yet:

1. Create a new repository on [GitHub](https://github.com/new) (e.g. `Zomato-AI-Restaurant-Recommendation-Service`).
2. Add the remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repository name.
