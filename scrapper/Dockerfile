# Utiliser une image Python officielle comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer cron
RUN apt-get update && apt-get install -y cron

# Copier le fichier des exigences et installer les dépendances Python
COPY requirements.txt /app/
RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt 

# Copier l'ensemble de l'application dans le conteneur
COPY . /app/

# Rendre le script entrypoint exécutable
COPY entrypointscrapy.sh /app/
RUN chmod +x /app/entrypointscrapy.sh


# Définir le script entrypoint comme point d'entrée pour le conteneur
ENTRYPOINT [ "sh", "/app/entrypointscrapy.sh" ]
