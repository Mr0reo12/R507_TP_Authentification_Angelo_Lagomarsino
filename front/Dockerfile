# Dockerfile pour le Frontend
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers frontend dans le conteneur
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart

# Exposer le port utilisé par le frontend
EXPOSE 5010

# Commande pour lancer le frontend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5010"]
