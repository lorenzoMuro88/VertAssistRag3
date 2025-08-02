import threading
from typing import Optional, Tuple, List, Dict, Any
import faiss
import numpy as np
from .vectorstore import load_faiss_index

class FAISSIndexSingleton:
    """Singleton per gestire l'indice FAISS in modo thread-safe"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._index = None
            self._texts = []
            self._metadata = []
            self._initialized = True
    
    def load_index(self, index_path: str) -> bool:
        """Carica l'indice FAISS"""
        try:
            self._index, self._texts, self._metadata = load_faiss_index(index_path)
            return True
        except Exception as e:
            print(f"Errore nel caricamento dell'indice: {e}")
            return False
    
    def get_index(self) -> Optional[faiss.Index]:
        """Restituisce l'indice FAISS"""
        return self._index
    
    def get_texts(self) -> List[str]:
        """Restituisce i testi"""
        return self._texts
    
    def get_metadata(self) -> List[Dict[str, Any]]:
        """Restituisce i metadati"""
        return self._metadata
    
    def is_loaded(self) -> bool:
        """Verifica se l'indice è caricato"""
        return self._index is not None and len(self._texts) > 0
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Esegue una ricerca nell'indice"""
        if not self.is_loaded():
            return []
        
        try:
            if self._index is not None:
                D, I = self._index.search(query_vector, top_k)
                results = []
                for i in I[0]:
                    if i < len(self._texts):
                        results.append({
                            "text": self._texts[i],
                            "meta": self._metadata[i] if i < len(self._metadata) else {}
                        })
                return results
            return []
        except Exception as e:
            print(f"Errore nella ricerca: {e}")
            return []

# Istanza globale
faiss_singleton = FAISSIndexSingleton() 