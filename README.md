# VertAssistRag3

Un sistema di assistenza virtuale basato su RAG (Retrieval-Augmented Generation) per la gestione di informazioni e documenti.

## 🚀 Caratteristiche

- **Sistema RAG**: Implementazione di Retrieval-Augmented Generation per risposte accurate
- **Interfaccia Web**: Dashboard amministrativa e interfaccia utente
- **Gestione Documenti**: Caricamento e indicizzazione di documenti
- **Autenticazione**: Sistema di login e registrazione utenti
- **Multilingua**: Supporto per italiano, inglese e francese
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
└── routes/               # Moduli delle route
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

## 📚 Utilizzo

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

Crea un file `.env` con le seguenti variabili:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## 📝 Script Utili

- `scripts/clear_documents.sh`: Pulisce i documenti caricati
- `scripts/list_app_folders.sh`: Lista le cartelle dell'applicazione
- `scripts/remove_backs.sh`: Rimuove i file di backup

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