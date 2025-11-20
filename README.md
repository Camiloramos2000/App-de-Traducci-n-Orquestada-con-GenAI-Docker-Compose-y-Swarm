# 🌍 App de Traducción Orquestada con GenAI, Docker Compose y Swarm

Este proyecto es una aplicación de traducción de texto impulsada por **Google GenAI (Gemini)**.  
La aplicación expone una interfaz web amigable construida con **Gradio** y registra cada interacción, métricas de latencia y parámetros en **MLflow**.

El sistema permite dos modos de ejecución:

- **Orquestación Local**: Usando Docker Compose para desarrollo y pruebas.  
- **Orquestación en Producción**: Usando Docker Swarm para escalabilidad y alta disponibilidad.

---

## 📸 Capturas de Pantalla

### 1. Interfaz de Usuario (Gradio)

<div align="center">
<img src="img/Gradio Swarm.png" alt="Interfaz de Traducción Gradio" width="800" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
<p><em>Interfaz donde el usuario ingresa el texto y selecciona el idioma de destino.</em></p>
</div>

### 2. Registro de Runs (MLflow)

<div align="center">
<img src="img/Run swarm.png" alt="Dashboard de MLflow" width="800" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
<p><em>Dashboard de MLflow mostrando los 'runs' de cada traducción con sus métricas.</em></p>
</div>

---

## 🛠️ 1. Orquestación Local (Docker Compose)

Ideal para desarrollo, pruebas o depuración. Utiliza `docker-compose.yml` y construye la imagen localmente desde tu `Dockerfile`.

### **Paso 1: Configurar la API Key**

En **Linux / Mac**:

```
export API_KEY="tu_api_key_de_google_aqui"
```

En **Windows (PowerShell)**:

```
$env:API_KEY="tu_api_key_de_google_aqui"
```

### **Paso 2: Construir y Levantar**

```
docker-compose up --build
```

### **Paso 3: Acceder a los Servicios**

- Traductor (Gradio): http://localhost:7860  
- MLflow UI: http://localhost:5000  

Para detener:

```
docker-compose down
```

---

## 🐝 2. Despliegue en Producción (Docker Swarm)

Para ambientes reales, usando la imagen optimizada de Docker Hub:  
`camiloramos2000/traductor-genai:1.0.0`

### **Prerrequisitos**
- Docker instalado  
- `docker swarm init` ejecutado  

### **Paso 1: Desplegar el Stack**

```
docker stack deploy -c docker-stack.yml traductor_stack
```

### **Paso 2: Verificar y Escalar**

Revisar servicios:

```
docker stack services traductor_stack
```

Escalar a 3 réplicas:

```
docker service scale traductor_stack_app-traductor=3
```

---

## 📦 Gestión de Imágenes (Docker Hub)

Comandos usados para publicar la imagen:

```
docker login
docker tag app_traductor:latest camiloramos2000/traductor-genai:1.0.0
docker push camiloramos2000/traductor-genai:1.0.0
```

### Prueba de Imagen en Docker Hub
<div align="center">
<img src="img/imagen_app_dockerHub.png" alt="Imagen subida a Docker Hub" width="800" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
<p><em>Evidencia de la imagen publicada en el registro de Docker Hub.</em></p>
</div>

---

## 📂 Estructura del Proyecto

- **docker-compose.yml**: Orquestación local (Dev).  
- **docker-stack.yml**: Orquestación remota (Prod/Swarm).  
- **Dockerfile**: Construcción de la imagen.  
- **main.py**: Interfaz Gradio.  
- **Translate.py**: Lógica de traducción + MLflow.  
- **model.py**: Conexión a Google GenAI.

---

## 🧠 Arquitectura y Conceptos Clave

### 1. Arquitectura del Sistema

Servicios:

- **app-traductor**: Lógica de traducción + interfaz Gradio.  
- **mlflow-server**: Registro de métricas y artefactos.

Redes:

- **traductor-net**: Red interna para comunicación segura.

Volúmenes:

- **mlflow-db-data**: Base de datos SQLite.  
- **mlflow-artifacts-data**: Archivos persistentes.

---

### 2. Diferencias entre Compose y Stack

| Característica | Docker Compose | Docker Stack / Swarm |
|----------------|----------------|-----------------------|
| **Origen** | build local | imagen fija |
| **Red** | bridge (1 host) | overlay (multi-host) |
| **Escalado** | limitado | automático, replicas |
| **Restart** | simple | restart_policy avanzada |
| **Updates** | recrea contenedor | rolling updates |

---

## 3. Guía de Comandos Clave

```
docker-compose up --build
docker push <usuario>/<imagen>:<tag>
docker swarm init
docker stack deploy -c <archivo> <nombre>
docker service scale <servicio>=<n>
```

---

## 4. Observaciones del Sistema

- **Latencia**: Dominada por la API de Google Gemini.  
- **Calidad**: gemini-2.5-flash ofrece buen equilibrio.  
- **Persistencia**: Garantizada por volúmenes MLflow.

---

## 🧹 Limpieza

Para eliminar el stack:

```
docker stack rm traductor_stack
```
