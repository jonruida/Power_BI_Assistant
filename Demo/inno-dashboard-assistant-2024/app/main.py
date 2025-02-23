#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
Power BI AssistantSuite Streamlit App Configuration.

This script sets up the front-end of the Power BI Suite application using Streamlit. 
It allows users to navigate between different pages including:
- Home
- Report Generator
- Assistant
- Update Data (if enabled)

It also configures the sidebar navigation and checks if the "Update Data" page should 
be included based on an environment variable.
"""

import os
from typing import List

import streamlit as st

# Initialize the default page state in the session
if "page" not in st.session_state:
    st.session_state.page = "home"

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="Power BI Suite", layout="wide", initial_sidebar_state="expanded"
)

# Read the variable from .env
update_data_enabled: bool = os.getenv("UPDATE_DATA_PAGE", "False") == "True"

# List of available pages
pages: List[st.Page] = [
    st.Page("home.py", title="Home", icon=":material/home:"),
    st.Page(
        "report_generator.py",
        title="Report Generator",
        icon=":material/lab_profile:",
    ),
    st.Page("assistant.py", title="Assistant", icon=":material/forum:"),
]

# Add 'Update Data' page if enabled in the .env file
if update_data_enabled:
    pages.append(
        st.Page("update_data.py", title="Update Data", icon=":material/update:")
    )


# Function to run the navigation in the sidebar
def run_navigation(pages: List[st.Page]) -> None:
    """
    Renders the sidebar navigation for the Streamlit app.

    Args:
        pages (List[st.Page]): List of pages to be included in the sidebar navigation.

    Returns:
        None
    """
    pg = st.navigation(pages, position="sidebar")
    pg.run()


# Create and run the navigation in the sidebar
run_navigation(pages)
