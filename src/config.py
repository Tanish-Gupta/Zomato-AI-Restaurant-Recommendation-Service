"""Configuration management for the application."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

# Load .env from project root and from phase2_llm (if present)
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "src" / "phase2_llm" / ".env")
load_dotenv()  # cwd as fallback

DATA_CACHE_DIR = BASE_DIR / "data" / "cache"

DATASET_NAME = os.getenv("DATASET_NAME", "ManikaSaini/zomato-restaurant-recommendation")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
