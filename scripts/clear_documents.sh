#!/bin/bash
# Shortcut per cancellare tutti i documenti dal volume persistente su Fly.io
read -p "Sei sicuro di voler cancellare TUTTI i documenti su /data/documents della VM Fly.io? [y/N] " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
  fly ssh console -C 'rm -rf /data/documents/*'
  echo "Tutti i documenti su /data/documents sono stati cancellati dalla VM Fly.io."
else
  echo "Operazione annullata. Nessun documento è stato cancellato."
fi 