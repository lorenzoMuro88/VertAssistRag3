from flask import Flask, request, session
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from rag.vectorstore import load_faiss_index
from routes.core import core_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Carica le variabili d'ambiente
load_dotenv()

# Configurazioni iniziali
MODEL = os.getenv("MODEL", "gpt-4")
# Configurazione percorsi
IS_PRODUCTION = os.getenv("FLASK_ENV") != "development"
BASE_DIR = "/data" if IS_PRODUCTION else "data"
INDEX_PATH = os.path.join("rag", "index.faiss")  # Indice nella directory dell'app
LOG_PATH = os.path.join(BASE_DIR, "logs", "queries.jsonl")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione file handler per i log
os.makedirs('logs', exist_ok=True)
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=1024 * 1024,  # 1MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(file_handler)

# Caricamento indice FAISS con gestione errori
try:
    faiss_index, texts, metadata = load_faiss_index(INDEX_PATH)
except Exception as e:
    logger.error(f"Failed to load FAISS index: {str(e)}")
    raise

# Inizializzazione Flask app
app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static'
)
app.secret_key = SECRET_KEY

# Configurazione CORS
CORS(app, resources={r"/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

# Configurazione rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Limiti specifici per route
@app.before_request
def before_request():
    # Limiti per le chiamate OpenAI
    if request.endpoint and 'openai' in request.endpoint:
        # Limite per utente
        limiter.limit(os.getenv("RATE_LIMIT_OPENAI_USER", "30 per hour"), 
                     key_func=lambda: f"openai_user_{session.get('user_id', 'anonymous')}")
        # Limite per IP
        limiter.limit(os.getenv("RATE_LIMIT_OPENAI_IP", "100 per hour"), 
                     key_func=get_remote_address)
        # Limite per modello specifico
        model = request.args.get('model', 'gpt-4')
        limiter.limit(os.getenv("RATE_LIMIT_OPENAI_MODEL", "20 per hour"), 
                     key_func=lambda: f"openai_model_{model}")

# Config globale accessibile nei blueprint
app.config["MODEL"] = MODEL
app.config["LOG_PATH"] = LOG_PATH
app.config["FAISS_INDEX"] = faiss_index
app.config["TEXTS"] = texts
app.config["METADATA"] = metadata

# Configurazione limiti OpenAI
app.config["OPENAI_LIMITS"] = {
    "gpt-4": {
        "requests_per_hour": int(os.getenv("OPENAI_GPT4_REQUESTS_PER_HOUR", "20")),
        "tokens_per_hour": int(os.getenv("OPENAI_GPT4_TOKENS_PER_HOUR", "100000")),
        "max_tokens_per_request": int(os.getenv("OPENAI_GPT4_MAX_TOKENS_PER_REQUEST", "4000"))
    },
    "gpt-3.5-turbo": {
        "requests_per_hour": int(os.getenv("OPENAI_GPT35_REQUESTS_PER_HOUR", "50")),
        "tokens_per_hour": int(os.getenv("OPENAI_GPT35_TOKENS_PER_HOUR", "200000")),
        "max_tokens_per_request": int(os.getenv("OPENAI_GPT35_MAX_TOKENS_PER_REQUEST", "4000"))
    }
}

# Registrazione Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(core_bp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)