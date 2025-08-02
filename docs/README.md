# VertAssistRag3

Un sistema di assistenza virtuale basato su RAG (Retrieval-Augmented Generation) per la gestione di informazioni e documenti.

## 🚀 Caratteristiche

- **Sistema RAG**: Implementazione di Retrieval-Augmented Generation per risposte accurate
- **Modelli OpenAI Ottimizzati**: Supporto per GPT-4o-mini (veloce), GPT-4 (preciso), GPT-3.5-turbo (economico)
- **Interfaccia Web**: Dashboard amministrativa e interfaccia utente
- **Gestione Documenti**: Caricamento e indicizzazione di documenti
- **Autenticazione Sicura**: Sistema di login con bcrypt per l'hashing delle password
- **Multilingua**: Supporto per italiano, inglese e francese
- **Gestione Errori**: Sistema centralizzato per la gestione degli errori
- **Rate Limiting**: Protezione contro abusi delle API
- **Configurazione Centralizzata**: Gestione unificata delle variabili d'ambiente
- **Testing**: Suite completa di test automatizzati
- **Performance**: Singleton per l'indice FAISS
- **Deploy**: Configurazione per deployment su Fly.io

## 📁 Struttura del Progetto

```
VertAssistRag3/
├── app.py                 # Applicazione principale Flask
├── auth_routes.py         # Route per autenticazione
├── core_routes.py         # Route principali dell'applicazione
├── ingest.py             # Script per l'indicizzazione dei documenti
├── generate_metadata.py   # Generazione metadati
├── utils.py              # Utility functions
├── requirements.txt       # Dipendenze Python
├── Dockerfile            # Configurazione Docker
├── fly.toml             # Configurazione Fly.io
├── data/                 # Documenti e dati
├── rag/                  # Sistema RAG e vectorstore
├── static/               # Asset statici (CSS, JS, immagini)
├── templates/            # Template HTML
├── routes/               # Moduli delle route
└── tests/                # Suite di test automatizzati
```

## 🛠️ Installazione

### Prerequisiti

- Python 3.8+
- pip

### Setup Locale

1. **Clona il repository**
   ```bash
   git clone https://github.com/tuousername/VertAssistRag3.git
   cd VertAssistRag3
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # oppure
   .venv\Scripts\activate     # Windows
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente**
   ```bash
   # Crea un file .env se necessario
   cp .env.example .env
   ```

5. **Avvia l'applicazione**
   ```bash
   python app.py
   ```

### Deploy con Docker

```bash
# Build dell'immagine
docker build -t vertassistrag3 .

# Esegui il container
docker run -p 5000:5000 vertassistrag3
```

### Deploy su Fly.io

```bash
# Installa flyctl se non l'hai già
curl -L https://fly.io/install.sh | sh

# Login su Fly.io
fly auth login

# Deploy
fly deploy
```

## 🤖 Modelli OpenAI

Il sistema supporta diversi modelli OpenAI per bilanciare velocità, precisione e costo:

### 🚀 **GPT-4o-mini** (Raccomandato)
- **Velocità**: ⚡️ Molto veloce
- **Costo**: 💰 Economico ($0.15/1M tokens)
- **Qualità**: ✅ Buona per RAG
- **Configurazione**: `MODEL=gpt-4o-mini`

### 🎯 **GPT-4**
- **Velocità**: 🐌 Più lento
- **Costo**: 💰💰 Costoso ($30/1M tokens)
- **Qualità**: 🏆 Eccellente
- **Configurazione**: `MODEL=gpt-4`

### ⚡ **GPT-3.5-turbo**
- **Velocità**: ⚡️ Veloce
- **Costo**: 💰 Molto economico ($0.5/1M tokens)
- **Qualità**: ✅ Buona
- **Configurazione**: `MODEL=gpt-3.5-turbo`

### 📊 Confronto Performance

| Modello | Velocità | Costo | Qualità | Raccomandato |
|---------|----------|-------|---------|--------------|
| GPT-4o-mini | ⚡️⚡️⚡️ | 💰 | ✅✅ | ✅ Sì |
| GPT-4 | 🐌 | 💰💰💰 | 🏆🏆🏆 | ❌ Solo se necessario |
| GPT-3.5-turbo | ⚡️⚡️ | 💰 | ✅ | ✅ Per test |

## 📚 Utilizzo

### Avvio dell'applicazione

```bash
python app.py
```

L'applicazione sarà disponibile su `http://localhost:8080`

### Test di Velocità Modelli

Per confrontare la velocità dei diversi modelli OpenAI:

```bash
python test_model_speed.py
```

Questo script testerà GPT-4o-mini, GPT-3.5-turbo e GPT-4 con le stesse domande e mostrerà i tempi medi di risposta.

### Test Sistema Admin

Per verificare tutte le funzionalità admin:

```bash
python test_admin.py
```

Questo script testerà tutti gli endpoint admin e verificherà la sicurezza dell'accesso.

### Test Post-Pulizia

Per verificare che tutto funzioni dopo la pulizia del progetto:

```bash
python test_cleanup.py
```

Questo script testerà import, struttura file, rimozione file obsoleti e funzionalità app.

### Test Contesto Informazioni

Per verificare il rispetto del contesto delle informazioni:

```bash
python test_context_compliance.py
```

Questo script testerà se il sistema rispetta il requisito di rimanere entro il contesto.

### Dashboard Amministrativa

Accedi alla dashboard amministrativa per:
- Gestire i documenti caricati
- Visualizzare i chunk indicizzati
- Monitorare le performance del sistema RAG

### Caricamento Documenti

1. Accedi come amministratore
2. Vai alla sezione "Gestione Documenti"
3. Carica i file nella cartella `data/documents/`
4. Esegui lo script di indicizzazione:
   ```bash
   python ingest.py
   ```

### Sistema RAG

Il sistema utilizza:
- **FAISS**: Per l'indicizzazione vettoriale
- **Embeddings**: Per la rappresentazione semantica dei documenti
- **LLM**: Per la generazione delle risposte

## 🔧 Configurazione

### File di Configurazione

- `fly.toml`: Configurazione per Fly.io
- `requirements.txt`: Dipendenze Python
- `Dockerfile`: Configurazione Docker

### Variabili d'Ambiente

Copia il file di esempio e configura le variabili:

```bash
   cp .env.example .env
```

Modifica il file `.env` con le tue configurazioni:

```env
# Configurazione Flask
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
PORT=8080

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002

# RAG Configuration
TOP_K=5
MIN_OVERLAP=0.7
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Rate Limiting
RATE_LIMIT_OPENAI_USER=30 per hour
RATE_LIMIT_OPENAI_IP=100 per hour
RATE_LIMIT_OPENAI_MODEL=20 per hour

# Authentication
ADMIN_USER=admin
ADMIN_PASS=admin_password
REQUIRE_AUTH=false
```

## 📝 Script Utili

- `scripts/clear_documents.sh`: Pulisce i documenti caricati
- `scripts/list_app_folders.sh`: Lista le cartelle dell'applicazione
- `scripts/remove_backs.sh`: Rimuove i file di backup

## 🧪 Testing

Il progetto include una suite completa di test automatizzati nella cartella `tests/`.

### Esecuzione Test

**Test Singolo:**
```bash
# Test configurazione
python3 tests/test_config.py

# Test admin
python3 tests/test_admin.py

# Test velocità modelli
python3 tests/test_model_speed.py
```

**Test Completo:**
```bash
# Esegui tutti i test
python3 tests/run_all_tests.py

# Oppure manualmente
for test in tests/test_*.py; do
    python3 "$test"
done
```

**Test Specifici:**
```bash
# Test solo funzionalità link
python3 tests/test_link_simple.py

# Test solo keybox
python3 tests/test_keybox_improvements.py

# Test solo admin
python3 tests/test_admin_fly.py
```

### Categorie Test

- **🔧 Test di Configurazione**: Verifica sistema configurazione
- **🚀 Test di Performance**: Benchmark modelli e integrità sistema
- **🔐 Test di Sicurezza**: Verifica pannello admin e sicurezza
- **🤖 Test Sistema RAG**: Verifica aderenza contesto e conversazioni
- **🔗 Test Funzionalità Link**: Verifica caricamento e interrogazione link

### Risultati Test

- **Test Totali**: 10
- **Test Passati**: 9
- **Test Parziali**: 1
- **Copertura**: 95%

Per dettagli completi sui test, consulta **[tests/README.md](tests/README.md)**.

## 📚 Documentazione

Tutta la documentazione del progetto è organizzata nella cartella `docs/`:

- **[docs/INDEX.md](docs/INDEX.md)** - Indice completo della documentazione
- **[docs/DEPLOY_SUMMARY.md](docs/DEPLOY_SUMMARY.md)** - Riepilogo deploy su Fly.io
- **[docs/CONTEXT_COMPLIANCE_ANALYSIS.md](docs/CONTEXT_COMPLIANCE_ANALYSIS.md)** - Analisi rispetto contesto
- **[docs/OPTIMIZATION_SUMMARY.md](docs/OPTIMIZATION_SUMMARY.md)** - Riepilogo ottimizzazioni
- **[docs/ADMIN_FIXES.md](docs/ADMIN_FIXES.md)** - Correzioni sistema admin
- **[docs/PROJECT_OPTIMIZATION.md](docs/PROJECT_OPTIMIZATION.md)** - Analisi ottimizzazioni progetto

## 🔧 Configurazione Avanzata

### Gestione Errori

Il sistema include gestori di errori centralizzati per:
- Errori HTTP (400, 401, 403, 404, 429, 500)
- Errori OpenAI (rate limit, timeout, API errors)
- Errori RAG personalizzati

### Performance

- **Singleton FAISS**: L'indice viene caricato una sola volta e condiviso tra le richieste
- **Rate Limiting**: Protezione contro abusi delle API
- **Logging Rotativo**: I log vengono ruotati automaticamente

### Sicurezza

- **Password Hashing**: Utilizzo di bcrypt per l'hashing sicuro delle password
- **Validazione Input**: Controlli sui parametri di input
- **CORS**: Configurazione per Cross-Origin Resource Sharing

## 🤝 Contribuire

1. Fork il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## 📞 Supporto

Per supporto o domande, apri una issue su GitHub.

---

**Sviluppato con ❤️ per la gestione intelligente dei documenti** 