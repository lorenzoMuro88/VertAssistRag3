#!/usr/bin/env python3
"""
Test per verificare le migliorie al sistema keybox
Testa varianti naturali del linguaggio per i codici keybox
"""

import requests
import json
import time

BASE_URL = "https://rag-assistant.fly.dev"

def test_keybox_variants():
    """Test varianti naturali per richieste keybox"""
    print("🔑 Test Migliorie Sistema Keybox")
    print("=" * 60)
    
    # Test cases con varianti naturali
    test_cases = [
        {
            "category": "Varianti Base",
            "tests": [
                "Qual è il codice della stanza Hb 3?",
                "Qual è il codice della camera Hb 5?",
                "Qual è il codice della houseboat Hb 7?",
                "Qual è il codice keybox per Hb 8?",
                "Qual è la chiave della stanza Hb 9?",
                "Qual è l'accesso alla stanza Hb 11?"
            ]
        },
        {
            "category": "Varianti con Preposizioni",
            "tests": [
                "Codice per la stanza Hb 3",
                "Codice per la camera Hb 5",
                "Codice per la houseboat Hb 7",
                "Chiave per la stanza Hb 8",
                "Accesso per la stanza Hb 9"
            ]
        },
        {
            "category": "Varianti Senza Hb",
            "tests": [
                "Qual è il codice della stanza 3?",
                "Qual è il codice della camera 5?",
                "Qual è il codice della houseboat 7?",
                "Qual è la chiave della stanza 8?"
            ]
        },
        {
            "category": "Varianti Generiche",
            "tests": [
                "Codice stanza Hb 3",
                "Codice camera Hb 5",
                "Codice houseboat Hb 7",
                "Chiave stanza Hb 8",
                "Accesso stanza Hb 9"
            ]
        }
    ]
    
    session = requests.Session()
    results = {
        "success": 0,
        "total": 0,
        "details": []
    }
    
    for category in test_cases:
        print(f"\n📋 {category['category']}")
        print("-" * 40)
        
        for test_query in category['tests']:
            print(f"Test: {test_query}")
            
            try:
                response = session.post(f"{BASE_URL}/ask", 
                                     json={"message": test_query, "lang": "it"})
                
                if response.status_code == 200:
                    answer = response.text
                    
                    # Verifica se la risposta contiene un codice keybox
                    if any(code in answer for code in ['*03#', '*05#', '*06#', '*08#', '*09#', '*19#']):
                        print(f"   ✅ SUCCESSO: Risposta contiene codice keybox")
                        results["success"] += 1
                        results["details"].append({
                            "query": test_query,
                            "status": "success",
                            "answer": answer[:100] + "..."
                        })
                    elif "Non sono in grado di rispondere" in answer:
                        print(f"   ❌ FALLIMENTO: Risposta generica")
                        results["details"].append({
                            "query": test_query,
                            "status": "failure",
                            "answer": answer[:100] + "..."
                        })
                    else:
                        print(f"   ⚠️ PARZIALE: Risposta non contiene codice")
                        results["details"].append({
                            "query": test_query,
                            "status": "partial",
                            "answer": answer[:100] + "..."
                        })
                else:
                    print(f"   ❌ ERRORE: Status {response.status_code}")
                    results["details"].append({
                        "query": test_query,
                        "status": "error",
                        "answer": f"HTTP {response.status_code}"
                    })
                
                results["total"] += 1
                time.sleep(1)  # Pausa tra le richieste
                
            except Exception as e:
                print(f"   ❌ ECCEZIONE: {str(e)}")
                results["details"].append({
                    "query": test_query,
                    "status": "exception",
                    "answer": str(e)
                })
                results["total"] += 1
    
    return results

def test_specific_keybox_queries():
    """Test specifici per ogni codice keybox"""
    print("\n🎯 Test Specifici per Codici Keybox")
    print("=" * 60)
    
    test_cases = [
        ("Hb 3", "*03#"),
        ("Hb 5", "*05#"),
        ("Hb 7", "*06#"),
        ("Hb 8", "*08#"),
        ("Hb 9", "*09#"),
        ("Hb 11", "*19#")
    ]
    
    session = requests.Session()
    results = {
        "correct": 0,
        "total": 0,
        "details": []
    }
    
    for room, expected_code in test_cases:
        print(f"\n🏠 Test stanza {room} (codice atteso: {expected_code})")
        
        # Test con varianti
        variants = [
            f"Qual è il codice della stanza {room}?",
            f"Qual è il codice della camera {room}?",
            f"Qual è il codice della houseboat {room}?",
            f"Codice stanza {room}",
            f"Chiave stanza {room}"
        ]
        
        for variant in variants:
            print(f"  Test: {variant}")
            
            try:
                response = session.post(f"{BASE_URL}/ask", 
                                     json={"message": variant, "lang": "it"})
                
                if response.status_code == 200:
                    answer = response.text
                    
                    if expected_code in answer:
                        print(f"    ✅ CORRETTO: Trovato {expected_code}")
                        results["correct"] += 1
                    elif "Non sono in grado di rispondere" in answer:
                        print(f"    ❌ FALLIMENTO: Risposta generica")
                    else:
                        print(f"    ⚠️ PARZIALE: Risposta non contiene {expected_code}")
                    
                    results["details"].append({
                        "room": room,
                        "variant": variant,
                        "expected": expected_code,
                        "found": expected_code in answer,
                        "answer": answer[:100] + "..."
                    })
                else:
                    print(f"    ❌ ERRORE: Status {response.status_code}")
                    results["details"].append({
                        "room": room,
                        "variant": variant,
                        "expected": expected_code,
                        "found": False,
                        "answer": f"HTTP {response.status_code}"
                    })
                
                results["total"] += 1
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ ECCEZIONE: {str(e)}")
                results["details"].append({
                    "room": room,
                    "variant": variant,
                    "expected": expected_code,
                    "found": False,
                    "answer": str(e)
                })
                results["total"] += 1
    
    return results

def analyze_results(variants_results, specific_results):
    """Analizza i risultati dei test"""
    print("\n📊 Analisi Risultati")
    print("=" * 60)
    
    # Statistiche varianti
    variants_success_rate = (variants_results["success"] / variants_results["total"]) * 100 if variants_results["total"] > 0 else 0
    print(f"🎯 Varianti Naturali: {variants_success_rate:.1f}% successo ({variants_results['success']}/{variants_results['total']})")
    
    # Statistiche specifiche
    specific_success_rate = (specific_results["correct"] / specific_results["total"]) * 100 if specific_results["total"] > 0 else 0
    print(f"🎯 Codici Specifici: {specific_success_rate:.1f}% successo ({specific_results['correct']}/{specific_results['total']})")
    
    # Analisi dettagliata
    print(f"\n📋 Dettagli Varianti:")
    for detail in variants_results["details"]:
        status_icon = "✅" if detail["status"] == "success" else "❌" if detail["status"] == "failure" else "⚠️"
        print(f"  {status_icon} {detail['query']}")
    
    print(f"\n📋 Dettagli Specifici:")
    for detail in specific_results["details"]:
        status_icon = "✅" if detail["found"] else "❌"
        print(f"  {status_icon} {detail['room']} - {detail['variant']}")

def main():
    """Esegue tutti i test"""
    print("🔑 Test Migliorie Sistema Keybox")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print("=" * 60)
    
    try:
        # Test varianti naturali
        variants_results = test_keybox_variants()
        
        # Test specifici per codici
        specific_results = test_specific_keybox_queries()
        
        # Analisi risultati
        analyze_results(variants_results, specific_results)
        
        print("\n" + "=" * 60)
        overall_success = variants_results["success"] + specific_results["correct"]
        overall_total = variants_results["total"] + specific_results["total"]
        overall_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0
        
        print(f"🎉 RISULTATO FINALE: {overall_rate:.1f}% successo ({overall_success}/{overall_total})")
        
        if overall_rate >= 70:
            print("✅ Le migliorie al sistema keybox sono efficaci!")
        elif overall_rate >= 50:
            print("⚠️ Le migliorie hanno effetto parziale, ulteriori ottimizzazioni necessarie")
        else:
            print("❌ Le migliorie non sono sufficienti, necessarie ulteriori modifiche")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Errore durante i test: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 