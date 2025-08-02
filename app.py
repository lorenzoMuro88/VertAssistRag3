from flask import Flask, request, session
import logging
from logging.handlers import RotatingFileHandler
import os
from rag.vectorstore import load_faiss_index
from routes.core import core_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from error_handlers import register_error_handlers

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

def create_app():
    """Factory function per creare l'applicazione Flask"""
    
    # Valida la configurazione
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Errore di configurazione: {e}")
        raise
    
    # Caricamento indice FAISS con gestione errori
    try:
        faiss_index, texts, metadata = load_faiss_index(config.INDEX_PATH)
        logger.info("Indice FAISS caricato con successo")
    except Exception as e:
        logger.error(f"Errore nel caricamento dell'indice FAISS: {str(e)}")
        # In produzione, fallback con indice vuoto
        if config.IS_PRODUCTION:
            logger.warning("Utilizzo indice vuoto come fallback")
            faiss_index, texts, metadata = None, [], []
        else:
            raise
    
    # Inizializzazione Flask app
    app = Flask(__name__, 
        static_folder='static',
        static_url_path='/static'
    )
    app.secret_key = config.SECRET_KEY
    app.config.from_object(config)
    
    # Configurazione CORS
    CORS(app, resources={r"/*": {"origins": config.ALLOWED_ORIGINS}})
    
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
            limiter.limit(config.RATE_LIMIT_OPENAI_USER, 
                         key_func=lambda: f"openai_user_{session.get('user_id', 'anonymous')}")
            # Limite per IP
            limiter.limit(config.RATE_LIMIT_OPENAI_IP, 
                         key_func=get_remote_address)
            # Limite per modello specifico
            model = request.args.get('model', 'gpt-4')
            limiter.limit(config.RATE_LIMIT_OPENAI_MODEL, 
                         key_func=lambda: f"openai_model_{model}")
    
    # Config globale accessibile nei blueprint
    app.config["FAISS_INDEX"] = faiss_index
    app.config["TEXTS"] = texts
    app.config["METADATA"] = metadata
    
    # Registrazione gestori di errori
    register_error_handlers(app)
    
    # Registrazione Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(core_bp)
    
    return app

# Creazione dell'applicazione
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)