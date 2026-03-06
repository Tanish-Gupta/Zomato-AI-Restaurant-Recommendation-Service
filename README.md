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

## Deploy on Vercel (frontend + backend)

**Option A – Frontend only on Vercel (recommended for production)**  
Vercel's serverless `/tmp` is too small (~512 MB) for the full Hugging Face dataset (~1 GB). For a working API with the full dataset and LLM:

1. Deploy the **API** on [Railway](https://railway.app) or [Render](https://render.com) (run `uvicorn src.main:app --host 0.0.0.0 --port $PORT`).
2. Deploy the **frontend** on Vercel and set **`VITE_API_URL`** to your API URL (e.g. `https://your-app.onrender.com`).
3. On the API host, set **`CORS_EXTRA_ORIGINS`** to your Vercel app URL.

**Option B – Frontend + API on the same Vercel project**  
The `api/` folder is deployed as serverless functions. This works for a **demo**, but the first request will try to download the dataset and will fail with "Not enough disk space" because the dataset needs ~1 GB and Vercel's disk is limited. The app will show a message directing users to deploy the API on Railway or Render. To try it anyway:

1. Import the repo in Vercel. Build and env are read from `vercel.json`.
2. Set **`GROQ_API_KEY`** if you want LLM summaries.
3. Leave **`VITE_API_URL`** unset to use the same origin.

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
