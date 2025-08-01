import os
import glob
import json
import logging
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
from rag.vectorstore import save_faiss_index
import numpy as np
import tiktoken

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione ambiente
load_dotenv()
client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
INDEX_PATH = "rag/index.faiss"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
IS_PRODUCTION = os.getenv("FLASK_ENV") != "development"
BASE_DIR = "/data" if IS_PRODUCTION else "data"
CHUNK_LOG = os.path.join(BASE_DIR, "documents", "chunks.jsonl")
METADATA_PATH = "data/documents/metadata.json"


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), size - overlap):
        chunk = tokens[i:i + size]
        chunks.append(encoding.decode(chunk))
    return chunks


def load_txt_files(folder: str):
    return _load_generic_files(folder, "*.txt")


def load_md_files(folder: str):
    return _load_generic_files(folder, "*.md")


def load_pdf_files(folder: str):
    texts = []
    for filepath in glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True):
        try:
            reader = PdfReader(filepath)
            content = "\n".join([page.extract_text() or "" for page in reader.pages])
            relpath = os.path.relpath(filepath, folder).replace("\\", "/")
            texts.append((relpath, content))
        except Exception as e:
            logger.warning(f"Errore durante la lettura PDF {filepath}: {e}")
    return texts


def _load_generic_files(folder: str, pattern: str):
    texts = []
    for filepath in glob.glob(os.path.join(folder, "**", pattern), recursive=True):
        relpath = os.path.relpath(filepath, folder).replace("\\", "/")
        with open(filepath, "r", encoding="utf-8") as f:
            texts.append((relpath, f.read()))
    return texts


def load_web_pages(urls: list):
    texts = []
    for idx, url in enumerate(urls):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            body = soup.get_text()
            texts.append((f"web_page_{idx}", body))
        except Exception as e:
            logger.warning(f"Errore durante lo scraping di {url}: {e}")
    return texts


def embed_chunks(chunks):
    embeddings = []
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        result = client.embeddings.create(input=batch, model=EMBEDDING_MODEL)
        vectors = [np.array(record.embedding, dtype=np.float32) for record in result.data]
        embeddings.extend(vectors)
    return embeddings


def load_metadata(metadata_path):
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


if __name__ == "__main__":
    logger.info("📥 Caricamento documenti da cartella e web...")

    texts = (
        load_txt_files("data/documents") +
        load_md_files("data/documents") +
        load_pdf_files("data/documents")
    )

    urls = [
        "https://www.visitrimini.com/en/events/"
    ]
    texts += load_web_pages(urls)

    logger.info(f"📄 Documenti totali trovati: {len(texts)}")

    metadata_index = load_metadata(METADATA_PATH)

    chunks = []
    metadata = []

    for relpath, content in texts:
        logger.info(f"Elaborazione: {relpath}")
        doc_chunks = chunk_text(content)
        chunks.extend(doc_chunks)

        meta_entry = metadata_index.get(relpath, {})
        meta_base = {
            "source": relpath,
            "description": meta_entry.get("description", ""),
            "tags": meta_entry.get("tags", [])
        }
        metadata.extend([meta_base] * len(doc_chunks))

    logger.info(f"✂️ Totale chunk generati: {len(chunks)}")

    vectors = embed_chunks(chunks)
    save_faiss_index(vectors, chunks, metadata, INDEX_PATH)

    logger.info("💾 Indicizzazione completata e salvata in FAISS.")

    with open(CHUNK_LOG, "w", encoding="utf-8") as out:
        for chunk, meta in zip(chunks, metadata):
            out.write(json.dumps({
                "text": chunk,
                "source": meta.get("source"),
                "description": meta.get("description"),
                "tags": meta.get("tags")
            }) + "\n")

    print(f"✅ Salvati {len(chunks)} chunk in {CHUNK_LOG}")