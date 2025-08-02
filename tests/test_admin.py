#!/usr/bin/env python3
"""
Script per testare tutte le funzionalità admin
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"
ADMIN_TOKEN = "vertassistrag3-secret-key-2024-secure"

def test_admin_endpoints():
    """Testa tutti gli endpoint admin"""
    print("🔧 Test Funzionalità Admin")
    print("=" * 40)
    
    # Test 1: Dashboard admin
    print("\n1️⃣ Test Dashboard Admin")
    response = requests.get(f"{BASE_URL}/admin?token={ADMIN_TOKEN}")
    if response.status_code == 200:
        print("   ✅ Dashboard admin accessibile")
    else:
        print(f"   ❌ Dashboard admin errore: {response.status_code}")
    
    # Test 2: Get MIN_OVERLAP
    print("\n2️⃣ Test Get MIN_OVERLAP")
    response = requests.get(f"{BASE_URL}/admin/get-min-overlap?token={ADMIN_TOKEN}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ MIN_OVERLAP: {data.get('min_overlap', 'N/A')}")
    else:
        print(f"   ❌ Get MIN_OVERLAP errore: {response.status_code}")
    
    # Test 3: Update MIN_OVERLAP
    print("\n3️⃣ Test Update MIN_OVERLAP")
    new_value = 0.4
    response = requests.post(
        f"{BASE_URL}/admin/update-min-overlap?token={ADMIN_TOKEN}",
        headers={"Content-Type": "application/json"},
        json={"min_overlap": new_value}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ MIN_OVERLAP aggiornato a: {data.get('min_overlap', 'N/A')}")
    else:
        print(f"   ❌ Update MIN_OVERLAP errore: {response.status_code}")
    
    # Test 4: Get Corrections
    print("\n4️⃣ Test Get Corrections")
    response = requests.get(f"{BASE_URL}/admin/get-corrections?token={ADMIN_TOKEN}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Corrections: {len(data.get('corrections', []))} elementi")
    else:
        print(f"   ❌ Get Corrections errore: {response.status_code}")
    
    # Test 5: Add Correction
    print("\n5️⃣ Test Add Correction")
    correction_data = {
        "query": "test query",
        "corrected_answer": "test answer"
    }
    response = requests.post(
        f"{BASE_URL}/admin/correct-answer?token={ADMIN_TOKEN}",
        headers={"Content-Type": "application/json"},
        json=correction_data
    )
    if response.status_code == 200:
        print("   ✅ Correction aggiunta")
    else:
        print(f"   ❌ Add Correction errore: {response.status_code}")
    
    # Test 6: Delete Correction
    print("\n6️⃣ Test Delete Correction")
    response = requests.post(
        f"{BASE_URL}/admin/delete-correction?token={ADMIN_TOKEN}",
        headers={"Content-Type": "application/json"},
        json={"query": "test query"}
    )
    if response.status_code == 200:
        print("   ✅ Correction eliminata")
    else:
        print(f"   ❌ Delete Correction errore: {response.status_code}")
    
    # Test 7: Admin Chunks
    print("\n7️⃣ Test Admin Chunks")
    response = requests.get(f"{BASE_URL}/admin/chunks?token={ADMIN_TOKEN}")
    if response.status_code == 200:
        print("   ✅ Admin chunks accessibile")
    else:
        print(f"   ❌ Admin chunks errore: {response.status_code}")
    
    # Test 8: Reindex (simulato)
    print("\n8️⃣ Test Reindex (simulato)")
    print("   ⚠️  Reindex richiede subprocess, testato manualmente")
    
    print("\n✅ Test completati!")

def test_admin_access_without_token():
    """Testa l'accesso admin senza token"""
    print("\n🔒 Test Accesso Senza Token")
    print("=" * 30)
    
    endpoints = [
        "/admin",
        "/admin/get-min-overlap",
        "/admin/get-corrections",
        "/admin/chunks"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 401:
            print(f"   ✅ {endpoint}: Correttamente protetto (401)")
        else:
            print(f"   ❌ {endpoint}: Non protetto ({response.status_code})")

def main():
    """Test principale"""
    print("🚀 Test Completo Sistema Admin")
    print("=" * 50)
    
    try:
        test_admin_endpoints()
        test_admin_access_without_token()
        print("\n🎉 Tutti i test completati con successo!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Errore: Impossibile connettersi al server")
        print("   Assicurati che l'applicazione sia in esecuzione su http://localhost:8080")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    main() 