import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config:
    """Configurações da aplicação"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Cache
    CACHE_FILE = "nf_cache.json"
    CACHE_TTL_HOURS = 24
    
    # OCR
    OCR_DPI = 100
    OCR_MAX_WORKERS = 6
    
    # FastAPI
    APP_TITLE = "NF PDF Extractor API"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
