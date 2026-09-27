"""Configuration and environment management for Stainless Steel Recommender"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
GRADES_DB_PATH = DATA_DIR / "grades_database.json"
KB_DIR = DATA_DIR / "knowledge_base"
FAISS_DIR = DATA_DIR / "faiss_index"


class Config:
    """Application configuration and credentials"""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    EVALUATOR_MODEL = os.getenv("EVALUATOR_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150

    # Default weights for general engineering optimization
    DEFAULT_WEIGHTS = {
        "corrosion": 0.30,
        "strength": 0.25,
        "cost": 0.20,
        "formability": 0.15,
        "weldability": 0.10
    }

    @classmethod
    def is_llm_available(cls) -> bool:
        """Check if Groq API key is configured"""
        key = cls.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
        return bool(key and len(key.strip()) > 5)

    @classmethod
    def get_llm(cls, temperature: float = 0.1):
        """Get ChatGroq LLM instance if configured, else None"""
        if not cls.is_llm_available():
            return None
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=cls.LLM_MODEL,
                api_key=cls.GROQ_API_KEY,
                temperature=temperature
            )
        except Exception:
            return None


__all__ = [
    "Config",
    "BASE_DIR",
    "DATA_DIR",
    "GRADES_DB_PATH",
    "KB_DIR",
    "FAISS_DIR"
]