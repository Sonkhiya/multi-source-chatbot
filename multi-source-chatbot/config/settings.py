import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
    
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store")
    METADATA_STORE_PATH = os.path.join(DATA_DIR, "metadata.db")
    PROCESSED_DOCS_PATH = os.path.join(DATA_DIR, "processed_documents")
    
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    
    @classmethod
    def ensure_dirs(cls):
        Path(cls.DATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.PROCESSED_DOCS_PATH).mkdir(parents=True, exist_ok=True)

settings = Settings()
