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
# 🏗️ Análisis de Arquitectura: Docker Compose vs. Docker Stack

Este documento explica línea por línea la estructura de los archivos de orquestación utilizados en el proyecto y las diferencias fundamentales entre el desarrollo local y el despliegue en producción.

---

## 1. `docker-compose.yml` (Entorno Local)

Este archivo está diseñado para desarrollo. Su objetivo es **construir la aplicación desde el código fuente** en tu máquina y levantar los servicios rápidamente.

### 📂 Estructura Desglosada

```yaml
services:
  # SERVICIO 1: LA APP DE TRADUCCIÓN
  traductor:
    container_name: app_traductor
    # [CLAVE]: 'build' indica que se debe crear la imagen desde cero
    build:
      context: .              # Usa los archivos de la carpeta actual
      dockerfile: Dockerfile  # Usa este archivo de instrucciones
    ports:
      - "7860:7860"           # Mapea puerto host:contenedor
    environment:
      - GENAI_API_KEY=${API_KEY}  # Inyecta variable desde tu PC
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000 # Conexión interna
    depends_on:
      - mlflow-server         # Espera a que MLflow inicie primero
    networks:
      - traductor-net         # Se une a la red privada

  # SERVICIO 2: SERVIDOR MLFLOW
  mlflow-server:
    image: ghcr.io/mlflow/mlflow:latest # Usa imagen oficial (no construye)
    container_name: mlflow-server
    ports:
      - "5000:5000"
    # Comando largo para iniciar el servidor con configuración específica
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:////mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts
      ...
    volumes:
      - mlflow-db-data:/mlflow                    # Persistencia de la DB
      - mlflow-artifacts-data:/mlflow/artifacts   # Persistencia de archivos
    networks:
      - traductor-net

# REDES
networks:
  traductor-net:
    driver: bridge  # [CLAVE]: Driver 'bridge' es el estándar para local

# VOLÚMENES
volumes:
  mlflow-db-data:
  mlflow-artifacts-data:
```

---

## 2. `docker-stack.yml` (Entorno Producción / Swarm)

Este archivo está diseñado para despliegue. Asume que la imagen ya existe en Docker Hub y prioriza **escalabilidad**, **resiliencia** y **alta disponibilidad**.

### 📂 Estructura Desglosada

```yaml
# REDES
networks:
  traductor-net:
    driver: overlay # [CLAVE]: Para comunicación entre múltiples nodos

# VOLÚMENES
volumes:
  mlflow-db-data:
  mlflow-artifacts-data:

services:
  # SERVICIO 1: APP DE TRADUCCIÓN
  app-traductor:
    # [DIFERENCIA CRUCIAL]: Usa 'image', NO 'build'
    image: camiloramos2000/traductor-genai:1.0.0
    ports:
      - "7860:7860"
    environment:
      - GENAI_API_KEY=${API_KEY}
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000
    deploy:
      replicas: 2             # Levanta 2 copias idénticas
      restart_policy:
        condition: on-failure # Reinicia solo si falla
      update_config:
        parallelism: 1        # Actualiza 1 a la vez
        delay: 10s            # Espera 10 segundos por réplica
    networks:
      - traductor-net

  # SERVICIO 2: MLFLOW
  mlflow-server:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    deploy:
      replicas: 1             # 1 instancia por base de datos SQLite
      placement:
        constraints:
          - node.role == manager  # Corre en el nodo manager
    networks:
      - traductor-net
```

---

## 3. Diferencias Clave: Compose vs. Stack

Aquí es donde realmente se ve la diferencia entre **“funciona en mi máquina”** y **“funciona en producción”**.

| Característica        | docker-compose.yml   | docker-stack.yml | Explicación |
|----------------------|----------------------|------------------|-------------|
| **Origen del Código** | `build: .` | `image: usuario/repo:tag` | En producción los nodos no tienen tu código local; descargan una imagen lista. |
| **Red** | `driver: bridge` | `driver: overlay` | `bridge` conecta contenedores en un PC; `overlay` une múltiples servidores. |
| **Escalabilidad** | Manual | `deploy.replicas: N` | Swarm asegura siempre el número deseado de réplicas. |
| **Dependencias** | `depends_on` | Ignorado | Swarm maneja reintentos automáticos entre servicios. |
| **Contenedores** | Nombres fijos | Nombres dinámicos | Evita conflictos entre nodos. |
| **Actualizaciones** | Recreación total | `update_config` | Permite rolling updates sin downtime. |

---

## 📝 Resumen de Conceptos

### 🔧 Build vs Image

- **Compose**: “Toma estos archivos y compila algo nuevo”.
- **Stack**: “Descarga la versión estable 1.0.0 y ejecútala”.

### 🌐 Overlay Network

Permite que servicios en diferentes máquinas actúen como si estuvieran en una sola, pudiendo comunicarse usando:

```
http://mlflow-server:5000
```

### 🧠 Deploy Config

Es la capa inteligente del clúster; define:

- Cuántas réplicas mantener  
- Cómo recuperarse ante fallos  
- Cómo actualizar sin afectar usuarios  

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
