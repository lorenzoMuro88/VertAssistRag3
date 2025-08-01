import os
import json
import logging
import re
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione ambiente
load_dotenv()
client = OpenAI()
MODEL = "gpt-4o"
DOCUMENTS_FOLDER = "data/documents"
OUTPUT_PATH = os.path.join(DOCUMENTS_FOLDER, "metadata.json")


def extract_text_from_file(filepath):
    try:
        if filepath.endswith(".txt") or filepath.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif filepath.endswith(".pdf"):
            reader = PdfReader(filepath)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        logger.warning(f"Impossibile leggere {filepath}: {e}")
    return ""


def get_relative_path(filepath):
    return os.path.relpath(filepath, DOCUMENTS_FOLDER).replace("\\", "/")


def extract_json_from_response(text):
    try:
        if text.strip().startswith("{"):
            return json.loads(text)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        logger.debug(f"Parsing JSON fallito. Risposta:\n{text}")
        raise e
    return None


def generate_metadata(text):
    prompt = (
        "Leggi il seguente testo e genera:\n"
        "1. Una breve descrizione (max 30 parole).\n"
        "2. Una lista di massimo 5 tag tematici.\n"
        'Rispondi solo in questo formato JSON: {"description": "...", "tags": ["...", "..."]}\n\n'
        f"Testo:\n{text[:2000]}"
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        if content is not None:
            content = content.strip()
        else:
            logger.error("La risposta di OpenAI non contiene contenuto.")
            return None
        logger.debug(f"🔍 Risposta per debug:\n{content}")
        return extract_json_from_response(content)
    except Exception as e:
        logger.error(f"Errore durante la generazione metadati: {e}")
        return None


def scan_and_generate_metadata():
    metadata = {}
    count = 0
    for root, _, files in os.walk(DOCUMENTS_FOLDER):
        for file in files:
            if not file.lower().endswith((".txt", ".md", ".pdf")):
                continue
            path = os.path.join(root, file)
            rel_path = get_relative_path(path)
            logger.info(f"Elaborazione: {rel_path}")
            text = extract_text_from_file(path)
            if not text.strip():
                continue
            meta = generate_metadata(text)
            if meta:
                metadata[rel_path] = meta
                count += 1
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Metadati generati per {count} documenti in {OUTPUT_PATH}")


if __name__ == "__main__":
    scan_and_generate_metadata()