#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
App initializing script.

"This script runs both the backend (Flask) and frontend (Streamlit) 
servers concurrently using threads."
"""

import subprocess
import threading


def run_flask():
    """
    Runs the Flask application using subprocess.
    """
    subprocess.run(["python", "-m", "app.flask_app"])


def run_streamlit():
    """
    Runs the Streamlit application using subprocess.
    """
    subprocess.run(["streamlit", "run", "./app/main.py"])


if __name__ == "__main__":
    """
    Runs both Flask and Streamlit applications in parallel using threads.
    """
    # Create a thread for running the Flask application
    flask_thread = threading.Thread(target=run_flask)

    # Create a thread for running the Streamlit application
    streamlit_thread = threading.Thread(target=run_streamlit)

    # Start the Flask thread
    flask_thread.start()

    # Start the Streamlit thread
    streamlit_thread.start()

    # Wait for both threads to complete
    flask_thread.join()
    streamlit_thread.join()
