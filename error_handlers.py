from flask import Blueprint, jsonify, render_template, request
import logging
from werkzeug.exceptions import HTTPException
from openai import OpenAIError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Registra i gestori di errori per l'applicazione Flask"""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Richiesta non valida", "details": str(error)}), 400
        return render_template("error.html", error="Richiesta non valida", code=400), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Non autorizzato", "details": "Credenziali mancanti o non valide"}), 401
        return render_template("error.html", error="Non autorizzato", code=401), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Accesso negato", "details": "Non hai i permessi per accedere a questa risorsa"}), 403
        return render_template("error.html", error="Accesso negato", code=403), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Pagina non trovata", "details": "La risorsa richiesta non esiste"}), 404
        return render_template("error.html", error="Pagina non trovata", code=404), 404
    
    @app.errorhandler(429)
    def too_many_requests(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Troppe richieste", "details": "Hai superato il limite di richieste"}), 429
        return render_template("error.html", error="Troppe richieste", code=429), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Errore interno del server: {error}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Errore interno del server", "details": "Si è verificato un errore imprevisto"}), 500
        return render_template("error.html", error="Errore interno del server", code=500), 500
    
    @app.errorhandler(OpenAIError)
    def openai_error(error):
        logger.error(f"Errore OpenAI: {error}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Errore del servizio AI", "details": "Problema con il servizio di intelligenza artificiale"}), 503
        return render_template("error.html", error="Errore del servizio AI", code=503), 503
    
    @app.errorhandler(RateLimitError)
    def rate_limit_error(error):
        logger.warning(f"Rate limit raggiunto: {error}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Limite di richieste raggiunto", "details": "Troppe richieste al servizio AI"}), 429
        return render_template("error.html", error="Limite di richieste raggiunto", code=429), 429
    
    @app.errorhandler(APITimeoutError)
    def timeout_error(error):
        logger.error(f"Timeout API: {error}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Timeout del servizio", "details": "Il servizio AI non ha risposto in tempo"}), 504
        return render_template("error.html", error="Timeout del servizio", code=504), 504
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Errore non gestito: {error}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"error": "Errore imprevisto", "details": "Si è verificato un errore non previsto"}), 500
        return render_template("error.html", error="Errore imprevisto", code=500), 500

class RAGError(Exception):
    """Eccezione personalizzata per errori RAG"""
    pass

class IndexNotFoundError(RAGError):
    """Eccezione per indice FAISS non trovato"""
    pass

class InvalidQueryError(RAGError):
    """Eccezione per query non valide"""
    pass 