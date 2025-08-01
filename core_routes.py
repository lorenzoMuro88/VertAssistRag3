from flask import Blueprint, request, Response, render_template, session, redirect, url_for, stream_with_context
from openai import OpenAI
import numpy as np
import os
import logging
import json
from datetime import datetime
from rag.vectorstore import load_faiss_index, search_faiss
from utils import calculate_overlap, log_interaction, load_env, get_model

core_bp = Blueprint("core", __name__)

# Caricamento ambiente e modello
load_env()
client = OpenAI()
MODEL = get_model()

# Carica l'indice FAISS dalla directory dell'applicazione
faiss_index, texts, metadata = load_faiss_index("rag/index.faiss")

@core_bp.route("/")
def home():
    if not session.get("authenticated") or session.get("role") != "user":
        return redirect(url_for("auth.login"))
    return render_template("index.html")

@core_bp.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return redirect(url_for("core.home"))

@core_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("message", "").strip()
    if not query:
        return Response("Messaggio vuoto", status=400, mimetype="text/plain")

    history = session.get("history", [])
    recent_turns = "\n".join([f"Utente: {q}\nAssistente: {a}" for q, a in history[-2:]])
    full_query = f"Conversazione fino a ora:\n{recent_turns}\nUtente: {query}" if recent_turns else query

    query_embedding = client.embeddings.create(
        input=[full_query],
        model="text-embedding-ada-002"
    ).data[0].embedding
    query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    results = search_faiss(faiss_index, texts, metadata, query_vector, top_k=int(os.getenv("TOP_K", 5)))
    valid_chunks = [r for r in results if len(r["text"].strip()) >= 30]

    if not valid_chunks:
        logging.warning(f"[FUORI AMBITO] Domanda: {query}")
        log_interaction(query, 0.0, True)
        return Response(
            "Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.\n\n"
            "Non trovi quello che stai cercando? Contattaci qui: [link placeholder]",
            mimetype="text/plain"
        )

    context = "\n---\n".join([r["text"] for r in valid_chunks])
    system_prompt = (
        "Sei un assistente specializzato nel fornire informazioni affidabili e dettagliate sulle orchidee. "
        "Non usare tag HTML o attributi nei link. Se devi citare un'immagine, scrivi solo il link come testo. "
        "Rispondi solo a domande relative a tipi di orchidee, cura, coltivazione, parassiti, potatura e ambienti ideali. "
        "Non rispondere a domande personali, generiche, commerciali o che non riguardino direttamente le orchidee. "
        "Se non hai informazioni sufficienti nel contesto, di' chiaramente: \"Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili.\" "
        "Non inventare. Non usare conoscenze esterne. Se nei documenti è presente un'immagine o un link a un'immagine correlata alla domanda, cita esplicitamente l'immagine.\n\n"
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
        MIN_OVERLAP = float(os.getenv("MIN_OVERLAP", 0))

        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                accumulated += delta

        overlap_score = calculate_overlap(accumulated, valid_chunks)
        logging.info(f"Overlap con i chunk: {overlap_score}%%")

        if overlap_score < MIN_OVERLAP:
            logging.warning(f"Overlap troppo basso: {overlap_score} < {MIN_OVERLAP}")
            log_interaction(query, overlap_score, True)
            yield "Non sono in grado di rispondere a questa domanda in base alle informazioni disponibili."
            return

        log_interaction(query, overlap_score, False)

        for line in accumulated.splitlines():
            yield line + "\n"
        yield f"\n\n[overlap:{overlap_score}]"

        if "non sono in grado di rispondere" in accumulated.lower():
            yield "\n\n Prova a formulare la domanda diversamente"

        history.append((query, accumulated))
        session["history"] = history[-6:]

    return Response(generate(), mimetype="text/plain")