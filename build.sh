#!/usr/bin/env bash
# Render build script — exécuté à chaque déploiement
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques (Django admin, DRF browsable, etc.)
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate