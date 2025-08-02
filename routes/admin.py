from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, session
import json
import os
import subprocess
from werkzeug.utils import secure_filename
from config import config

admin_bp = Blueprint("admin", __name__, template_folder="../templates")

# Configurazione percorsi
IS_PRODUCTION = os.getenv("FLASK_ENV") != "development"
BASE_DIR = "/data" if IS_PRODUCTION else "data"
ADMIN_TOKEN = config.ADMIN_TOKEN
LOG_FILE = os.path.join(BASE_DIR, "logs", "queries.jsonl")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "documents")
URLS_FILE = os.path.join(BASE_DIR, "urls.txt")
CHUNKS_FILE = os.path.join(BASE_DIR, "documents", "chunks.jsonl")
CORRECTIONS_FILE = os.path.join(BASE_DIR, "corrections.jsonl")

# Crea le directory necessarie
for directory in [os.path.dirname(LOG_FILE), UPLOAD_FOLDER, os.path.dirname(URLS_FILE)]:
    os.makedirs(directory, exist_ok=True)

# Crea i file se non esistono
for file_path in [LOG_FILE, URLS_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            pass

def check_auth():
    # Controlla il token nell'URL (metodo legacy)
    token = request.args.get("token")
    if token and token == ADMIN_TOKEN:
        return True
    
    # Controlla l'header Authorization (metodo moderno)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Rimuovi "Bearer "
        if token == ADMIN_TOKEN:
            return True
    
    return False

def get_documents():
    documents = []
    if os.path.exists(UPLOAD_FOLDER):
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                if file.endswith(('.pdf', '.txt', '.md')) and not file.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, file), UPLOAD_FOLDER)
                    documents.append(rel_path)
    return sorted(documents)

def get_links():
    links = []
    if os.path.exists(URLS_FILE):
        try:
            with open(URLS_FILE, "r", encoding="utf-8") as f:
                links = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Errore nella lettura del file URLs: {str(e)}")
    return links

def get_chunks():
    chunks = []
    if os.path.exists(CHUNKS_FILE):
        try:
            with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        chunks.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Errore nella lettura del file chunks: {str(e)}")
    return chunks

def load_corrections():
    corrections = {}
    if os.path.exists(CORRECTIONS_FILE):
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    corrections[item["query"]] = item["corrected_answer"]
                except Exception:
                    continue
    return corrections

def save_correction(query, corrected_answer):
    # Carica tutte le correzioni esistenti
    corrections = []
    if os.path.exists(CORRECTIONS_FILE):
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    if item["query"] != query:
                        corrections.append(item)
                except Exception:
                    continue
    # Aggiungi o aggiorna la correzione
    corrections.append({"query": query, "corrected_answer": corrected_answer})
    # Sovrascrivi il file
    with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
        for c in corrections:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

@admin_bp.route("/admin", endpoint="admin_dashboard")
def admin_dashboard():
    if not check_auth():
        # Se è una richiesta AJAX/API, restituisci JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Authorization'):
            return jsonify({'error': 'Unauthorized'}), 401
        # Altrimenti mostra la pagina di login
        return render_template("admin_login.html")

    log_entries = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        log_entries.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Errore nella lettura del file di log: {str(e)}")

    log_entries = sorted(log_entries, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Ottieni il valore di MIN_OVERLAP
    min_overlap = float(os.getenv('MIN_OVERLAP', '0.7'))
    
    return render_template("admin.html", 
                         logs=log_entries,
                         documents=get_documents(),
                         links=get_links(),
                         needs_reindex=session.get('needs_reindex', False),
                         min_overlap=min_overlap,
                         chunks=get_chunks())

@admin_bp.route("/admin/delete-document", methods=["POST"])
def delete_document():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400

        # Verifica che il file sia nella cartella documents
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Elimina il file
        os.remove(file_path)
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route("/admin/delete-link", methods=["POST"])
def delete_link():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        link = data.get('link')
        if not link:
            return jsonify({'error': 'Link is required'}), 400

        # Leggi tutti i link
        links = get_links()
        
        # Rimuovi il link specificato
        if link in links:
            links.remove(link)
            
            # Scrivi la lista aggiornata
            with open(URLS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(links))
            
            return jsonify({'message': 'Link deleted successfully'})
        else:
            return jsonify({'error': 'Link not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route("/admin/chunks", endpoint="admin_chunks")
def admin_chunks():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    chunks = get_chunks()
    return render_template("admin_chunks.html", chunks=chunks)

@admin_bp.route("/admin/upload", methods=["POST"], endpoint="admin_upload")
def admin_upload():
    if not check_auth():
        return redirect(url_for("admin.admin_dashboard"))

    uploaded_file = request.files.get("document")
    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        if filename:
            path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(path)
            flash(f"File '{filename}' caricato con successo.", "success")
            session['needs_reindex'] = True

    link = request.form.get("link")
    if link:
        with open(URLS_FILE, "a", encoding="utf-8") as f:
            f.write(link.strip() + "\n")
        flash(f"Link '{link}' aggiunto con successo.", "success")
        session['needs_reindex'] = True

    return redirect(url_for("admin.admin_dashboard", token=request.args.get("token")))

@admin_bp.route("/admin/reindex", methods=["POST"], endpoint="admin_reindex")
def admin_reindex():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Esegui la reindicizzazione
        subprocess.run(["python", "ingest.py"], check=True)
        
        # Genera i metadati aggiornati
        subprocess.run(["python", "generate_metadata.py"], check=True)
        
        # Resetta il flag di reindicizzazione
        session['needs_reindex'] = False
        
        return jsonify({'message': 'Reindicizzazione e generazione metadati completate con successo'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Errore durante la reindicizzazione: {str(e)}'}), 500

@admin_bp.route('/admin/get-min-overlap')
def get_min_overlap():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        min_overlap = float(os.getenv('MIN_OVERLAP', '0.7'))
        return jsonify({'min_overlap': min_overlap})
    except Exception as e:
        print(f"Errore nel recupero del MIN_OVERLAP: {str(e)}")  # Debug
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/update-min-overlap', methods=['POST'])
def update_min_overlap():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        if not data or 'min_overlap' not in data:
            return jsonify({'error': 'Missing min_overlap parameter'}), 400
        
        try:
            min_overlap = float(data['min_overlap'])
        except (ValueError, TypeError):
            return jsonify({'error': 'min_overlap must be a valid number'}), 400

        if not 0 <= min_overlap <= 1:
            return jsonify({'error': 'min_overlap must be between 0 and 1'}), 400

        # Aggiorna il file .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        env_lines = []
        
        # Leggi il file .env esistente
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Cerca la riga con MIN_OVERLAP
        min_overlap_found = False
        for i, line in enumerate(env_lines):
            if line.startswith('MIN_OVERLAP='):
                # Assicurati che il valore sia salvato in formato decimale
                env_lines[i] = f'MIN_OVERLAP={min_overlap:.2f}\n'
                min_overlap_found = True
                break
        
        # Se non esiste, aggiungila
        if not min_overlap_found:
            env_lines.append(f'MIN_OVERLAP={min_overlap:.2f}\n')
        
        # Scrivi il file .env
        with open(env_path, 'w') as f:
            f.writelines(env_lines)
        
        # Aggiorna la variabile d'ambiente
        os.environ['MIN_OVERLAP'] = str(min_overlap)
        
        return jsonify({'min_overlap': min_overlap})
    except Exception as e:
        print(f"Errore nell'aggiornamento del MIN_OVERLAP: {str(e)}")  # Debug
        return jsonify({'error': str(e)}), 500

@admin_bp.route("/admin/correct-answer", methods=["POST"])
def correct_answer():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    query = data.get("query")
    corrected_answer = data.get("corrected_answer")
    if not query or not corrected_answer:
        return jsonify({"error": "Missing data"}), 400
    save_correction(query, corrected_answer)
    return jsonify({"message": "Correzione salvata!"})

@admin_bp.route("/admin/get-corrections")
def get_corrections():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    corrections = []
    if os.path.exists(CORRECTIONS_FILE):
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    corrections.append(item)
                except Exception:
                    continue
    return jsonify({"corrections": corrections})

@admin_bp.route("/admin/delete-correction", methods=["POST"])
def delete_correction():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    # Rimuovi la correzione dal file
    if os.path.exists(CORRECTIONS_FILE):
        new_lines = []
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    if item["query"] != query:
                        new_lines.append(line)
                except Exception:
                    continue
        with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    return jsonify({"message": "Correzione eliminata!"})