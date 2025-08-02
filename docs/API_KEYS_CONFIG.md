# 🔑 Configurazione Chiavi API

## 📋 **Panoramica**

Questo documento spiega come sono configurate le chiavi API nel progetto VertAssistRag3, sia in ambiente di sviluppo (locale) che in produzione (Fly.io).

## 🔧 **Chiavi Configurate**

### 1. **OpenAI API Key**
- **Scopo**: Chiamate a modelli OpenAI (GPT-4o-mini, embeddings)
- **Ambiente**: Sviluppo e Produzione
- **Sicurezza**: Alta priorità

### 2. **Admin Token**
- **Scopo**: Accesso al pannello amministrativo
- **Ambiente**: Sviluppo e Produzione
- **Sicurezza**: Alta priorità

### 3. **Secret Key (Flask)**
- **Scopo**: Sessioni e sicurezza Flask
- **Ambiente**: Sviluppo e Produzione
- **Sicurezza**: Media priorità

## 🌐 **Configurazione Produzione (Fly.io)**

### ✅ **Metodo: Secrets Fly.io**

Le chiavi sono configurate come secrets su Fly.io per massima sicurezza:

```bash
# Verifica secrets configurati
flyctl secrets list --app rag-assistant

# Risultato:
NAME            DIGEST                  CREATED AT       
ADMIN_TOKEN     759969dcae1707e2        1h24m ago       
OPENAI_API_KEY  cc6bd5e06df2798c        Jun 9 2025 16:42
SECRET_KEY      4dc6e5ba5b20cd74        Jun 9 2025 17:23
```

### 🔧 **Come Configurare Nuovi Secrets**

```bash
# Impostare OpenAI API Key
flyctl secrets set OPENAI_API_KEY="your-key-here" --app rag-assistant

# Impostare Admin Token
flyctl secrets set ADMIN_TOKEN="your-admin-token" --app rag-assistant

# Impostare Secret Key
flyctl secrets set SECRET_KEY="your-secret-key" --app rag-assistant
```

### ✅ **Vantaggi**
- **Sicurezza**: Chiavi non visibili nel codice
- **Isolamento**: Separazione ambiente dev/prod
- **Gestione**: Controllo centralizzato
- **Rotazione**: Facile aggiornamento chiavi

## 💻 **Configurazione Sviluppo (Locale)**

### 📁 **File: `.env`**

Le chiavi sono configurate nel file `.env` locale:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Admin
ADMIN_TOKEN=vertassistrag3-secret-key-2024-secure

# Flask
SECRET_KEY=your-secret-key-here
```

### ⚠️ **Importante**
- Il file `.env` è nel `.gitignore`
- Non viene mai committato nel repository
- Contiene solo chiavi di sviluppo

## 🔄 **Caricamento Chiavi**

### 📝 **Codice: `config.py`**

```python
import os
from dotenv import load_dotenv

# Carica variabili da .env (locale) o secrets (produzione)
load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")
    
    # Admin
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "vertassistrag3-secret-key-2024-secure")
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
```

### 🎯 **Logica di Caricamento**

1. **Sviluppo**: `load_dotenv()` carica da `.env`
2. **Produzione**: `os.getenv()` legge da secrets Fly.io
3. **Fallback**: Valori di default per configurazioni non critiche

## 🛡️ **Sicurezza**

### ✅ **Best Practices Implementate**

1. **Separazione Ambienti**
   - Sviluppo: `.env` locale
   - Produzione: Secrets Fly.io

2. **Gitignore**
   - `.env` escluso dal repository
   - Chiavi mai committate

3. **Validazione**
   - Controllo presenza chiavi critiche
   - Errori chiari se mancanti

4. **Rotazione**
   - Facile aggiornamento secrets
   - Processo documentato

### 🔍 **Verifica Sicurezza**

```bash
# Verifica secrets produzione
flyctl secrets list --app rag-assistant

# Verifica .env locale (non committato)
cat .env | grep -E "(OPENAI|ADMIN|SECRET)"

# Verifica gitignore
cat .gitignore | grep -E "\.env"
```

## 🚨 **Troubleshooting**

### ❌ **Problema: "Incorrect API key provided"**

**Possibili cause:**
1. Chiave non configurata in produzione
2. Chiave scaduta o invalida
3. Chiave locale non aggiornata

**Soluzioni:**
```bash
# Verifica secrets produzione
flyctl secrets list --app rag-assistant

# Aggiorna secret se necessario
flyctl secrets set OPENAI_API_KEY="new-key" --app rag-assistant

# Verifica .env locale
cat .env | grep OPENAI_API_KEY
```

### ❌ **Problema: "Unauthorized" admin**

**Possibili cause:**
1. ADMIN_TOKEN non configurato
2. Token sbagliato
3. Problema autenticazione

**Soluzioni:**
```bash
# Verifica admin token
flyctl secrets list --app rag-assistant | grep ADMIN

# Aggiorna token se necessario
flyctl secrets set ADMIN_TOKEN="new-token" --app rag-assistant
```

## 📊 **Stato Attuale**

### ✅ **Produzione (Fly.io)**
- **OpenAI API Key**: ✅ Configurata
- **Admin Token**: ✅ Configurato
- **Secret Key**: ✅ Configurato

### ✅ **Sviluppo (Locale)**
- **OpenAI API Key**: ✅ Configurata
- **Admin Token**: ✅ Configurato
- **Secret Key**: ⚠️ Da configurare se necessario

## 🎯 **Raccomandazioni**

### 🔧 **Per Sviluppatori**
1. Usa sempre `.env` per sviluppo locale
2. Non committare mai chiavi nel repository
3. Aggiorna `.env.example` con nuovi parametri
4. Testa sempre in locale prima del deploy

### 🚀 **Per Deploy**
1. Configura sempre secrets su Fly.io
2. Verifica secrets dopo ogni deploy
3. Usa chiavi diverse per dev/prod
4. Documenta processi di rotazione

### 🛡️ **Per Sicurezza**
1. Ruota regolarmente le chiavi
2. Monitora uso API
3. Usa rate limiting
4. Logga accessi admin

**Le chiavi API sono configurate correttamente e in modo sicuro! 🔑✨** 