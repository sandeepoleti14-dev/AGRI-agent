"""
Central config — loads .env and exposes typed constants.
All modules import from here, never from os.environ directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = str(DATA_DIR / "farmers.db")
CHROMA_DIR = str(DATA_DIR / "chroma_db")
RAW_DOCS_DIR = str(DATA_DIR / "raw_docs")

# ── LLM (Google Gemini) ───────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DECISION_MODEL = os.getenv("DECISION_MODEL", "gemini-3.5-flash-lite")
VISION_MODEL = os.getenv("VISION_MODEL", "gemini-3.8-flash")
# ── RAG ───────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

# ── Thresholds ────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "75.0"))
WEATHER_TIMEOUT_SECONDS = int(os.getenv("WEATHER_TIMEOUT_SECONDS", "10"))
