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

    Add your OpenAI API KEY:

    OPENAI_API_KEY= xxxxxxxxxxxxxxxxxxxxxxxxxx 

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

    30 seconds after container started (necessary to ensure proper Qdrant service initilization), the application will be available at http://localhost:8501.
    
    --**Important:** In order to use the app first time, it's necessary to upload data by choosing all colecctions in the update data page--  


## Security

A general **vulnerability audit report** is available in [**General Report**](./tests/security/general_report.md). This audit includes an analysis of the project's dependencies and static code, as well as a scan of Docker images. It highlights any vulnerabilities detected and categorizes them by severity and confidence level. Tools such as **pip-audit**, **bandit**, **semgrep**, and **Docker Scout** were used in the audit.

## Using the Application
Automatic Reports: Access the main screen at http://localhost:8501 to generate automatic reports based on Power BI dashboards.

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

1. ### [x] [FIX] Incorrect collections (Medium)  
   **Description:** Incorrect collections were being returned.  
   - #### a.  [x] Fix by uploading the Qdrant library properly.  
   - #### b.  [x] Instruct the context tool LLM not to use the `'''json'''` character when returning collections and n_values to the parser.  

2. ### [x] [FIX] Flashrank library troubles downloading the model from HF repos (Medium)  
   **Description:** Flashrank library has trouble downloading the model from HuggingFace repositories.  
   - #### a.  [x] Create a volume to make models persistent.  
   - #### b.  [x] Map the volume to allow using new rerank models.  

3. ### [x] [FEATURE] Load LLM Rerank before using it to reduce response time (Easy)  
   **Description:** Achieved in the previous step.  

4. ### [x] [FEATURE] Enable velocity/accuracy selector by configuring parameters (Medium)  
   **Description:** Configure parameters such as LLM models, retriever methods, rerank cross-encoder models, collection access, and custom collections.  
   #### **Parameters Configured**:  
   - a. Retriever method (Vectorstore search/SelfQuerying).  
   - b. Rerank cross-encoder model (Tiny/Small).  
   - c. Rerank model max_length.  
   - d. Collection access and N_values.  
   - e. Custom collection and N_value tool.  

5. ### [ ] [FIX] Substitute ascitoint function with a hash function (Easy)  
   **Description:** The function is intended to create unique ids and produces collisions. 

6. ### [x] [FIX] Memory issue (Easy/Medium)  
   **Description:** The system mixes topics in responses when using information from previous searches.  
   - ####  a. [x] Set `ReqConversationBufferWindowMemory.return_messages` parameter to "False".   

7. ### [x] [FIX] Agent Stop due to iteration limit (Medium)  
   **Description:** The agent stops prematurely because of limit iterations.  
   **Completion date:** 2/12/2024  
   - #### a.  [x] Fix RAG search-related bugs.  
   - #### b.  [x] Set `early_stopping_method` parameter to "generate" to iterate Agent.executor one more time to generate an answer with previous info, when it stops due to time or iteration limit.  

8. ### [ ] [FEATURE] Reorganize function definitions (Easy)  
   **Description:** Move functions like `get_reports`, `det_dates_by_ids`, and `string_to_ascii` to a utility file.  

9. ### [ ] [FIX] Report generated Markdown title issue (Easy)  
   **Description:** The report's generated Markdown title isn’t displayed in the correct format.  

10. ### [ ] [FEATURE] Manage image vulnerabilities (High/Medium)  
    **Description:** Address high and medium image vulnerabilities.  

11. ### [ ] [FEATURE] Improve Context Tool for RAG results (Medium)  
    **Description:** Enhance the Context Tool to improve RAG search results.  
    - #### a.  [x] Tune the prompt for the custom collection tool.  
    - #### b.  [ ] Implement further improvements.  

12. ### [ ] [FIX] Selenium checkbox unselection (Medium)  
    **Description:** Selenium fails to unselect checkboxes.  

13. ### [ ] [FEATURE] Automate ETL process (Difficult)  
    **Description:** Automate the ETL process for better efficiency.  

14. ### [ ] [FEATURE] Speed up embedding and upload (Medium)  
    **Description:** Current process is too slow; optimize for speed.  

15. ### [ ] [FEATURE] Normalize and format Qdrant vectors (Easy/Medium)  
    **Description:** Ensure all content in Qdrant vectors is Unicode-formatted.  

16. ### [ ] [FEATURE] Improve table ingestion for large tables (Easy/Medium)  
    **Description:** Enhance table retrieval to detect all values, especially for large tables.  

17. ### [ ] [FEATURE] Complete tables with captured JSONs (Medium/Difficult)  
    **Description:** Fill in tables with data captured from JSONs.  

18. ### [ ] [FEATURE] Test GPT models and parameters (Medium)  
    **Description:** Experiment with different GPT models, temperatures, and parameters.  

19. ### [ ] [FEATURE] Set up a relational database (Medium)  
    **Description:** Replace Qdrant storage for names, dates, etc., with a relational database.  

20. ### [ ] [FEATURE] Include tips in a database (Medium/Difficult)  
    **Description:** Add tips from chat histories or theory to a database for improving interpretation.  



