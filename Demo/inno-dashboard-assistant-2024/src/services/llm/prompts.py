#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This script defines prompts for an AI agent and a Retrieval-Augmented Generation (RAG) system.

get_character_prompt: Defines the AI agent's behavior, guiding interactions and tool invocation.
get_context_prompt: Selects relevant database collections for responding to Power BI report queries.
report_prompts: Prompts for getting a markdown format report, sumarized and extensive format.
"""
from typing import List


def get_character_prompt() -> str:
    """
    Generates the character prompt for the agent, including the available tools.

    This prompt is sourced from the LangChain library, specifically from the
    `hwchase17/react-chat` model on the Smith platform (https://smith.langchain.com/hub/hwchase17/react-chat).
    It is designed for creating a conversational agent (chatbot) that interacts with users
    in a natural and coherent manner, while also allowing the use of external tools if necessary.
    The agent decides whether to use a tool based on the context of the conversation and generates
    responses accordingly.

    The prompt follows a structured format where the assistant can evaluate whether to use a tool,
    execute the corresponding action, and respond with the result. If no tool is needed, the assistant
    simply provides the answer directly to the user. The format includes placeholders for tools,
    conversation history, new input, and the agent's scratchpad to guide its reasoning process.

    Returns:
        str: The character prompt, ready for use with the conversational agent.

    Example usage:
        character_prompt = get_character_prompt()
    """
    character_prompt = (
        "Assistant is a large language model trained by OpenAI.\n\n"
        "Assistant is designed to be able to assist with a wide range of tasks, "
        "from answering simple questions to providing in-depth explanations and "
        "discussions on a wide range of topics. As a language model, Assistant is "
        "able to generate human-like text based on the input it receives, allowing "
        "it to engage in natural-sounding conversations and provide responses that "
        "are coherent and relevant to the topic at hand.\n\n"
        "Assistant is constantly learning and improving, and its capabilities are "
        "constantly evolving. It is able to process and understand large amounts of text, "
        "and can use this knowledge to provide accurate and informative responses to a "
        "wide range of questions. Additionally, Assistant is able to generate its own "
        "text based on the input it receives, allowing it to engage in discussions and "
        "provide explanations and descriptions on a wide range of topics.\n\n"
        "Overall, Assistant is a powerful tool that can help with a wide range of tasks "
        "and provide valuable insights and information on a wide range of topics. Whether "
        "you need help with a specific question or just want to have a conversation about "
        "a particular topic, Assistant is here to assist.\n\n"
        "TOOLS:\n"
        "------\n\n"
        "Assistant has access to the following tools:\n\n"
        "{tools}\n\n"
        "To use a tool, please use the following format:\n\n"
        "```\n"
        "Thought: Do I need to use a tool? Yes\n"
        "Action: the action to take, should be one of [{tool_names}]\n"
        "Action Input: the input to the action\n"
        "Observation: the result of the action\n"
        "```\n\n"
        "When you have a response to say to the Human, or if you do not need to use a tool, "
        "you MUST use the format:\n\n"
        "```\n"
        "Thought: Do I need to use a tool? No\n"
        "Final Answer: [your response here]\n"
        "```\n\n"
        "Begin!\n\n"
        "Previous conversation history:\n"
        "{chat_history}\n\n"
        "New input: {input}\n"
        "{agent_scratchpad}"
    )
    return character_prompt


def get_context_prompt(query: str) -> str:
    """
    Returns the context analysis prompt for collection selection in a RAG architecture.

    This function generates a dynamic prompt that assists in determining which collections
    should be used to provide the most accurate context for a given query within a
    Retrieval-Augmented Generation (RAG) system. The collections are optimized for different
    types of data in a database that contains information about Power BI reports, including
    dashboards, pages, charts, tables, KPIs, and more.

    The prompt is structured to help the system evaluate the user's query and decide which
    collection(s) to retrieve, based on the level of detail required for the query. The
    available collections are:

    - **report_names**: Report names, ideal for queries that require only report titles.
    - **element_names**: Index of elements in each report, useful for schema or element existence checks.
    - **upload_dates**: Dates when reports were updated, for queries about report update history.
    - **Report Summaries**: Concise summaries of individual reports, ideal for high-level overviews.
    - **Elements**: Detailed data on individual report components like charts, tables, and KPIs.
    - **Text Pages**: Complete text data from report pages, useful for in-depth section or page queries.

    The prompt outlines a sequential decision-making flow for selecting the minimal, most relevant
    collections to answer the query effectively. The process proceeds through a series of steps,
    where each step refines the selection of collections based on the user's query and its information needs.

    Args:
        query (str): The query string that the system needs to process and analyze for context selection.

    Returns:
        str: A formatted prompt string, ready to be used in a RAG system to determine the best collection(s).

    Example usage:
        context_prompt = get_context_prompt("When were the reports last updated?")

    Example Output:
        {
            "collections": [{"name": "upload_dates", "n": 10}]
        }

    The prompt will guide the system through the following steps:
    1. Assess the high-level information need (e.g., just report names or more detailed data).
    2. Determine if the query requires specific element names, upload dates, or other types of details.
    3. Based on the evaluation, the appropriate collections will be selected and the number of documents
       needed from each collection will be estimated.

    **Only the resulting JSON object should be returned without any additional explanation or text.**
    """
    context_prompt = (
        f"Given the query: '{query}', analyze the user's query to determine which collection(s) "
        f"should be used to provide the most accurate context. "
        f"The database contains information about Power BI reports, where each report is made up of dashboards, "
        f"organized into pages that contain elements such as charts, tables, and KPIs. "
        f"This database is part of a **Retrieve** system in a RAG (Retrieval-Augmented Generation) "
        f"architecture, where each collection is optimized to retrieve a limited number of relevant elements.\n\n"
        "- **report_names**: Contains only names of available reports, ideal for queries that only require "
        "report titles.\n"
        "- **element_names**: This collection stores only an index of elements in each report, allowing for "
        "quick retrieval of report schemas or confirmation of element existence without any data, "
        "value, or content.\n"
        "- **upload_dates**: Contains all dates when the reports were updated, suitable for queries that "
        "inquire about the report's upload or update history.\n"
        "- **Report Summaries**: Contains concise overviews of individual reports, organized by date, "
        "suitable for queries seeking general summaries of specific reports.\n"
        "- **Elements**: This collection provides detailed data on individual report components (charts, "
        "tables, KPIs), ideal for queries that target specific details within reports such as values or specific data.\n"
        "- **Text Pages**: Contains complete text data from each report’s pages, organized by date, and "
        "provides in-depth information for queries focused on specific sections or pages within dashboards.\n\n"
        "### Instructions:\n\n"
        "**Sequential Collection Selection Flow**:\n"
        "- Follow this sequence to select the most relevant collection(s) possible. By default, "
        "the number of documents are as follows; adjust as needed: report_names: 20, element_names: 2, "
        "upload_dates: 20, Report Summaries: 2, Elements: 3, Text Pages: 2.\n"
        "#### Step 1: High-Level Information Need\n"
        "- **Question**: Does the query require only report names(without any further data or value) or an index of available reports?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed, "
        "the less the better: `n` (based on typical response volume).\n"
        '    - Return `[{{"name": "report_names", "n": n}}]`, end process.\n'
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "#### Step 2: Element Names Need\n"
        "- **Question**: Does the query require only an index of element names (without any further data or value) within a report?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed, "
        "the less the better: `n` (based on expected elements).\n"
        '    - Add `{{"name": "element_names", "n": n}}` to the previous collection selection.\n'
        "    - **If more information is required such as KPI or element values, or further data**:\n"
        "      - Continue to the next step.\n"
        "    - **If no additional information is needed**:\n"
        "      - Return the collection list, end process.\n"
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "#### Step 3: Upload Dates Need\n"
        "- **Question**: Does the query require upload or update dates of reports?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed, the less the better: `n` (based on historical data).\n"
        '    - Add `{{"name": "upload_dates", "n": n}}` to the previous collection selection.\n'
        "    - **If more information is required**:\n"
        "      - Continue to the next step.\n"
        "    - **If no additional information is needed**:\n"
        "      - Return the collection list, end process.\n"
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "#### Step 4: Specific Element Information Need\n"
        "- **Question**: Does the query require specific values of specific KPIs, tables, charts or other visualizations? "
        "(e.g., charts, tables, or KPIs) within a report?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed starting from 3, the less the better: `n` (based on expected details).\n"
        '    - Return added `[{{"name": "Elements", "n": n}}]`, end process.\n'
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "#### Step 5: Report Summary Need\n"
        "- **Question**: Does the query require global context of a whole report section, "
        "usually to respond to complex questions?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed, the less the better: `n` (typically 1).\n"
        '    - Return added `[{{"name": "Report Summaries", "n": n}}]`, end process.\n'
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "#### Step 6: Page Summary Need\n"
        "- **Question**: Does the query require general context of a particular dashboard into a report section, "
        "in other words require detailed content or summaries from specific pages within a report?\n"
        "  - **If Yes**:\n"
        "    - Estimate the minimal number of documents needed, "
        "the less the better: `n` (based on number of pages required).\n"
        '    - Return added `[{{"name": "Text Pages", "n": n}}]`, end process.\n'
        "  - **If No**:\n"
        "    - Continue to the next step.\n\n"
        "3. **The response format should follow this structure**:\n"
        "Do not provide any JSON block notation or code formatting or further explanation in the answer."
        "Provided answer must only contain the dictionary as follows:"
        "{\n"
        '    "collections": [{"name": "<selected_collection_1>", "n": <number_of_documents_needed_1>}, '
        '{"name": "<selected_collection_2>", "n": <number_of_documents_needed_2>}]\n'
        "}\n\n"
        "### Examples:\n"
        "1. **Query**: 'What reports are available?'\n"
        '   **Answer**: {"collections": [{"name": "report_names", "n": 10}]}\n'
        "2. **Query**: 'When was the last report uploaded?'\n"
        '   **Answer**: {"collections": [{"name": "upload_dates", "n": 5}]}\n'
    )

    return context_prompt


"""
Prompts used to generate Markdown reports based on dashboard summaries.

- summarized_report_prompt: This prompt generates a brief and concise report that summarizes 
key metrics, insights, and notable observations from the dashboards.
- extensive_report_prompt: This prompt generates a more detailed report, suitable for longer 
dashboard summaries, spanning from 3 to 10 pages, including deeper analysis and recommendations.
"""

summarized_report_prompt = """
You are tasked with creating an informative report in Markdown format based on the provided
summaries of various dashboards. The report should be concise and focus on the key insights
derived from the data. Include the following sections:

1. **Title**
   - Title of the report

2. **Table of Contents**
   - Automatically generated based on the sections of the report.

3. **Introduction**
   - Brief overview of the purpose of the report.
   - Explanation of the dashboards being summarized.

4. **Dashboard Summaries**
   - For each dashboard summary provided, create a dedicated section that includes:
     - **Title of the Dashboard**
     - **Overview:** A brief description of the dashboard's purpose.
     - **Key Metrics:** Highlight the important KPIs or metrics visualized.
     - **Insights:** Summarize key insights derived from the dashboard, including any trends,
     anomalies, or notable observations.

5. **Conclusion**
   - Summarize the main findings from the dashboards.

Ensure that the Markdown is formatted attractively, with the use of headings, subheadings,
bullet points, and code blocks where necessary. Use appropriate Markdown syntax for links,
images, and tables to enhance readability, but don't include '''markdown''' in the beginning
and in the end.
"""

extensive_report_prompt = """
You are tasked with creating a comprehensive report in Markdown format based on the provided 
summaries of various dashboards. The report should be detailed and span from 3 to 10 pages, 
including the following sections:

1. **Title**
   - Title of the report

2. **Table of Contents**
   - Automatically generated based on the sections of the report.

3. **Introduction**
   - Brief overview of the purpose of the report.
   - Explanation of the dashboards being summarized.

4. **Dashboard Summaries**
   - For each dashboard summary provided, create a dedicated section that includes:
     - **Title of the Dashboard**
     - **Overview:** A brief description of the dashboard's purpose.
     - **Key Metrics:** Highlight the important KPIs or metrics visualized.
     - **Insights:** Summarize key insights derived from the dashboard, including any trends, 
     anomalies, or notable observations.
     - **Visualizations:** Include descriptions of significant visual elements (charts, graphs) 
     and their implications.
     - **Recommendations:** If applicable, provide actionable recommendations based on the 
     insights.

5. **Conclusion**
   - Summarize the main findings from the dashboards.
   - Discuss the overall implications for the business or project.

6. **Appendix (if needed)**
   - Any additional information, such as raw data or methodology used in analysis.

Ensure that the Markdown is formatted attractively, with the use of headings, subheadings, 
bullet points, and code blocks where necessary. Use appropriate Markdown syntax for links, images, 
and tables to enhance readability, but don't include '''markdown''' in the beginning and in the end.
"""


def get_summary_prompt(formato: str) -> str:
    """
    Returns the appropriate prompt to generate a report based on the specified format.

    The function selects between a prompt for a summarized (concise) report and a prompt for a
    detailed (extensive, multi-page) report, depending on the input format.

    Args:
        formato (str): The desired format for the report.
                       - "resumido" for a summarized (concise) report.
                       - Any other value for a detailed (extensive) report.

    Returns:
        str: The prompt that will guide the generation of the report, either summarized or detailed,
             in Markdown format.
    """
    if formato.lower() == "resumido":
        return summarized_report_prompt
    else:
        return extensive_report_prompt


def create_final_prompt(
        formato: str,
        query: str,
        doc_query: str,
        documents: List[str],
        language: str = "spanish",
) -> str:
    """
    Builds the final prompt to generate a report based on the provided inputs,
    including the format, query, document query, and retrieved documents.
    The final result is generated in the specified language.

    This function constructs a prompt by combining the appropriate summary prompt
    with the query and relevant documents. It returns the prompt as a formatted string.

    Args:
        formato (str): The desired format for the report, either "resumido" for a summarized report
                       or any other value for a detailed report.
        query (str): The specific query or request from the user related to the report.
        doc_query (str): The query or identifier for the documents being retrieved.
        documents (list): A list of documents or sections of a report retrieved for processing.
        language (str, optional): The language in which the report should be generated. The default value is "spanish".

    Returns:
        str: The final prompt built, formatted in Markdown with the relevant sections
             and in the requested language.
    """
    # Get the appropriate prompt
    prompt_to_use = get_summary_prompt(formato)

    # Build the prompt with the query logic
    prompt = [prompt_to_use]
    prompt.append("Documents retrieved:")

    for doc in documents:
        prompt.append(doc.page_content)

    prompt.append(
        "must generate the information in the following language (including all section subtitles):"
    )
    prompt.append(language)

    if query:
        prompt.append(
            f"You must take into account the user's request. User's request: {query}"
        )

    # Include the report ID and query date
    prompt.append(f"Querying for: {doc_query}")

    # Convert the list into a single string with line breaks between elements
    return "\n".join(prompt)
