#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
Data_upload page deploying script.

"This script configurates Data_upload Streamlit page 
intended for temporary use."
"""

import json

import requests
import streamlit as st

# Update data
st.sidebar.header("Update Data")
update_type = st.sidebar.selectbox(
    "Select update type:",
    ["all", "tabular", "report_summary", "text_pages", "metadata"],
)

if st.sidebar.button("Update Data"):
    """
    Sends a request to update data based on the selected update type.
    The response is displayed on the sidebar.
    """
    # Show the spinner while waiting for the response
    with st.spinner("Updating data... Please wait."):
        response = requests.post(
            "http://localhost:5001/update_data",
            json={"update_type": update_type},
        )
        result = response.json()

    # Display the result of the update operation
    st.sidebar.success(json.dumps(result, indent=2))
