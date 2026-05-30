import os
import uuid

import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


st.set_page_config(
    page_title="RAG Banking Assistant",
    page_icon="🏦",
    layout="wide",
)


st.title("🏦 RAG Banking Assistant")


if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4().hex[:8]}"


if "messages" not in st.session_state:
    st.session_state.messages = []


tab_chat, tab_admin, tab_analytics = st.tabs(
    [
        "Chat",
        "Administración",
        "Analítica",
    ]
)


with tab_chat:
    st.subheader("Asistente conversacional")

    session_id = st.text_input(
        "Session ID",
        value=st.session_state.session_id,
    )

    st.session_state.session_id = session_id

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Haz una pregunta sobre el contenido scrapeado..."
    )

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Consultando el sistema RAG..."):
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "session_id": session_id,
                        "question": question,
                    },
                    timeout=300,
                )

                response.raise_for_status()
                data = response.json()

            answer = data["answer"]
            st.markdown(answer)

            if data.get("sources"):
                with st.expander("Fuentes recuperadas"):
                    for source in data["sources"]:
                        st.markdown(
                            f"**{source.get('title', 'Sin título')}**"
                        )
                        st.caption(source.get("url", ""))
                        st.write(source.get("preview", ""))

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


with tab_admin:
    st.subheader("Carga e indexación")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ejecutar scraping"):
            with st.spinner("Scrapeando sitio web..."):
                response = requests.post(
                    f"{API_BASE_URL}/scrape",
                    timeout=300,
                )

                response.raise_for_status()
                st.success(response.json())

    with col2:
        if st.button("Indexar documentos"):
            with st.spinner("Indexando documentos en Chroma..."):
                response = requests.post(
                    f"{API_BASE_URL}/ingest",
                    timeout=300,
                )

                response.raise_for_status()
                st.success(response.json())

    st.info(
        "Flujo recomendado: primero scraping, luego indexación, después usar el chat."
    )


with tab_analytics:
    st.subheader("Métricas del histórico conversacional")

    if st.button("Actualizar métricas"):
        summary = requests.get(
            f"{API_BASE_URL}/analytics/summary",
            timeout=60,
        ).json()

        questions = requests.get(
            f"{API_BASE_URL}/analytics/questions",
            timeout=60,
        ).json()

        sources = requests.get(
            f"{API_BASE_URL}/analytics/sources",
            timeout=60,
        ).json()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Sesiones", summary["total_sessions"])
        col2.metric("Mensajes", summary["total_messages"])
        col3.metric("Preguntas", summary["total_questions"])
        col4.metric("Latencia prom. ms", summary["average_latency_ms"])

        st.markdown("### Preguntas frecuentes")
        questions_df = pd.DataFrame(questions["top_questions"])
        st.dataframe(questions_df, use_container_width=True)

        st.markdown("### Fuentes más recuperadas")
        sources_df = pd.DataFrame(sources["top_sources"])
        st.dataframe(sources_df, use_container_width=True)