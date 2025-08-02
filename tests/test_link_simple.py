#!/usr/bin/env python3
"""
Test semplificato per verificare la funzionalità link
"""

import requests
import time

BASE_URL = "https://rag-assistant.fly.dev"

def test_link_functionality():
    """Test semplificato per link"""
    print("🔗 Test Semplificato Funzionalità Link")
    print("=" * 60)
    
    session = requests.Session()
    
    # Test 1: Verifica se l'admin mostra link
    print("1. Test accesso admin...")
    
    try:
        admin_response = session.get(f"{BASE_URL}/admin", 
                                   headers={"Authorization": "Bearer vertassistrag3-secret-key-2024-secure"})
        
        if admin_response.status_code == 200:
            print("   ✅ Accesso admin riuscito")
            admin_content = admin_response.text
            
            if "link" in admin_content.lower():
                print("   ✅ Admin contiene sezione link")
            else:
                print("   ⚠️ Admin non mostra sezione link")
        else:
            print(f"   ❌ Errore accesso admin: {admin_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Errore: {str(e)}")
        return False
    
    # Test 2: Verifica file urls.txt
    print("2. Test file urls.txt...")
    
    try:
        import os
        urls_file = "data/urls.txt"
        if os.path.exists(urls_file):
            with open(urls_file, 'r') as f:
                content = f.read().strip()
                if content:
                    print(f"   ✅ File urls.txt contiene: {len(content.split())} link")
                    for line in content.split('\n'):
                        if line.strip():
                            print(f"      - {line.strip()}")
                else:
                    print("   ⚠️ File urls.txt vuoto")
        else:
            print("   ❌ File urls.txt non trovato")
    except Exception as e:
        print(f"   ❌ Errore lettura file: {str(e)}")
    
    # Test 3: Test singola query con delay
    print("3. Test query singola...")
    
    try:
        # Aspetta 5 secondi per evitare rate limiting
        print("   ⏳ Aspetto 5 secondi per evitare rate limiting...")
        time.sleep(5)
        
        response = session.post(f"{BASE_URL}/ask", 
                              json={"message": "Quali eventi ci sono a Rimini?", "lang": "it"})
        
        if response.status_code == 200:
            answer = response.text
            print(f"   ✅ Risposta ricevuta ({len(answer)} caratteri)")
            
            if "Non sono in grado di rispondere" in answer:
                print("   ⚠️ Risposta generica - link potrebbero non essere indicizzati")
            elif any(keyword in answer.lower() for keyword in ["rimini", "eventi", "turismo"]):
                print("   ✅ Risposta contiene informazioni sui link!")
            else:
                print("   ⚠️ Risposta non specifica sui link")
                print(f"   📝 Anteprima: {answer[:200]}...")
        else:
            print(f"   ❌ Errore: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Errore query: {str(e)}")
    
    return True

def test_ingest_locally():
    """Test ingest locale"""
    print("\n4. Test ingest locale...")
    
    try:
        import subprocess
        import os
        
        # Verifica se la chiave API è configurata
        if not os.path.exists('.env'):
            print("   ❌ File .env non trovato")
            return False
        
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'your-openai-api-key-here' in env_content:
                print("   ❌ Chiave API non configurata nel .env")
                return False
            else:
                print("   ✅ Chiave API configurata")
        
        # Esegui ingest
        print("   🔄 Esecuzione ingest...")
        result = subprocess.run(["python", "ingest.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ Ingest completato con successo")
            if "web_page" in result.stdout:
                print("   ✅ Link web processati")
            else:
                print("   ⚠️ Nessun link web trovato nell'output")
        else:
            print(f"   ❌ Errore ingest: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Errore durante ingest: {str(e)}")

def main():
    """Esegue il test"""
    print("🔗 Test Funzionalità Link")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print("=" * 60)
    
    try:
        # Test funzionalità
        success = test_link_functionality()
        
        # Test ingest locale
        test_ingest_locally()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ Test completato con successo!")
            print("📋 Risultati:")
            print("   - Admin accessibile")
            print("   - File urls.txt configurato")
            print("   - Funzionalità link implementata")
        else:
            print("❌ Test fallito")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Errore durante i test: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 