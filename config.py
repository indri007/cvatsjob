"""
Centralized configuration module.
Loads settings from .env file and provides config constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ─── Gemini ───────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")


# ─── Database ─────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'jobs.db'}")

# ─── Vector Store ─────────────────────────────────────────
VECTOR_STORE = os.getenv("VECTOR_STORE", "chromadb")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db"))
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION_NAME = "indonesian_jobs"

# ─── Embedding ────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "local")  # "local" or "openai"

# ─── N8N ──────────────────────────────────────────────────
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# ─── Dataset ──────────────────────────────────────────────
DATASET_PATH = BASE_DIR / "Dataset" / "jobs.jsonl"
DATA_DIR = BASE_DIR / "data"

# ─── App Settings ─────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = 100
SUPPORTED_CV_FORMATS = [".pdf", ".docx", ".doc"]
TOP_K_RESULTS = 10


from google import genai as google_genai

_gemini_client = None

def get_gemini_client():
    """Get or create the Gemini client."""
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        _gemini_client = google_genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client

def is_gemini_configured() -> bool:
    """Check if Gemini API key is set."""
    return bool(GEMINI_API_KEY)


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
