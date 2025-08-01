#!/bin/sh
# Copia la struttura dati locale nel volume persistente solo se la directory è vuota
if [ ! -d /data/documents ] || [ -z "$(ls -A /data/documents 2>/dev/null)" ]; then
  echo "[Entrypoint] Copio dati iniziali in /data ..."
  cp -r /app/data/* /data/
else
  echo "[Entrypoint] /data/documents non è vuota, nessuna copia eseguita."
fi
exec python app.py 