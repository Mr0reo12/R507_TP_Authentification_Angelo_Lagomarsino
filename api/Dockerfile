# Dockerfile pour le Backend
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du backend dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart

# Exposer le port utilisé par le backend
EXPOSE 5009

# Commande pour lancer le backend
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5009"]