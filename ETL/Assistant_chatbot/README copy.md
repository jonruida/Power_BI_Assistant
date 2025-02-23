# PowerBI Insights Generator

**PowerBI Insights Generator** is an advanced tool designed to automatically generate insightful reports and perform data queries from Power BI dashboards. Leveraging large language models (LLM), this project processes and analyzes the exported reports to deliver comprehensive insights and actionable answers.

## Project Scope

1. **Automated Report Generation**:
   - Utilize large language models (LLM) to transform exported Power BI dashboards into detailed, informative reports.

2. **Interactive QnA System**:
   - Develop a dynamic question and answer (QnA) feature that allows users to query the generated reports, with clear references to the original data tables for accurate and easy cross-referencing.


3. **Technologies**:
   - **Vector Databases**: For efficient data storage and querying.
   - **LangChain**: For advanced document and data processing.
   - **Prompt Engineering**: To optimize report generation and responses.
   - **Streamlit**: As a visualization tool to interact with reports and results.
   - **Flow Orchestration**: To manage the extraction and insertion of new data tables and keep the system up to date.

### Insights

- [PowerBI Oficial app](https://learn.microsoft.com/en-us/power-bi/create-reports/insights#considerations-and-limitations)

## Architecture

![Architecture Diagram](https://bitbucket.org/sdggroup/inno-dashboard-assistant-2024/raw/main/assets/ARCH_INTERN.png)

## Data Extraction

We explore several approaches for data extraction, including using Selenium with mitmproxy, scraping Power BI APIs, and other advanced techniques. Each approach has its own set of strategies and challenges.

### ExploredTechnologies Used

- **LLM (Large Language Models)**
- **LangChain**
- **Streamlit**
- **Vector Databases**
- **Selenium**
- **mitmproxy**

## Data Transformation

## Getting Started

1. **Environment Setup**:
   - Clone the repository: `git clone <repository URL>`
   - Install the required dependencies: `pip install -r requirements.txt`

2. **Running the Project**:
   - Follow the instructions in the configuration file to adjust parameters according to your needs.
   - Run the main script to start data processing and report generation.

## License


