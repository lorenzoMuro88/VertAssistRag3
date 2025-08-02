#!/usr/bin/env python3
"""
Script per testare il rispetto del contesto delle informazioni
"""

import requests
import json
import time

BASE_URL = "https://rag-assistant.fly.dev"

def test_context_compliance():
    """Testa se il sistema rispetta il contesto delle informazioni"""
    print("🔍 Test Rispetto Contesto Informazioni")
    print("=" * 50)
    
    # Test domande FUORI CONTESTO (dovrebbero essere rifiutate)
    out_of_context_tests = [
        {
            "query": "Come si cura un gatto?",
            "expected": "rifiuto",
            "description": "Domanda su animali domestici"
        },
        {
            "query": "Qual è la capitale della Francia?",
            "expected": "rifiuto", 
            "description": "Domanda di geografia generale"
        },
        {
            "query": "Come si cucina la pasta?",
            "expected": "rifiuto",
            "description": "Domanda di cucina"
        },
        {
            "query": "Qual è il tempo oggi?",
            "expected": "rifiuto",
            "description": "Domanda sul meteo"
        },
        {
            "query": "Come si programma in Python?",
            "expected": "rifiuto",
            "description": "Domanda di programmazione"
        }
    ]
    
    # Test domande NEL CONTESTO (dovrebbero essere accettate)
    in_context_tests = [
        {
            "query": "Qual è la password del WiFi?",
            "expected": "accettazione",
            "description": "Informazione WiFi House Boat"
        },
        {
            "query": "Come faccio il check-in?",
            "expected": "accettazione",
            "description": "Procedura check-in"
        },
        {
            "query": "Dove si trova il parcheggio?",
            "expected": "accettazione",
            "description": "Informazione parcheggio"
        },
        {
            "query": "Quali sono le regole della casa?",
            "expected": "accettazione",
            "description": "Regole house boat"
        },
        {
            "query": "Qual è il codice per la House Boat 5?",
            "expected": "accettazione",
            "description": "Codice keybox"
        }
    ]
    
    print("\n🚫 Test Domande FUORI CONTESTO")
    print("-" * 40)
    
    out_of_context_passed = 0
    for i, test in enumerate(out_of_context_tests, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Domanda: {test['query']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                headers={"Content-Type": "application/json"},
                json={"message": test['query']},
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Verifica se la risposta contiene il messaggio di rifiuto
                if "non sono in grado di rispondere" in content:
                    print("   ✅ RIFIUTATA correttamente")
                    out_of_context_passed += 1
                else:
                    print("   ❌ ACCETTATA (dovrebbe essere rifiutata)")
                    print(f"   Risposta: {response.text[:100]}...")
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    print(f"\n📊 Risultati FUORI CONTESTO: {out_of_context_passed}/{len(out_of_context_tests)}")
    
    print("\n✅ Test Domande NEL CONTESTO")
    print("-" * 40)
    
    in_context_passed = 0
    for i, test in enumerate(in_context_tests, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Domanda: {test['query']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                headers={"Content-Type": "application/json"},
                json={"message": test['query']},
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Verifica se la risposta contiene informazioni utili
                if "non sono in grado di rispondere" not in content and len(content) > 50:
                    print("   ✅ ACCETTATA correttamente")
                    print(f"   Risposta: {response.text[:100]}...")
                    in_context_passed += 1
                else:
                    print("   ❌ RIFIUTATA (dovrebbe essere accettata)")
                    print(f"   Risposta: {response.text[:100]}...")
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    print(f"\n📊 Risultati NEL CONTESTO: {in_context_passed}/{len(in_context_tests)}")
    
    # Calcola punteggio complessivo
    total_tests = len(out_of_context_tests) + len(in_context_tests)
    total_passed = out_of_context_passed + in_context_passed
    
    print(f"\n🏆 RISULTATO FINALE")
    print("=" * 30)
    print(f"✅ Test superati: {total_passed}/{total_tests}")
    print(f"❌ Test falliti: {total_tests - total_passed}/{total_tests}")
    print(f"📊 Percentuale successo: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 PERFETTO! Il sistema rispetta completamente il contesto!")
        return True
    elif total_passed >= total_tests * 0.8:
        print("\n✅ BUONO! Il sistema rispetta principalmente il contesto.")
        return True
    else:
        print("\n⚠️ ATTENZIONE! Il sistema non rispetta adeguatamente il contesto.")
        return False

def test_edge_cases():
    """Testa casi limite del controllo contesto"""
    print("\n🔬 Test Casi Limite")
    print("=" * 30)
    
    edge_cases = [
        {
            "query": "WiFi",
            "expected": "accettazione",
            "description": "Parola chiave semplice"
        },
        {
            "query": "House Boat",
            "expected": "accettazione", 
            "description": "Termine specifico"
        },
        {
            "query": "Ciao, come stai?",
            "expected": "rifiuto",
            "description": "Saluto generico"
        },
        {
            "query": "Grazie mille!",
            "expected": "rifiuto",
            "description": "Ringraziamento generico"
        },
        {
            "query": "Puoi aiutarmi?",
            "expected": "rifiuto",
            "description": "Richiesta generica di aiuto"
        }
    ]
    
    passed = 0
    for i, test in enumerate(edge_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Domanda: {test['query']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                headers={"Content-Type": "application/json"},
                json={"message": test['query']},
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text.lower()
                
                if test['expected'] == "accettazione":
                    if "non sono in grado di rispondere" not in content:
                        print("   ✅ ACCETTATA correttamente")
                        passed += 1
                    else:
                        print("   ❌ RIFIUTATA (dovrebbe essere accettata)")
                else:
                    if "non sono in grado di rispondere" in content:
                        print("   ✅ RIFIUTATA correttamente")
                        passed += 1
                    else:
                        print("   ❌ ACCETTATA (dovrebbe essere rifiutata)")
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    print(f"\n📊 Casi limite: {passed}/{len(edge_cases)}")
    return passed == len(edge_cases)

def main():
    """Test principale"""
    print("🧪 Test Rispetto Contesto VertAssistRag3")
    print("=" * 60)
    
    try:
        # Test principale
        main_result = test_context_compliance()
        
        # Test casi limite
        edge_result = test_edge_cases()
        
        print(f"\n🎯 CONCLUSIONE FINALE")
        print("=" * 30)
        
        if main_result and edge_result:
            print("✅ ECCELLENTE: Il sistema rispetta completamente il contesto!")
            print("✅ Tutti i test sono superati")
            print("✅ Il sistema è pronto per la produzione")
        elif main_result:
            print("✅ BUONO: Il sistema rispetta principalmente il contesto")
            print("⚠️ Alcuni casi limite potrebbero essere migliorati")
        else:
            print("❌ ATTENZIONE: Il sistema non rispetta adeguatamente il contesto")
            print("🔧 Sono necessari miglioramenti")
        
        return main_result and edge_result
        
    except requests.exceptions.ConnectionError:
        print("❌ Errore: Impossibile connettersi al server")
        print("   Assicurati che l'applicazione sia in esecuzione su Fly.io")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 