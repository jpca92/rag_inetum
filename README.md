# RAG Banking Assistant

Sistema RAG local con web scraping, base vectorial, historial conversacional persistente, analítica de conversaciones e interfaz web.

El caso de uso simula un asistente interno que responde preguntas sobre información publicada en el sitio de un banco, inicialmente configurado para `https://www.bbva.com.co/`.

## Estado inicial

Este repositorio corresponde a una prueba técnica para construir un sistema RAG en Python que corre localmente.

## Objetivos principales

- Extraer información de un sitio web bancario mediante web scraping.
- Almacenar datos crudos y limpios en local.
- Indexar contenido en una base vectorial.
- Exponer una interfaz conversacional.
- Mantener historial conversacional por sesión.
- Agregar analítica básica sobre las conversaciones.
- Dockerizar el proyecto completo.

## Stack propuesto

- Python
- FastAPI
- Streamlit
- ChromaDB
- Sentence Transformers
- Hugging Face Transformers
- SQLite
- Docker Compose

## Ejecución

