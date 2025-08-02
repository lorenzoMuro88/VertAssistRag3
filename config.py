import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

class Config:
    """Configurazione centralizzata dell'applicazione"""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    PORT = int(os.getenv("PORT", 8080))
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")  # Modello più veloce per default
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # RAG
    TOP_K = int(os.getenv("TOP_K", 5))
    MIN_OVERLAP = float(os.getenv("MIN_OVERLAP", 0.3))  # Ridotto da 0.7 a 0.3 (30%)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    
    # Quality Control
    ENABLE_ADAPTIVE_QUALITY = os.getenv("ENABLE_ADAPTIVE_QUALITY", "true").lower() == "true"
    QUALITY_DEBUG_MODE = os.getenv("QUALITY_DEBUG_MODE", "false").lower() == "true"
    
    # Percorsi
    IS_PRODUCTION = FLASK_ENV != "development"
    BASE_DIR = "/data" if IS_PRODUCTION else "data"
    INDEX_PATH = os.path.join("rag", "index.faiss")
    LOG_PATH = os.path.join(BASE_DIR, "logs", "queries.jsonl")
    METADATA_PATH = os.path.join(BASE_DIR, "documents", "metadata.json")
    
    # Rate Limiting
    RATE_LIMIT_OPENAI_USER = os.getenv("RATE_LIMIT_OPENAI_USER", "30 per hour")
    RATE_LIMIT_OPENAI_IP = os.getenv("RATE_LIMIT_OPENAI_IP", "100 per hour")
    RATE_LIMIT_OPENAI_MODEL = os.getenv("RATE_LIMIT_OPENAI_MODEL", "20 per hour")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    
    # Autenticazione
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_PASS = os.getenv("ADMIN_PASS")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "vertassistrag3-secret-key-2024-secure")
    REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    
    # OpenAI Limits
    OPENAI_LIMITS = {
        "gpt-4": {
            "requests_per_hour": int(os.getenv("OPENAI_GPT4_REQUESTS_PER_HOUR", "20")),
            "tokens_per_hour": int(os.getenv("OPENAI_GPT4_TOKENS_PER_HOUR", "100000")),
            "max_tokens_per_request": int(os.getenv("OPENAI_GPT4_MAX_TOKENS_PER_REQUEST", "4000"))
        },
        "gpt-4o-mini": {
            "requests_per_hour": int(os.getenv("OPENAI_GPT4O_MINI_REQUESTS_PER_HOUR", "100")),
            "tokens_per_hour": int(os.getenv("OPENAI_GPT4O_MINI_TOKENS_PER_HOUR", "500000")),
            "max_tokens_per_request": int(os.getenv("OPENAI_GPT4O_MINI_MAX_TOKENS_PER_REQUEST", "4000"))
        },
        "gpt-3.5-turbo": {
            "requests_per_hour": int(os.getenv("OPENAI_GPT35_REQUESTS_PER_HOUR", "50")),
            "tokens_per_hour": int(os.getenv("OPENAI_GPT35_TOKENS_PER_HOUR", "200000")),
            "max_tokens_per_request": int(os.getenv("OPENAI_GPT35_MAX_TOKENS_PER_REQUEST", "4000"))
        }
    }
    
    @classmethod
    def validate(cls):
        """Valida la configurazione richiesta"""
        required_vars = [
            ("SECRET_KEY", cls.SECRET_KEY),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing = []
        for name, value in required_vars:
            if not value:
                missing.append(name)
        
        if missing:
            raise ValueError(f"Variabili d'ambiente mancanti: {', '.join(missing)}")
        
        return True

class DevelopmentConfig(Config):
    """Configurazione per sviluppo"""
    DEBUG = True
    FLASK_ENV = "development"

class ProductionConfig(Config):
    """Configurazione per produzione"""
    DEBUG = False
    FLASK_ENV = "production"

# Configurazione attiva
config = ProductionConfig if os.getenv("FLASK_ENV") == "production" else DevelopmentConfig 