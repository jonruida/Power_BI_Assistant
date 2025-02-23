# Power BI Assistant

This repository contains two implementations of a Power BI Assistant designed to analyze dashboards, generate automatic reports, and provide insights using state-of-the-art AI technologies.

## Overview

The project includes two versions:

### 1. **Polished Version - OpenAI API with ChatGPT-4**
Located in the `./Demo` directory, this implementation utilizes:
- **OpenAI GPT-4**: For natural language understanding and insights generation.
- **OpenAI Embeddings**: To power semantic search and improve the query results.

This version is fully functional making it the recommended choice for production use.

---

### 2. **Functional Version - Groq API with Llama 3.3**
Located in the `./Llama3` directory, this version employs:
- **Groq API** with **Llama 3.3** and **local embeddings**: An alternative large language model for generating insights and reports.

While this version is operational, there are pending improvements:
- **Code Commentary FIX**: Adjustments needed for adapt code commentaries from OpenAI version to Llama version.
- **Secret Management**: Requires further refinement to handle Groq API's access token.

---

## Project Structure

- **`./Demo`**: Polished version using OpenAI API with GPT-4.
- **`./Llama3`**: Functional version using Groq API with Llama 3.3.
- **`./Research`**: Documented experiments and research made during the initial phase of the project, includes not completed ETL pipelines.


## Features

### Shared Features:
- **Dashboard Analysis**: Extracts insights from Power BI dashboards.
- **Automatic Reports**: Generates concise and detailed summaries.
- **Semantic Search**: Enables natural language queries about dashboards.


---

## Installation and Usage

For setup instructions, refer to the individual README files in the respective directories:
- [OpenAI Version Setup](./Demo/inno-dashboard-assistant-2024/README.md)
- [Llama 3.3 Version Setup](./Llama3/inno-dashboard-assistant-2024/README.md)

---

## Future work

- The ETL process automation is still pending. This includes addressing a bug:

    [FIX] Selenium checkbox unselection 
    Description: Selenium fails to unselect checkboxes.
    Additionally, the access strategy for Power BI workspaces has yet to be defined, as this decision could significantly influence the overall ETL automation approach.