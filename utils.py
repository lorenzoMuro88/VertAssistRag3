import os
import re
import json
from datetime import datetime
from flask import current_app

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

def log_query(query, overlap, fallback=False):
    """Logga una query con il suo overlap."""
    try:
        log_path = current_app.config.get("LOG_PATH")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "overlap": overlap,
                "fallback": fallback
            }
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Errore nel logging della query: {str(e)}")