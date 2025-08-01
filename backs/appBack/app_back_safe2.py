from flask import Flask, request, Response, render_template, session, redirect, url_for, stream_with_context
from dotenv import load_dotenv
from openai import OpenAI
import os
import numpy as np
from rag.vectorstore import load_faiss_index, search_faiss
import logging
import re
from datetime import datetime
import json

# Funzione per calcolare l'overlap tra la risposta e i chunk usati
def calculate_overlap(response, chunks):
    def clean(text):
        return set(re.sub(r"[^\w]", " ", text.lower()).split())

    resp_tokens = clean(response)
    chunk_tokens = set()
    for chunk in chunks:
        chunk_tokens.update(clean(chunk["text"]))

    if not resp_tokens:
        return 0.0

    overlap = len(resp_tokens & chunk_tokens) / len(resp_tokens)
    return round(overlap * 100, 2)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caricamento ambiente e client OpenAI
load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o")
LOG_PATH = "../../logs/queries.jsonl"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "rag_secret")

# Carica l'indice FAISS dalla directory dell'applicazione
faiss_index, texts, metadata = load_faiss_index("rag/index.faiss")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return redirect(url_for("home"))

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("message", "").strip()

    if not query:
        return Response("Messaggio vuoto", status=400, mimetype="text/plain")

    history = session.get("history", [])

    logger.info("CONVERSAZIONE ATTUALE:")
    for q, a in history[-2:]:
        logger.info(f"U: {q}\nA: {a}")
    logger.info(f"NUOVA DOMANDA: {query}")

    recent_turns = "\n".join([f"Utente: {q}\nAssistente: {a}" for q, a in history[-2:]])
    full_query = f"Conversazione fino a ora:\n{recent_turns}\nUtente: {query}" if recent_turns else query

    query_embedding = client.embeddings.create(
        input=[full_query],
        model="text-embedding-ada-002"
    ).data[0].embedding

    query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    results = search_faiss(faiss_index, texts, metadata, query_vector, top_k=5)
    valid_chunks = [r for r in results if len(r["text"].strip()) >= 30]

    if not valid_chunks:
        logger.warning(f"[FUORI AMBITO] Domanda: {query}")
        _log_interaction(query, 0.0, True)
        return Response(
            "Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.\n\n"
            "Non trovi quello che stai cercando? Contattaci qui: [link placeholder]",
            mimetype="text/plain"
        )

    logger.info("Chunk utilizzati per la domanda: %s", query)
    for idx, chunk in enumerate(valid_chunks, start=1):
        logger.info("Chunk %d:\n%s\n", idx, chunk["text"])

    context = "\n---\n".join([r["text"] for r in valid_chunks])

    system_prompt = (
        "Sei un assistente specializzato nel fornire informazioni affidabili e dettagliate sulle orchidee. "
        "Rispondi solo se trovi informazioni precise e complete nei documenti forniti nel contesto. "
        "Se la risposta non è chiaramente e completamente supportata dai documenti, rispondi esclusivamente: 'Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.' "
        "Non inventare, non dedurre, non usare conoscenze esterne, non fornire spiegazioni aggiuntive, non rispondere in modo generico o approssimativo. "
        "Usa solo ed esclusivamente le informazioni presenti nei documenti forniti. Se la domanda non è coperta, rispondi solo con la frase indicata, senza aggiungere altro. "
        "Non usare tag HTML o attributi nei link. Se devi citare un'immagine, scrivi solo il link come testo. "
        "Rispondi solo a domande relative a tipi di orchidee, cura, coltivazione, parassiti, potatura e ambienti ideali. "
        "Non rispondere a domande personali, generiche, commerciali o che non riguardino direttamente le orchidee. "
        "Se nei documenti è presente un'immagine o un link a un'immagine correlata alla domanda, cita esplicitamente l'immagine e inseriscila nella risposta. \n\n"
        f"Contesto:\n{context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for q, a in history[-2:]:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": query})

    @stream_with_context
    def generate():
        accumulated = ""
        fallback_detected = False

        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                accumulated += delta
                yield delta

        overlap_score = calculate_overlap(accumulated, valid_chunks)
        logger.info(f"Overlap con i chunk: {overlap_score}%%")
        yield f"\n\n[overlap:{overlap_score}]"

        if "non sono in grado di rispondere" in accumulated.lower():
            fallback_detected = True
            yield "\n\nNon trovi quello che stai cercando? Contattaci qui: [link placeholder]"

        history.append((query, accumulated))
        session["history"] = history[-6:]
        _log_interaction(query, overlap_score, fallback_detected)

    return Response(generate(), mimetype="text/plain")


def _log_interaction(query, overlap, fallback):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "overlap": overlap,
        "fallback": fallback
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data) + "\n")

from routes.admin import admin_bp
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)