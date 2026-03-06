# AI Restaurant Recommendation Service

An intelligent restaurant recommendation system using the Zomato dataset (Hugging Face) and Groq LLM for personalized suggestions.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # Add your GROQ_API_KEY
```

If Gradio fails to import (`HfFolder` error), pin HuggingFace Hub:

```bash
pip install 'huggingface_hub>=0.23,<1.0'
```

## Download the dataset (run once)

Download and cache the Zomato dataset so the API and UI return results quickly:

```bash
python -m scripts.download_dataset
```

Then start the API and/or UI.

## Run the app

**API (port 8000):**

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/health  

**Streamlit UI (port 8501):**

```bash
python -m scripts.run_streamlit
```

- Open http://localhost:8501 (first load may take ~30s while the dataset loads)

**Gradio UI (port 7860):**

```bash
python3 -c "from src.phase4_ui.gradio_app import run_ui; run_ui(server_port=7860)"
```

- Open http://127.0.0.1:7860 (first load may take ~30s while the dataset loads)

**React UI (port 5173 or 5174):**

```bash
# Terminal 1: start API first (required — frontend will show an error if API is not running)
python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: start frontend
cd frontend && npm install && npm run dev
```

- Open the URL Vite prints (e.g. http://localhost:5173 or http://localhost:5174). The UI will show a clear message if the API is not reachable.

## Deploy on Vercel (React UI)

The React frontend can be deployed on [Vercel](https://vercel.com):

1. **Import the repo** in Vercel (New Project → Import Git Repository).
2. **Build settings** are read from the root `vercel.json`: the app builds from the `frontend` folder and outputs `frontend/dist`. No need to set Root Directory if you use this config.
3. **Environment variable (required for live API):** In Vercel → Project → Settings → Environment Variables, add:
   - **Name:** `VITE_API_URL`  
   - **Value:** your deployed API URL (e.g. `https://your-api.onrender.com` or `https://your-api.railway.app`).  
   The frontend calls this URL for cuisines, locations, and recommendations. If you leave it unset, the app will try `http://localhost:8000` and will only work if users have the API running locally.
4. **Deploy the API separately** (the FastAPI backend is not run on Vercel). Deploy it on [Railway](https://railway.app), [Render](https://render.com), or another host, then set `VITE_API_URL` in Vercel to that API URL. On the API host, set the env var `CORS_EXTRA_ORIGINS` to your Vercel app URL (e.g. `https://your-app.vercel.app`) so the browser can call the API.

After deployment, the Vercel URL will serve the same React UI (nav, hero, cards, sort, pagination) as when you run locally.

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
- `src/phase4_ui/` — Streamlit & Gradio UIs
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
