#!/usr/bin/env python3
"""
Script per eseguire tutti i test del progetto VertAssistRag3
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_test(test_file):
    """Esegue un singolo test"""
    print(f"🧪 Eseguendo {test_file}...")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {test_file}: PASS")
            return True
        else:
            print(f"❌ {test_file}: FAIL")
            print(f"   Errore: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_file}: ERROR - {str(e)}")
        return False

def get_test_files():
    """Ottiene la lista dei file di test"""
    test_dir = Path(__file__).parent
    test_files = []
    
    for test_file in test_dir.glob("test_*.py"):
        if test_file.name != "run_all_tests.py":
            test_files.append(str(test_file))
    
    return sorted(test_files)

def main():
    """Esegue tutti i test"""
    print("🧪 Test Suite VertAssistRag3")
    print("=" * 60)
    
    # Ottieni lista test
    test_files = get_test_files()
    
    if not test_files:
        print("❌ Nessun test trovato!")
        return False
    
    print(f"📋 Trovati {len(test_files)} test:")
    for test_file in test_files:
        print(f"   - {os.path.basename(test_file)}")
    
    print("\n🚀 Inizio esecuzione test...")
    print("=" * 60)
    
    # Esegui test
    results = {
        "total": len(test_files),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    start_time = time.time()
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n[{i}/{len(test_files)}] ", end="")
        
        test_start = time.time()
        success = run_test(test_file)
        test_duration = time.time() - test_start
        
        if success:
            results["passed"] += 1
            status = "PASS"
        else:
            results["failed"] += 1
            status = "FAIL"
        
        results["details"].append({
            "file": os.path.basename(test_file),
            "status": status,
            "duration": test_duration
        })
        
        # Pausa tra i test per evitare rate limiting
        if i < len(test_files):
            print("   ⏳ Pausa 2 secondi...")
            time.sleep(2)
    
    # Risultati finali
    total_duration = time.time() - start_time
    success_rate = (results["passed"] / results["total"]) * 100
    
    print("\n" + "=" * 60)
    print("📊 RISULTATI FINALI")
    print("=" * 60)
    
    print(f"🎯 Test Totali: {results['total']}")
    print(f"✅ Test Passati: {results['passed']}")
    print(f"❌ Test Falliti: {results['failed']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️ Tempo Totale: {total_duration:.1f}s")
    
    print("\n📋 Dettagli Test:")
    for detail in results["details"]:
        status_icon = "✅" if detail["status"] == "PASS" else "❌"
        print(f"   {status_icon} {detail['file']} ({detail['duration']:.1f}s)")
    
    print("\n" + "=" * 60)
    
    if success_rate >= 90:
        print("🎉 ECCELLENTE! Tutti i test principali sono passati!")
    elif success_rate >= 70:
        print("✅ BUONO! La maggior parte dei test è passata.")
    elif success_rate >= 50:
        print("⚠️ DISCRETO! Alcuni test hanno fallito.")
    else:
        print("❌ PROBLEMATICO! Molti test hanno fallito.")
    
    print("=" * 60)
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 