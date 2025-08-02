#!/usr/bin/env python3
"""
Script per testare la velocità dei diversi modelli OpenAI
"""

import time
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_model_speed(model_name, test_questions, base_url="http://localhost:8080"):
    """Testa la velocità di un modello specifico"""
    print(f"\n🧪 Testando {model_name}...")
    
    # Cambia il modello temporaneamente
    original_model = os.getenv("MODEL")
    os.environ["MODEL"] = model_name
    
    total_time = 0
    successful_requests = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"  Domanda {i}: {question[:50]}...")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers={"Content-Type": "application/json"},
                json={"message": question},
                timeout=30
            )
            
            if response.status_code == 200:
                elapsed = time.time() - start_time
                total_time += elapsed
                successful_requests += 1
                print(f"    ✅ {elapsed:.2f}s")
            else:
                print(f"    ❌ Errore HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Errore: {e}")
    
    # Ripristina il modello originale
    if original_model:
        os.environ["MODEL"] = original_model
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"\n📊 Risultati {model_name}:")
        print(f"   Tempo medio: {avg_time:.2f}s")
        print(f"   Richieste riuscite: {successful_requests}/{len(test_questions)}")
        return avg_time
    else:
        print(f"\n❌ Nessuna richiesta riuscita per {model_name}")
        return None

def main():
    """Test principale"""
    print("🚀 Test di Velocità Modelli OpenAI")
    print("=" * 50)
    
    # Domande di test
    test_questions = [
        "Qual è la password del WiFi?",
        "Come faccio il check-in?",
        "Qual è il codice per la House Boat 5?",
        "Quali sono le regole della casa?",
        "Dove si trova il parcheggio?"
    ]
    
    # Modelli da testare
    models = [
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-4"
    ]
    
    results = {}
    
    for model in models:
        avg_time = test_model_speed(model, test_questions)
        if avg_time:
            results[model] = avg_time
    
    # Confronto finale
    if results:
        print("\n🏆 CONFRONTO FINALE")
        print("=" * 30)
        
        # Ordina per velocità (più veloce prima)
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        
        for i, (model, time) in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"{medal} {model}: {time:.2f}s")
        
        fastest = sorted_results[0]
        slowest = sorted_results[-1]
        improvement = ((slowest[1] - fastest[1]) / slowest[1]) * 100
        
        print(f"\n⚡ Miglioramento: {fastest[0]} è {improvement:.1f}% più veloce di {slowest[0]}")
    
    print("\n✅ Test completato!")

if __name__ == "__main__":
    main() 