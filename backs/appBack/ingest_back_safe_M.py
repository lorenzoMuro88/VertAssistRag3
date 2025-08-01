import os
import glob
import logging
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
from rag.vectorstore import save_faiss_index
import numpy as np
import tiktoken
import json

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione ambiente
load_dotenv()
client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
INDEX_PATH = "rag/index.faiss"  # Indice nella directory dell'app
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
IS_PRODUCTION = os.getenv("FLASK_ENV") != "development"
BASE_DIR = "/data" if IS_PRODUCTION else "data"
CHUNK_LOG = os.path.join(BASE_DIR, "documents", "chunks.jsonl")


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), size - overlap):
        chunk = tokens[i:i + size]
        chunks.append(encoding.decode(chunk))
    return chunks


def load_txt_files(folder: str):
    texts = []
    for filepath in glob.glob(os.path.join(folder, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            texts.append((f.read(), {
                "source": os.path.basename(filepath),
                "format": "txt"
            }))
    return texts


def load_md_files(folder: str):
    texts = []
    for filepath in glob.glob(os.path.join(folder, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            texts.append((f.read(), {
                "source": os.path.basename(filepath),
                "format": "md"
            }))
    return texts


def load_pdf_files(folder: str):
    texts = []
    for filepath in glob.glob(os.path.join(folder, "*.pdf")):
        reader = PdfReader(filepath)
        content = "\n".join([page.extract_text() or "" for page in reader.pages])
        texts.append((content, {
            "source": os.path.basename(filepath),
            "format": "pdf"
        }))
    return texts


def load_web_pages(urls: list):
    texts = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            body = soup.get_text()
            texts.append((body, {
                "source": url,
                "format": "html"
            }))
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


if __name__ == "__main__":
    logger.info("Caricamento dei documenti...")
    texts = load_txt_files("documents") + load_md_files("documents") + load_pdf_files("documents")

    urls = [
        "https://it.wikipedia.org/wiki/Orchidee",
        "https://www.starbene.it/benessere/orchidee-segreti-coltivarle-tutte-stagioni"
    ]
    texts += load_web_pages(urls)

    logger.info(f"Documenti totali: {len(texts)}")

    chunks = []
    metadata = []
    for doc_id, (text, meta) in enumerate(texts):
        c = chunk_text(text)
        chunks.extend(c)
        metadata.extend([{**meta, "chunk_id": i} for i in range(len(c))])

    logger.info(f"Totale chunk generati: {len(chunks)}")

    vectors = embed_chunks(chunks)
    save_faiss_index(vectors, chunks, metadata, INDEX_PATH)

    logger.info("Salvataggio completato in FAISS.")

    with open(CHUNK_LOG, "w", encoding="utf-8") as out:
        for chunk, meta in zip(chunks, metadata):
            out.write(json.dumps({
                "text": chunk,
                "metadata": meta
            }) + "\n")
    print(f"✅ Salvati {len(chunks)} chunk in {CHUNK_LOG}")