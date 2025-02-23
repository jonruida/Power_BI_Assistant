#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""Power BI Assistant Suite App Home streamlit page configuration.

This script sets up the front-end of Power BI Assistant Suite Home page using 
Streamlit. It allows users to navigate to chatbot 
assistant page or report generator page.
"""

import base64

import streamlit as st


# Function to convert an image to base64 format
@st.cache_data
def get_img(file: str):
    """
    Converts an image file to a base64 encoded string.

    Args:
        file (str): The path to the image file.

    Returns:
        str: The base64 encoded image string.
    """
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Local path for the background image
local_image_path = "./assets/Fondo_home.png"
img = get_img(file=local_image_path)

# Combined styles for the page
combined_style = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img}"); 
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 100vh;
}}
.title-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 15vh; /* Adjust the height as needed */
}}
h1 {{
    display: inline-block;
    color: #f5eef8;
    font-size: 6vw;
    text-align: center;
    padding: 10px;
    border-radius: 10px;
}}
.button-container {{
    display: flex;
    justify-content: center;
    margin-top: 50px;
}}
.button {{
    width: 90%;
    padding: 20px;
    font-size: 3vw;
    text-align: center;
    margin: 0 10px;
}}
.logo-container {{
    display: flex;
    justify-content: center;
    margin-top: 30px;
}}
.logo {{
    width: 400px;  /* Increased logo size by 400% */
    height: auto;
}}
</style>
"""

# Apply the styles to the Streamlit page
st.markdown(combined_style, unsafe_allow_html=True)

# Page title
st.markdown(
    "<div class='title-container'><h1>Power BI Suite</h1></div>",
    unsafe_allow_html=True,
)

# Create columns for the buttons
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

# Button styles
button_style = """
<style>
    .button {
        display: inline-block;
        padding: 0.6em 1.2em;
        font-size: 18px;
        color: #333333;  /* Black text color */
        background-color: #f5f5f5;  /* Off-white background */
        border: 1px solid #dcdcdc;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
        margin-top: 50px;  /* Additional space below */
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }
    .button:hover {
        background-color: #e0e0e0;  /* Hover background color */
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
    }
</style>
"""

# Insert the button style into the app
st.markdown(button_style, unsafe_allow_html=True)

# Styled buttons inside columns
with col2:
    st.markdown(
        '<a href="/assistant" target="_self" class="button">Chat Assistant</a>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        '<a href="/report_generator" target="_self" class="button">Report Generator</a>',
        unsafe_allow_html=True,
    )

# Path to the logo and its base64 conversion
logo_path = "./assets/logo.png"
logo_img = get_img(file=logo_path)

# HTML to display the logo beneath the buttons
st.markdown(
    f"""
<div class='logo-container'>
    <img src="data:image/png;base64,{logo_img}" class="logo" alt="Logo">
</div>
""",
    unsafe_allow_html=True,
)
