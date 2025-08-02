import os
import re
import json
from datetime import datetime
from flask import current_app
from typing import List, Dict, Tuple
import numpy as np

def calculate_overlap(response, chunks):
    """Calcolo overlap base con token matching"""
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

def calculate_semantic_overlap(response, chunks):
    """Calcolo overlap semantico più sofisticato"""
    def extract_key_phrases(text):
        # Estrae frasi chiave (sostantivi, aggettivi, verbi principali)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filtra parole comuni
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    resp_phrases = extract_key_phrases(response)
    chunk_phrases = []
    for chunk in chunks:
        chunk_phrases.extend(extract_key_phrases(chunk["text"]))
    
    if not resp_phrases:
        return 0.0
    
    # Calcola overlap semantico
    chunk_phrase_set = set(chunk_phrases)
    semantic_overlap = len(set(resp_phrases) & chunk_phrase_set) / len(set(resp_phrases))
    return round(semantic_overlap * 100, 2)

def calculate_content_quality_score(response, chunks):
    """Calcola un punteggio di qualità del contenuto"""
    score = 0.0
    
    # 1. Lunghezza della risposta (0-20 punti)
    if len(response) > 50:
        score += 20
    elif len(response) > 20:
        score += 10
    
    # 2. Presenza di informazioni specifiche (0-30 punti)
    specific_indicators = ['perché', 'come', 'quando', 'dove', 'quale', 'quali', 'specifico', 'esempio']
    specific_count = sum(1 for indicator in specific_indicators if indicator in response.lower())
    score += min(30, specific_count * 5)
    
    # 3. Coerenza con i chunk (0-30 punti)
    semantic_overlap = calculate_semantic_overlap(response, chunks)
    score += (semantic_overlap / 100) * 30
    
    # 4. Assenza di frasi generiche (0-20 punti)
    generic_phrases = ['non so', 'non ho informazioni', 'non posso aiutarti', 'non ho dati']
    generic_count = sum(1 for phrase in generic_phrases if phrase in response.lower())
    score += max(0, 20 - generic_count * 5)
    
    return round(score, 2)

def adaptive_quality_threshold(query_type, response_length):
    """Soglia adattiva basata sul tipo di query e lunghezza risposta"""
    base_threshold = 0.3  # 30% base
    
    # Aggiusta per tipo di query
    if any(word in query_type.lower() for word in ['specifico', 'dettagliato', 'completo']):
        base_threshold += 0.2
    elif any(word in query_type.lower() for word in ['generale', 'breve', 'semplice']):
        base_threshold -= 0.1
    
    # Aggiusta per lunghezza risposta
    if response_length > 200:
        base_threshold -= 0.1  # Più permissivo per risposte lunghe
    elif response_length < 50:
        base_threshold += 0.1  # Più stringente per risposte brevi
    
    return max(0.1, min(0.8, base_threshold))  # Limita tra 10% e 80%

def classify_query_type(query):
    """Classifica il tipo di query per adattare la soglia"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['come', 'procedura', 'passo', 'istruzioni']):
        return 'procedurale'
    elif any(word in query_lower for word in ['cosa', 'che cosa', 'definizione', 'significato']):
        return 'definizione'
    elif any(word in query_lower for word in ['quando', 'tempo', 'periodo', 'stagione']):
        return 'temporale'
    elif any(word in query_lower for word in ['dove', 'luogo', 'posizione', 'ambiente']):
        return 'spaziale'
    elif any(word in query_lower for word in ['perché', 'motivo', 'causa', 'ragione']):
        return 'causale'
    else:
        return 'generale'

def enhanced_quality_check(response, chunks, query):
    """Controllo qualità avanzato con multiple metriche"""
    results = {
        'token_overlap': calculate_overlap(response, chunks),
        'semantic_overlap': calculate_semantic_overlap(response, chunks),
        'content_quality': calculate_content_quality_score(response, chunks),
        'query_type': classify_query_type(query),
        'response_length': len(response),
        'adaptive_threshold': adaptive_quality_threshold(classify_query_type(query), len(response))
    }
    
    # Calcola punteggio complessivo
    overall_score = (
        results['token_overlap'] * 0.3 +
        results['semantic_overlap'] * 0.4 +
        results['content_quality'] * 0.3
    ) / 100
    
    results['overall_score'] = round(overall_score * 100, 2)
    results['passes_threshold'] = overall_score >= results['adaptive_threshold']
    
    return results

def log_query(query, overlap, fallback=False):
    """Logga una query con il suo overlap."""
    try:
        log_path = current_app.config.get("LOG_PATH")
        if log_path:
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

def log_enhanced_query(query, quality_results, fallback=False):
    """Logga una query con risultati di qualità avanzati."""
    try:
        log_path = current_app.config.get("LOG_PATH")
        if log_path:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "quality_results": quality_results,
                    "fallback": fallback
                }
                f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Errore nel logging della query: {str(e)}")