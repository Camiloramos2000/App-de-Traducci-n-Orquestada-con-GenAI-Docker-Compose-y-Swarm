FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para compilar algunas librerías Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero (mejora el uso de cache en builds)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Gradio debe escuchar desde afuera del contenedor
ENV GRADIO_SERVER_NAME=0.0.0.0

# Exponer el puerto donde se ejecutará la app
EXPOSE 7860

# Ejecutar la aplicación
CMD ["python", "main.py"]
