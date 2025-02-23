# Power BI Assistant

This project provides an advanced Power BI assistant designed to generate automatic reports and respond to queries about the company’s dashboards. The application runs in a Docker environment with containers for **Qdrant** (vector database) and **Python 3.11-slim** for the backend.

## Features

- **Automatic Reports**: Generates summaries and detailed analysis from Power BI dashboards.
- **Query Chatbot**: Responds to questions about dashboards using processed and stored data in the vector database.
- **Dynamic Configuration**: Enables an additional data update screen in Streamlit by setting an environment variable.

## Setup and Installation

This project uses Docker Compose to configure and launch the necessary containers. Make sure you have **Docker** and **Docker Compose** installed.

### Installation Steps

1. Clone this repository:
   ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2. Configure the environment variables:

    Create a .env file in the project’s root directory. For first use, define th variable UPDATE_DATA_PAGE=true to enable the data update screen in Streamlit:

    UPDATE_DATA_PAGE=True

    Add your Groq API KEY manually in:
    - Llama3\inno-dashboard-assistant-2024\src\services\agent\core.py 
    - Llama3\inno-dashboard-assistant-2024\src\services\llm\call_llm.py
    - Llama3\inno-dashboard-assistant-2024\src\services\retrievers\selfq_retrievers.py

    

3. Build and start Docker container to deploy the app:

    ```bash
      ./run_assistant.sh
    ```
    
    If you are using Linux, you may need to grant execution permissions before: 

    ```bash
      chmod +x run_assistant.sh
    ```

    
    This will create and run the container and the app:

    Container's principal features:

    - Qdrant: Vector database for storing and querying Power BI data.(availabe at localhost:6333)

    - Python 3.11-slim: Environment where the main application runs.

    30 seconds after container started (necessary to ensure proper Qdrant service initilization), the application will be available at http://localhost:8601.
    
    --**Important:** In order to use the app first time, it's necessary to upload data by choosing all colecctions in the update data page--  


## Security

A general **vulnerability audit report** is available in [**General Report**](./tests/security/general_report.md). This audit includes an analysis of the project's dependencies and static code, as well as a scan of Docker images. It highlights any vulnerabilities detected and categorizes them by severity and confidence level. Tools such as **pip-audit**, **bandit**, **semgrep**, and **Docker Scout** were used in the audit.

## Using the Application
Automatic Reports: Access the main screen at http://localhost:8601 to generate automatic reports based on Power BI dashboards.

Dashboard Queries: Use the integrated chatbot to ask questions about the available data in the reports.

If UPDATE_DATA_PAGE is set to True, an additional screen will be available for updating data extracted and transformed from Power BI.

## Prepared Files
This project includes files generated from the extraction and transformation process of Power BI data. These files are used to generate reports and supply the chatbot with updated information about **mock dashboards**.

## Technologies Used

- Python 3.11-slim
- Streamlit
- Qdrant - Vector database for data storage and retrieval
- Docker
- LLM

Enjoy using the Power BI Assistant to streamline your dashboard analysis!
## TODOs: Features and Fixes
Same FIX-LIST than ./Demo/README.md, with these two additional fixes.
- **Code Commentary FIX**: Adjustments needed for adapt code commentaries from OpenAI version to Llama version.



