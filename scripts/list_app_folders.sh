#!/bin/bash
# Script per elencare tutte le cartelle presenti in /app sulla VM Fly.io
fly ssh console -C 'ls -l /app' 