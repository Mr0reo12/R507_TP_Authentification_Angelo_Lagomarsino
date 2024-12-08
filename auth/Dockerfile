# Dockerfile pour le service Auth
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du service Auth dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart

# Exposer le port utilisé par le service Auth
EXPOSE 5002

# Commande pour démarrer le service Auth
CMD ["uvicorn", "auth:app", "--host", "0.0.0.0", "--port", "5002"]