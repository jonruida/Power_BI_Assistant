#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit

"""
Power BI Assistant Chatbot streamlit page configuration.

This script sets up the front-end of the Power BI Assistant Chatbot using 
Streamlit, providing the user interface for interacting with the assistant. 
It allows users to query reports, retrieve insights, communicating with backend 
components based in a chatbot powered with Qdrant for vector database management 
and llama-3 models to generate dynamic responses based on user input.
"""

import requests
import streamlit as st


def on_card_button_click(prompt: str) -> None:
    """
    Updates the session state to store the prompt and hides the cards.

    Args:
        prompt (str): The prompt to be set in the session state.
    """
    if not isinstance(prompt, str):

        raise TypeError(
            f"Expected 'prompt' to be a string, but got {type(prompt)}."
        )

    st.session_state.card_prompt = prompt
    st.session_state.show_cards = False


# Define the greeting and description text
saludo_asistente = (
    "👋 Hola, soy el asistente de Power BI. ¿En qué puedo ayudarte?"
)
descripcion_asistente = (
    "Estoy diseñado para mejorar la eficiencia en el análisis de informes y "
    "dashboards. Mis principales funciones incluyen la asistencia en la búsqueda "
    "de datos, la detección de anomalías, y la extracción de insights relevantes. "
    "¡Estoy aquí para ayudarte a sacar el máximo provecho de tus datos!"
)

# Display greeting and assistant description
st.markdown(
    f"<h2 style='text-align: left;'>{saludo_asistente}</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<h5 style='text-align: left;'>{descripcion_asistente}</h5>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<h3 style='text-align: left;'>Aquí hay algunas sugerencias:</h3>",
    unsafe_allow_html=True,
)

st.sidebar.header("Filtro")
response = requests.get("http://localhost:5001/get_reports")
if response.status_code == 200:
    informes = response.json().get("report_ids", [])
else:
    informes = ["Error al obtener informes"]
informes_contexto = informes.copy()
informes.insert(0, "Todos los informes")
informe_seleccionado = st.sidebar.selectbox(
    "Selecciona un informe:", informes, index=0
)

st.session_state["informe_seleccionado"] = informe_seleccionado
st.sidebar.write(f"Informe seleccionado: {informe_seleccionado}")

st.sidebar.header("Modo de Funcionamiento")

# Sidebar configuration slider
configurations = [
    "Max Speed",          # Quickest configuration
    "Efficient",          # Balanced configuration
    "Optimized",          # Current configuration
    "High Precision",     # High accuracy configuration
    "Max Accuracy",       # Most precise configuration
]

# Mapeo de descripciones según configuración
rendimiento = {
    "Max Speed": "Ideal para preguntas básicas",
    "Efficient": "Equilibrio entre rapidez y detalle",
    "Optimized": "Configuración recomendada para casos generales",
    "High Precision": "Recomendado para preguntas analíticas",
    "Max Accuracy": "Perfecto para casos complejos que requieren un amplio contexto"
}

# Usar `format_func` para mostrar íconos según configuración
selected_config = st.sidebar.select_slider(
    "Velocidad vs Exactitud:",
    options=configurations,
    value="Optimized",  # Valor predeterminado
    format_func=lambda x: "🚀" if x == "Max Speed" else "🧠" if x == "Max Accuracy" else "",
)

# Mostrar configuración seleccionada con descripción
st.sidebar.write(f"**{selected_config}**: {rendimiento[selected_config]}")

# Check if the assistant context has been sent
if "contexto_asistente" not in st.session_state:
    st.session_state.contexto_asistente = True
    # Create the context message
    mensaje_contexto = (
        saludo_asistente
        + descripcion_asistente
        + " Las secciones de informes disponibles son: "
    )

    # Add the report names to the context message
    mensaje_contexto += ", ".join(informes_contexto)

    # Send the message to the backend and get a response
    response = requests.post(
        "http://localhost:5001/query",
        json={
            "query": mensaje_contexto,
            "informe_seleccionado": informe_seleccionado,
            "informes_disponibles": informes,
            "configuration": selected_config, 
        },
    )


chat_col = st.columns(1)[0]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Escribe tu consulta aquí...")
card_prompt = st.session_state.get("card_prompt", None)

if prompt or card_prompt:
    if card_prompt:
        prompt = card_prompt
        st.session_state.card_prompt = None

    informe_seleccionado = st.session_state.get(
        "informe_seleccionado", "Todos los informes"
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the query to the assistant
    with st.chat_message("assistant"):
        response = requests.post(
            "http://localhost:5001/query",
            json={
                "query": prompt,
                "informe_seleccionado": informe_seleccionado,
                "informes_disponibles": informes,
                "configuration": selected_config, 

            },
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result["response"]

            # Eliminar las comillas al final hasta un máximo de 3 veces
            for _ in range(3):
                if not response_text.endswith((".", ":", "?", "!")):
                    response_text = response_text[:-1]

            # Mostrar y agregar el texto procesado
            st.markdown(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
        else:
            st.error("Error getting response.")
    st.session_state.show_cards = False

# Show cards for options
if "show_cards" not in st.session_state:
    st.session_state.show_cards = True

if st.session_state.show_cards:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button(
            "¿A qué secciones de Power BI tengo acceso?",
            key="btn1",
            on_click=lambda: on_card_button_click(
                "Nombres de los informes disponibles"
            ),
        )

    with col2:
        st.button(
            f"¿Qué información hay en la sección {informes[2]}?",
            key="btn3",
            on_click=lambda: on_card_button_click(f"¿Que información hay en el informe {informes[2]}?"),
        )

    with col3:
        st.button(
            f"¿Donde puedo encontrar el KPI de nivel de backlog?",
            key="btn2",
            on_click=lambda: on_card_button_click(
                f"¿Donde puedo encontrar el KPI de nivel de backlog?'"
            ),
        )

    # Adjust button width style
    st.markdown(
        """
        <style>
            .stButton > button {
                width: 100%;
                height: 60px;
                font-size: 16px;
                margin: 10px;
                text-align: left;  /* Align text to the left */
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
