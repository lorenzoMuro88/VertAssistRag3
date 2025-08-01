from flask import Blueprint, request, Response, render_template, session, redirect, url_for, stream_with_context, jsonify
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
import numpy as np
import logging
import json
import re
from datetime import datetime
from rag.vectorstore import load_faiss_index, search_faiss
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from routes.admin import load_corrections

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL", "gpt-4o")

# Configurazione percorsi
IS_PRODUCTION = os.getenv("FLASK_ENV") != "development"
BASE_DIR = "/data" if IS_PRODUCTION else "data"
LOG_PATH = os.path.join(BASE_DIR, "logs", "queries.jsonl")

logger = logging.getLogger(__name__)

core_bp = Blueprint("core", __name__, template_folder="../templates")

# Carica l'indice FAISS dalla directory dell'applicazione
faiss_index, texts, metadata = load_faiss_index("rag/index.faiss")

def calculate_overlap(response: str, chunks: List[Dict[str, Any]]) -> float:
    def clean(text: str) -> set:
        return set(re.sub(r"[^\w]", " ", text.lower()).split())
    resp_tokens = clean(response)
    chunk_tokens = set()
    for chunk in chunks:
        chunk_tokens.update(clean(chunk["text"]))
    if not resp_tokens:
        return 0.0
    overlap = len(resp_tokens & chunk_tokens) / len(resp_tokens)
    return round(overlap * 100, 2)

@core_bp.route("/", endpoint="home")
def home():
    require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    if require_auth and (not session.get("authenticated") or session.get("role") != "user"):
        return redirect(url_for("auth.login"))
    return render_template("index.html")

@core_bp.route("/reset", methods=["POST"], endpoint="reset")
def reset():
    session.pop("history", None)
    return redirect(url_for("core.home"))

@core_bp.route("/ask", methods=["POST"], endpoint="ask")
def ask():
    require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    if require_auth and (not session.get("authenticated") or session.get("role") != "user"):
        return Response("Non autorizzato", status=401, mimetype="text/plain")

    data = request.get_json()
    user_query = data.get("message", "").strip()
    lang = data.get("lang", "it")
    if not user_query:
        return Response("Messaggio vuoto", status=400, mimetype="text/plain")

    corrections = load_corrections()
    if user_query in corrections:
        return Response(corrections[user_query], mimetype="text/plain")

    history = session.get("history", [])
    recent_turns = "\n".join([f"Utente: {q}\nAssistente: {a}" for q, a in history[-2:]])
    full_query = f"Conversazione fino a ora:\n{recent_turns}\nUtente: {user_query}" if recent_turns else user_query

    query_embedding = client.embeddings.create(
        input=[full_query],
        model="text-embedding-ada-002"
    ).data[0].embedding
    query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    results = search_faiss(faiss_index, texts, metadata, query_vector, top_k=int(os.getenv("TOP_K", 5)))
    valid_chunks = [r for r in results if len(r["text"].strip()) >= 30]

    if not valid_chunks:
        logger.warning(f"[FUORI AMBITO] Domanda: {user_query}")
        _log_interaction(user_query, 0.0, True, answer=None)
        return Response(
            "Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.\n\n"
            "Non trovi quello che stai cercando? Contattaci qui: [link placeholder]",
            mimetype="text/plain"
        )

    context = "\n---\n".join([r["text"] for r in valid_chunks])
    lang_prompts = {
        'it': "Rispondi sempre in italiano.",
        'en': "Always answer in English.",
        'fr': "Réponds toujours en français."
    }
    system_prompt = (
        lang_prompts.get(lang, lang_prompts['it']) + " " +
        "Sei un assistente specializzato nel fornire informazioni affidabili e dettagliate sulle case in affitto di Nomastay. "
        "Rispondi solo se trovi informazioni precise e complete nei documenti forniti nel contesto. "
        "Se la risposta non è chiaramente e completamente supportata dai documenti, rispondi esclusivamente: 'Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.' "
        "Non inventare, non dedurre, non usare conoscenze esterne, non fornire spiegazioni aggiuntive, non rispondere in modo generico o approssimativo. "
        "Usa solo ed esclusivamente le informazioni presenti nei documenti forniti. Se la domanda non è coperta, rispondi solo con la frase indicata, senza aggiungere altro. "
        "Rispondi sempre nella stessa lingua del contesto e traduci se necessario contenuti presenti nella conoscenza nella stessa lingua della richiesta. "
        "Non usare tag HTML o attributi nei link. Se devi citare un'immagine, scrivi solo il link come testo. Formatta le liste con i punti e le virgole."
        "Rispondi solo a domande relative a servizi, regole della casa, accesso, parcheggio, raccolta differenziata e informazioni pratiche sulla struttura. "
        "Non rispondere a domande personali, generiche, commerciali o che non riguardino direttamente il soggiorno nelle case Nomastay. "
        "Se nei documenti è presente un'immagine o un link a un'immagine correlata alla domanda, cita esplicitamente l'immagine.\n\n"
        
        "IMPORTANTE - ISTRUZIONI PER I CODICI KEYBOX:\n"
        "1. I codici keybox devono essere forniti SOLO se presenti nel documento 'keybox_codici.md'\n"
        "2. Non fornire mai codici keybox se non sei assolutamente certo che siano corretti\n"
        "3. Se l'utente chiede un codice senza specificare una stanza esatta, chiedi per quale stanza vuole il codice\n"
        "4. Non fornire mai codici keybox per stanze non elencate nel documento\n"
        "5. Se l'utente chiede un codice per una stanza che non esiste, informalo che la stanza non è presente nel sistema\n"
        "6. Non fare supposizioni o deduzioni sui codici keybox\n"
        "7. Se hai dubbi sulla validità di una richiesta, chiedi sempre chiarimenti\n\n"
        
        f"Contesto:\n{context}"
    )

    messages: List[ChatCompletionMessageParam] = [{"role": "system", "content": system_prompt}]
    for q, a in history[-2:]:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_query})

    def generate():
        accumulated = ""
        MIN_OVERLAP = float(os.getenv("MIN_OVERLAP", 0))

        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
            max_tokens=1024
        )
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                accumulated += delta
                yield delta.encode('utf-8')

        overlap_score = calculate_overlap(accumulated, valid_chunks)
        logger.info(f"Overlap con i chunk: {overlap_score}%%")

        if overlap_score < MIN_OVERLAP or "non sono in grado di rispondere" in accumulated.lower():
            logger.warning(f"Overlap troppo basso o risposta fallback: {overlap_score} < {MIN_OVERLAP}")
            _log_interaction(user_query, overlap_score, True, answer=accumulated)
            yield "Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.".encode('utf-8')
            return

        _log_interaction(user_query, overlap_score, False, answer=accumulated)
        yield f"\n\n[overlap:{overlap_score}]".encode('utf-8')

        if "non sono in grado di rispondere" in accumulated.lower():
            yield "\n\n Prova a formulare la domanda diversamente".encode('utf-8')

        history.append((user_query, accumulated))
        session["history"] = history[-6:]

    return Response(stream_with_context(generate()), mimetype="text/plain", direct_passthrough=True)

@core_bp.route("/analyze-image", methods=["POST"], endpoint="analyze_image")
def analyze_image():
    if os.getenv("ENABLE_IMAGE_ANALYSIS", "false").lower() != "true":
        return {"error": "Analisi immagine disattivata"}, 403

    uploaded = request.files.get("file")
    if not uploaded:
        return {"error": "Nessun file ricevuto"}, 400

    user_prompt = request.form.get("prompt", "").strip()
    try:
        import base64
        image_bytes = uploaded.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        system_prompt = "Sei un assistente specializzato nel fornire informazioni affidabili e dettagliate sulle case in affitto nomastay, inclusi servizi, regole, accessi e caratteristiche delle proprietà..."
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt or "Questa è l'immagine."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{uploaded.mimetype};base64,{image_b64}",
                        "detail": "high"
                    }}
                ]}
            ]
        )
        if completion.choices[0].message.content is not None:
            result = completion.choices[0].message.content.strip()
            return {"result": result}
        return {"error": "Nessuna risposta generata"}, 500
    except Exception as e:
        logger.exception("Errore durante l'analisi immagine")
        return {"error": str(e)}, 500

@core_bp.route('/check-image-analysis')
def check_image_analysis():
    try:
        enabled = os.getenv('ENABLE_IMAGE_ANALYSIS', 'false').lower() == 'true'
        print(f"ENABLE_IMAGE_ANALYSIS: {enabled}")  # Debug
        return jsonify({'enabled': enabled})
    except Exception as e:
        print(f"Errore nel controllo dell'analisi immagini: {str(e)}")  # Debug
        return jsonify({'enabled': False}), 500

@core_bp.route('/image-analysis')
def image_analysis():
    try:
        enabled = os.getenv('ENABLE_IMAGE_ANALYSIS', 'false').lower() == 'true'
        if not enabled:
            return redirect(url_for('core.home'))
        require_auth = os.getenv('REQUIRE_AUTH', 'false').lower() == 'true'
        if require_auth and not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return render_template('image_analysis.html')
    except Exception as e:
        print(f"Errore nell'accesso all'analisi immagini: {str(e)}")  # Debug
        return redirect(url_for('core.home'))

def _log_interaction(query: str, overlap: float, fallback: bool, answer: Optional[str] = None) -> None:
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "overlap": overlap,
        "fallback": fallback,
        "answer": answer
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data) + "\n")