# Dockerfile para construir la aplicación FastAPI
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos al contenedor
COPY . .

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir fastapi uvicorn Jinja2 requests python-multipart

# Exponer el puerto que utilizará la aplicación
EXPOSE 5009

# Comando para ejecutar la aplicación
CMD ["python", "api.py"]

