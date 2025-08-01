#!/bin/bash
# Shortcut per rimuovere la cartella /app/backs dalla VM Fly.io
read -p "Sei sicuro di voler rimuovere la cartella /app/backs dalla VM Fly.io? [y/N] " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
  fly ssh console -C 'rm -rf /app/backs'
  echo "La cartella /app/backs è stata rimossa dalla VM Fly.io."
else
  echo "Operazione annullata. La cartella non è stata rimossa."
fi 