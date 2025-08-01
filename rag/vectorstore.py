import faiss
import pickle
import numpy as np

def save_faiss_index(embeddings, texts, metadata, path):
    """
    Salva un indice FAISS con embeddings e metadati associati.
    """
    embeddings = np.array(embeddings, dtype=np.float32)
    dim = embeddings.shape[1]

    # Crea l'indice vettoriale FAISS
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Salva l'indice binario
    faiss.write_index(index, path)

    # Salva i metadati e i testi in formato pickle
    with open(path + ".meta.pkl", "wb") as f:
        pickle.dump({"texts": texts, "metadata": metadata}, f)

def load_faiss_index(index_path):
    """
    Carica un indice FAISS e i relativi metadati associati.
    """
    index = faiss.read_index(index_path)
    with open(index_path + ".meta.pkl", "rb") as f:
        meta = pickle.load(f)
    return index, meta["texts"], meta["metadata"]

def search_faiss(index, texts, metadata, query_vector, top_k=5):
    """
    Esegue una ricerca semantica nell'indice FAISS.
    """
    D, I = index.search(query_vector, top_k)
    results = []
    for i in I[0]:
        results.append({
            "text": texts[i],
            "meta": metadata[i]
        })
    return results 