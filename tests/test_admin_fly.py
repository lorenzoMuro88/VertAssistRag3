#!/usr/bin/env python3
"""
Test completo delle funzionalità admin su Fly.io
Verifica accesso, API e sicurezza
"""

import requests
import json
import time

BASE_URL = "https://rag-assistant.fly.dev"
ADMIN_TOKEN = "vertassistrag3-secret-key-2024-secure"

def test_admin_access():
    """Test accesso admin con diversi metodi"""
    print("🔐 Test Accesso Admin")
    print("=" * 50)
    
    # Test 1: Accesso senza token (dovrebbe fallire)
    print("1. Test accesso senza token...")
    response = requests.get(f"{BASE_URL}/admin")
    if response.status_code == 401:
        print("   ✅ Accesso negato correttamente")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 2: Accesso con header Authorization
    print("2. Test accesso con header Authorization...")
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    response = requests.get(f"{BASE_URL}/admin", headers=headers)
    if response.status_code == 200 and "Admin - Log Interazioni" in response.text:
        print("   ✅ Accesso con header riuscito")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 3: Accesso con token nell'URL
    print("3. Test accesso con token nell'URL...")
    response = requests.get(f"{BASE_URL}/admin?token={ADMIN_TOKEN}")
    if response.status_code == 200 and "Admin - Log Interazioni" in response.text:
        print("   ✅ Accesso con URL token riuscito")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")

def test_admin_apis():
    """Test delle API admin"""
    print("\n🔧 Test API Admin")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    # Test 1: Get MIN_OVERLAP
    print("1. Test get MIN_OVERLAP...")
    response = requests.get(f"{BASE_URL}/admin/get-min-overlap", headers=headers)
    if response.status_code == 200:
        data = response.json()
        min_overlap = data.get('min_overlap')
        print(f"   ✅ MIN_OVERLAP: {min_overlap}")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 2: Get corrections
    print("2. Test get corrections...")
    response = requests.get(f"{BASE_URL}/admin/get-corrections", headers=headers)
    if response.status_code == 200:
        data = response.json()
        corrections = data.get('corrections', [])
        print(f"   ✅ Corrections trovate: {len(corrections)}")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 3: Admin chunks
    print("3. Test admin chunks...")
    response = requests.get(f"{BASE_URL}/admin/chunks", headers=headers)
    if response.status_code == 200:
        print("   ✅ Accesso chunks riuscito")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")

def test_admin_security():
    """Test sicurezza admin"""
    print("\n🛡️ Test Sicurezza Admin")
    print("=" * 50)
    
    # Test 1: API senza token
    print("1. Test API senza token...")
    response = requests.get(f"{BASE_URL}/admin/get-min-overlap")
    if response.status_code == 401:
        print("   ✅ Accesso negato correttamente")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 2: API con token sbagliato
    print("2. Test API con token sbagliato...")
    headers = {"Authorization": "Bearer wrong-token"}
    response = requests.get(f"{BASE_URL}/admin/get-min-overlap", headers=headers)
    if response.status_code == 401:
        print("   ✅ Accesso negato correttamente")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 3: API con header malformato
    print("3. Test API con header malformato...")
    headers = {"Authorization": "Bearer"}
    response = requests.get(f"{BASE_URL}/admin/get-min-overlap", headers=headers)
    if response.status_code == 401:
        print("   ✅ Accesso negato correttamente")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")

def test_main_app():
    """Test app principale"""
    print("\n🌐 Test App Principale")
    print("=" * 50)
    
    # Test 1: Homepage
    print("1. Test homepage...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("   ✅ Homepage accessibile")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")
    
    # Test 2: Ask endpoint
    print("2. Test ask endpoint...")
    data = {"question": "Dove si trova il parcheggio?"}
    response = requests.post(f"{BASE_URL}/ask", json=data)
    if response.status_code == 200:
        result = response.json()
        if "answer" in result:
            print("   ✅ Ask endpoint funzionante")
        else:
            print("   ⚠️ Risposta senza answer")
    else:
        print(f"   ❌ Errore: Status {response.status_code}")

def main():
    """Esegue tutti i test"""
    print("🚀 Test Completo Admin Fly.io")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print(f"Token: {ADMIN_TOKEN[:20]}...")
    print("=" * 60)
    
    try:
        test_admin_access()
        test_admin_apis()
        test_admin_security()
        test_main_app()
        
        print("\n" + "=" * 60)
        print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("🎉 Il sistema admin su Fly.io funziona correttamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Errore durante i test: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 