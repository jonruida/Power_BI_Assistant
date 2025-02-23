#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
Streamlit application for interactive report generation.

This script enables users to:
- Select a report from available options fetched via an API.
- Choose a specific date for the selected report.
- Generate a report in detailed or summarized formats.
- Provide custom suggestions to include in the generated report.
- Download the generated report as a PDF.

The app uses custom styling and integrates Markdown-to-PDF conversion.
"""

import base64
import io
import json
import time

import requests
import streamlit as st
from markdown_pdf import MarkdownPdf, Section


@st.cache_data
def string_to_int_ascii(s: str) -> int:
    """
    Converts a string to the sum of its ASCII values.

    Args:
        s (str): Input string.

    Returns:
        int: Sum of ASCII values of the characters in the string.
    """
    return sum(ord(char) for char in s)


def get_img(file: str):
    """
    Encodes an image file to a base64 string.

    Args:
        file (str): Path to the image file.

    Returns:
        str: Base64-encoded image string.
    """
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def convert_markdown_to_pdf(markdown_content: str):
    """
    Converts Markdown content to a PDF file.

    Args:
        markdown_content (str): Content in Markdown format.

    Returns:
        io.BytesIO: Buffer containing the generated PDF.
    """
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(markdown_content))
    pdf.meta["title"] = "Report"
    pdf.meta["author"] = "Report Author"
    pdf_buffer = io.BytesIO()
    pdf.save(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer


def clean_text(text: str) -> str:
    """
    Cleans text by replacing incorrect characters with the correct ones.

    Args:
        text (str): Input text to clean.

    Returns:
        str: Cleaned text.
    """
    replacements = {
        "Ã³": "ó",
        "Ã¡": "á",
        "Ã­": "í",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã¨": "è",
        "Ã©": "é",
        "Ã“": "Ó",
        "Ã": "Á",
        "Ã": "Í",
        "Ãš": "Ú",
        "Ã‰": "É",
        "â": "–",
        "â": "—",
        "â¬": "€",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    if not text.startswith("# "):
        text = "# Report\n\n" + text

    return text


# Path to the background image
local_image_path = "./assets/Fondo_reportes.png"
img = get_img(file=local_image_path)

# Custom CSS styling for Streamlit
combined_style = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    background-repeat: no-repeat;
    background-color: white;  
}}
h1 {{
    text-align: center;
    color: #524e57;  
    margin-top: -50px;
    font-size: 4vw;
}}
.content-container {{
    padding: 2vw;
    background-color: white; 
    border-radius: 10px;
    color: #808080;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    max-height: 80vh;
    overflow-y: auto;
}}
.stButton {{
    width: 40%;
    margin: 2vw auto;
}}
</style>
"""
# Path to the logo and its base64 conversion
logo_path = "./assets/logo_2.png"
logo_img = get_img(file=logo_path)

# HTML and CSS to position the logo proportionally to the screen size
st.markdown(
    f"""
<style>
.logo-container {{
    position: absolute;
    top: -3vh; /* Proporcional a la altura de la ventana */
    right: 0vw; /* Proporcional al ancho de la ventana */
    z-index: 1000;
}}
.logo {{
    width: 14vw; /* Tamaño proporcional al ancho de la ventana */
    height: auto;
}}
</style>
<div class='logo-container'>
    <img src="data:image/png;base64,{logo_img}" class="logo" alt="Logo">
</div>
""",
    unsafe_allow_html=True,
)
# Apply custom CSS
st.markdown(combined_style, unsafe_allow_html=True)
st.markdown("<h1>Report Generator</h1>", unsafe_allow_html=True)

# Column layout for the Streamlit interface
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    response = requests.get("http://localhost:5001/get_reports")
    if response.status_code == 200:
        informes = response.json().get("report_ids", [])
    else:
        informes = ["Error fetching reports"]

    informes.insert(0, "Todos los informes")
    informe_seleccionado = st.selectbox("Selecciona un informe:", informes, index=0)
    st.session_state["informe_seleccionado"] = informe_seleccionado

    if informe_seleccionado != "Todos los informes":
        report_id_int = string_to_int_ascii(s=informe_seleccionado)
        response = requests.get(
            f"http://localhost:5001/get_dates_by_id?id={report_id_int}"
        )

        if response.status_code == 200:
            fechas = response.json().get("dates", [])
            try:
                data = json.loads(fechas)
                dates = data.get("dates", [])
            except json.JSONDecodeError:
                dates = ["Error al procesar las fechas"]
        else:
            dates = ["Error al obtener las fechas"]

        fecha_seleccionada = st.selectbox("Selecciona una fecha:", dates)

        formato_extensivo = st.checkbox("Formato detallado", value=False)
        formato = "Detallado" if formato_extensivo else "Resumido"
        st.write(f"Formato seleccionado: {formato}")

        sugerencia = st.text_area(
            "Escribe una sugerencia o solicitud para el informe:", height=100
        )

        if st.button("Generar informe"):
            payload = {
                "report_id": informe_seleccionado,
                "fecha": fecha_seleccionada,
                "formato": formato,
                "query": sugerencia,
            }

            # Display a progress bar
            progress_bar = st.progress(0)
            t_1 = 0.15 if formato == "Resumido" else 0.35
            for i in range(100):
                time.sleep(t_1)
                progress_bar.progress(i + 1)

            # Submit the request to generate the report
            response = requests.post(
                "http://localhost:5001/generate_report", json=payload
            )

            if response.status_code == 200:
                report_content = response.text
                if report_content:
                    st.session_state["content"] = clean_text(report_content)
                else:
                    st.error("El informe generado está vacío.")
            else:
                st.error(
                    "Error al generar el informe. Verifique los parámetros e intente nuevamente."
                )
    else:
        st.write("Por favor selecciona un informe para ver las fechas disponibles.")

with col2:
    if "content" in st.session_state:
        # Display the generated content
        st.markdown(
            f"<div class='content-container'>{st.session_state['content']}</div>",
            unsafe_allow_html=True,
        )

        # Convert Markdown content to PDF
        pdf_content = convert_markdown_to_pdf(st.session_state["content"])

        # Download button for the PDF report
        st.download_button(
            label="Descargar informe como PDF",
            data=pdf_content,
            file_name="report.pdf",
            mime="application/pdf",
        )
