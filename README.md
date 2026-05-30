# RAG Banking Assistant

Sistema RAG local con web scraping, base vectorial, historial conversacional persistente, analítica de conversaciones e interfaz web sencilla.

El caso de uso simula un asistente interno que responde preguntas sobre información publicada en el sitio institucional de un banco, inicialmente configurado para `https://www.bbva.com.co/`.

---

## 1. Descripción del proyecto

Este proyecto implementa un sistema **RAG, Retrieval-Augmented Generation**, que permite consultar información extraída desde un sitio web institucional mediante una interfaz conversacional.

El sistema realiza las siguientes tareas:

- Extrae información del sitio web mediante web scraping.
- Guarda los datos crudos y limpios en local.
- Divide el contenido en chunks.
- Genera embeddings locales.
- Indexa los documentos en una base vectorial local.
- Permite hacer preguntas usando una interfaz web.
- Recupera documentos relevantes desde ChromaDB.
- Genera respuestas usando un modelo local de Hugging Face.
- Guarda historial conversacional por `session_id`.
- Usa los últimos `N` mensajes como memoria conversacional.
- Permite consultar métricas del histórico de conversaciones.

---

## 2. Stack tecnológico

- **Python**: lenguaje principal del sistema.
- **FastAPI**: backend para exponer endpoints REST.
- **Streamlit**: interfaz conversacional y panel de analítica.
- **BeautifulSoup + Trafilatura**: scraping y extracción de texto desde páginas web.
- **LangChain**: división de documentos y conexión con componentes RAG.
- **ChromaDB**: base vectorial local y persistente.
- **Sentence Transformers**: generación local de embeddings.
- **Hugging Face Transformers**: ejecución local del modelo generativo.
- **SQLite**: persistencia del historial conversacional.
- **Docker Compose**: ejecución local completa del sistema.

---

## 3. Arquitectura general

```text
Usuario
  ↓
Streamlit UI
  ↓
FastAPI
  ↓
RAG Facade
  ├── Conversation Memory
  ├── SQLite Repository
  ├── Chroma Vector Store
  ├── Hugging Face Embeddings
  └── Local LLM
```

---

## 4. Estructura del proyecto

```text
rag-banking-assistant/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── scraping/
│   │   ├── scraper.py
│   │   ├── cleaner.py
│   │   └── storage.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   ├── llm.py
│   │   └── chain.py
│   │
│   ├── conversation/
│   │   ├── repository.py
│   │   ├── memory.py
│   │   └── analytics.py
│   │
│   └── patterns/
│       ├── factories.py
│       ├── strategies.py
│       └── facade.py
│
├── ui/
│   └── streamlit_app.py
│
├── scripts/
│   ├── scrape.py
│   ├── ingest.py
│   └── reset_data.py
│
├── tests/
│   ├── test_cleaner.py
│   ├── test_memory.py
│   └── test_facade_sources.py
│
├── data/
│   ├── raw/
│   ├── clean/
│   └── chroma/
│
├── database/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Requisitos previos

Para ejecutar el proyecto se necesita:

- Docker
- Docker Compose
- Git

No se requieren API keys ni servicios pagos.

---

## 6. Configuración inicial

Clonar el repositorio:

```bash
git clone <repo-url>
cd rag-banking-assistant
```

Crear el archivo `.env` a partir del archivo de ejemplo:

```bash
cp .env.example .env
```

El archivo `.env.example` funciona como plantilla segura de configuración. El archivo `.env` real no se sube al repositorio porque puede contener valores privados o propios del entorno local.

Variables principales:

```env
SCRAPER_START_URL=https://www.bbva.com.co/
SCRAPER_ALLOWED_DOMAIN=www.bbva.com.co
SCRAPER_MAX_PAGES=25

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct

MEMORY_N_MESSAGES=6
CHUNK_SIZE=800
CHUNK_OVERLAP=120
TOP_K=8

ENABLE_RERANKER=false
```

---

## 7. Ejecución con Docker

Levantar todos los servicios:

```bash
docker compose up --build
```

Luego abrir la interfaz web:

```text
http://localhost:8501
```

Documentación interactiva de FastAPI:

```text
http://localhost:8000/docs
```

---

## 8. Uso de la aplicación

Flujo recomendado:

1. Entrar a la pestaña **Administración**.
2. Ejecutar scraping.
3. Indexar documentos.
4. Ir a la pestaña **Chat**.
5. Hacer preguntas usando un `session_id`.
6. Revisar métricas en la pestaña **Analítica**.

Ejemplo de pregunta:

```text
¿Qué productos de cuentas ofrece el banco?
```

---

## 9. Endpoints principales

```text
GET  /health
POST /scrape
POST /ingest
POST /chat
GET  /sessions
GET  /sessions/{session_id}/messages
GET  /analytics/summary
GET  /analytics/questions
GET  /analytics/sources
```

Ejemplo de request para `/chat`:

```json
{
  "session_id": "test-user-001",
  "question": "¿Qué cuentas ofrece el banco?"
}
```

Ejemplo de response:

```json
{
  "session_id": "test-user-001",
  "answer": "Según la información recuperada del sitio...",
  "sources": [
    {
      "title": "Título de la fuente",
      "url": "https://www.bbva.com.co/...",
      "preview": "Fragmento del contenido recuperado..."
    }
  ]
}
```

---

## 10. Flujo RAG

El flujo principal del sistema es:

```text
1. El usuario hace una pregunta desde Streamlit.
2. Streamlit envía la pregunta a FastAPI.
3. FastAPI llama al RAG Facade.
4. Se recuperan los últimos N mensajes de la sesión desde SQLite.
5. Se consulta ChromaDB para obtener documentos relevantes.
6. Opcionalmente se aplica reranking.
7. Se construye un prompt con historial, contexto y pregunta.
8. El modelo local genera la respuesta.
9. Se guarda la pregunta, la respuesta y las fuentes recuperadas.
10. La respuesta vuelve a Streamlit.
```

---

## 11. Historial conversacional

El sistema guarda los mensajes en SQLite usando un `session_id`.

Para cada nueva pregunta, se recuperan los últimos `N` mensajes de esa sesión. El valor de `N` se configura con:

```env
MEMORY_N_MESSAGES=6
```

Esto permite que el asistente mantenga contexto dentro de una conversación sin mezclar sesiones diferentes.

---

## 12. Analítica de conversaciones

La pestaña **Analítica** permite consultar:

- Total de sesiones.
- Total de mensajes.
- Total de preguntas.
- Latencia promedio.
- Preguntas más frecuentes.
- Fuentes más recuperadas.

Esta funcionalidad permite recorrer el histórico de conversaciones y extraer métricas de uso e impacto.

---

## 13. Patrones de diseño implementados

### 13.1 Factory Method

Ubicación:

```text
app/patterns/factories.py
```

Se usa para crear el modelo de embeddings y el cliente LLM.

Justificación:

Permite cambiar el proveedor de embeddings o el modelo generativo desde configuración sin modificar la lógica principal del sistema.

---

### 13.2 Strategy

Ubicación:

```text
app/patterns/strategies.py
app/scraping/cleaner.py
```

Se usa para definir diferentes estrategias de limpieza de texto.

Justificación:

El contenido web puede variar mucho entre bancos o sitios institucionales. Este patrón permite cambiar la forma de limpiar texto sin modificar el scraper.

---

### 13.3 Facade

Ubicación:

```text
app/patterns/facade.py
```

Se usa para encapsular el flujo completo del RAG:

1. Recuperar historial.
2. Buscar documentos relevantes.
3. Armar contexto.
4. Generar respuesta.
5. Guardar conversación.
6. Guardar evento RAG.

Justificación:

Mantiene los endpoints de FastAPI simples y separa la lógica de negocio de la capa API.

---

### 13.4 Repository

Ubicación:

```text
app/conversation/repository.py
```

Se usa para aislar el acceso a SQLite.

Justificación:

Permite cambiar SQLite por PostgreSQL u otra base de datos sin modificar la lógica conversacional.

---

## 14. Reranker

El sistema incluye una implementación opcional de reranker con CrossEncoder.

Para activarlo:

```env
ENABLE_RERANKER=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

Por defecto está desactivado para reducir consumo de recursos.

---

## 15. Decisiones de diseño

- Se eligió ejecución local para evitar costos y dependencias externas.
- Se usó Streamlit porque permite combinar chat y analítica en una misma interfaz.
- Se usó ChromaDB porque permite persistencia local simple.
- Se usó SQLite porque es suficiente para una prueba técnica y fácil de inspeccionar.
- Se dejó el modelo configurable para probar alternativas como modelos LiquidAI o Qwen.
- Se separó FastAPI de Streamlit para simular una arquitectura más cercana a producción.
- Se agregó un reranker opcional para mejorar la relevancia de los documentos recuperados.
- Se usa `.env.example` como plantilla y `.env` como configuración local.

---

## 16. Limitaciones conocidas

- El scraper no garantiza cobertura total del sitio, solo de las páginas descubiertas dentro del límite configurado.
- El modelo local puede responder más lento en CPU.
- La calidad de respuesta depende del contenido scrapeado y del modelo configurado.
- Algunas páginas institucionales pueden cargar contenido dinámico que no aparece en HTML estático.
- El reranker está disponible, pero desactivado por defecto para ahorrar recursos.
- No se implementó autenticación, ya que el alcance de la prueba está centrado en RAG, scraping, historial y analítica.

---

## 17. Futuras mejoras

- Agregar Playwright para páginas con JavaScript.
- Agregar PostgreSQL para historial en ambientes productivos.
- Agregar autenticación de usuarios internos.
- Agregar evaluación automática de calidad de respuestas.
- Agregar observabilidad con logs estructurados.
- Agregar exportación de analítica a CSV.
- Agregar despliegue opcional en la nube.
- Agregar caché para respuestas frecuentes.
- Agregar control de duplicados más avanzado en scraping.
- Agregar evaluación de relevancia de documentos recuperados.

---

## 18. Pruebas

Ejecutar pruebas:

```bash
pytest
```

---

## 19. Comandos útiles

Scraping desde script:

```bash
python scripts/scrape.py
```

Indexación desde script:

```bash
python scripts/ingest.py
```

Reset de datos locales:

```bash
python scripts/reset_data.py
```

---

## 20. Supuestos asumidos

- El sitio objetivo es `https://www.bbva.com.co/`.
- El sistema se ejecuta completamente en local mediante Docker Compose.
- El modelo generativo se descarga desde Hugging Face.
- El scraping se limita a un número configurable de páginas para evitar sobrecargar el sitio.
- La interfaz prioriza funcionalidad y claridad sobre diseño visual avanzado.
- El historial se persiste en SQLite por simplicidad y reproducibilidad local.