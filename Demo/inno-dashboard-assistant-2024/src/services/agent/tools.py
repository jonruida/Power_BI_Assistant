#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
Tool definitions for agent query processing.

This module defines a set of tools that are used by the agent to process queries. 
These tools interact with a Qdrant database client and can be used for retrieving 
contextual information and data origins. The tools include the 'Context' tool to 
provide relevant information from the database and the 'Origin' tool to retrieve 
metadata such as the report's origin, location, or other relevant details.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Tuple

from langchain.agents import Tool
from src.services.llm.call_llm import call_llm
from src.services.llm.prompts import get_context_prompt
from src.services.retrievers.selfq_retrievers import (
    get_reports,
    setup_retrievers,
)
from src.services.retrievers.vector_store_retrievers import (
    setup_retrievers as setup_fast_retriever)
from src.utils.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(name=__name__)


def get_tools(
        qdrant_client: Any,config: str, informe_seleccionado: str = None, 
) -> List[Tool]:
    """
    Returns a list of tools that can be used by an agent.

    Args:
        qdrant_client (Any): The client to interact with the Qdrant database.

    Returns:
        List[Tool]: List of Tool objects for the agent to use.
    """
    tools = [
        Tool(
            name="Context",
            func=context(
                qdrant_client, informe_seleccionado, config
            ),  # Calling the context function
            description="Anytime further information is needed, or you don't have specific information from previus conversations, this tool provides it to answer the user's query.",
        ),
        Tool(
            name="Origin",
            func=origin(qdrant_client),  # Calling the origin function
            description="Use this tool if the user requests the location"
                        " or origin (page number, report title, dashboard title, etc.) "
                        "of data such as KPI values, tables, charts, visual elements,"
                        " or insights produced by the assistant.",
        ),
    ]
    return tools


def origin(qdrant_client: Any) -> Callable[[str], List[str]]:
    """
    Returns the origin tool for retrieving the source or location of data.

    Args:
        qdrant_client (Any): The client to interact with the Qdrant database.

    Returns:
        Callable[[str], List[str]]: A function that processes a query to get
        data origin information.
    """

    def origin_tool(query: str) -> List[str]:
        # Number of elements to retrieve
        n_values = {"Elements": 3}
        collections = [{"name": "Elements", "n": 3}]
        model = "ms-marco-MiniLM-L-12-v2"
        origin_retriever = setup_retrievers(
            qdrant_client=qdrant_client,
            collections=collections,
            n_values=n_values,
            model=model,
        )
        final_result = origin_retriever.invoke(input=query)

        # Append information about the origin of the requested element
        final_result.append(
            "This tool has returned all the information related to the origin of the requested element. "
            "Return which report section it belongs to, on which page of that report it is located, "
            "and the title it has on that dashboard."
        )
        final_result.append(
            "Must answer in the same language as the user's question."
        )

        return final_result

    return origin_tool

def context(
        qdrant_client: Any, informe_seleccionado: str = None, config: str = 'Optimized'
) -> Callable[[str], List[str]]:
    """
    Returns the context tool for retrieving relevant information based on a query.

    Args:
        qdrant_client (Any): The client to interact with the Qdrant database.
        informe_seleccionado (str = None): Name of the selected report used to implement Selfquerying metada filtering.
        config (str): Configuration to choose the type of retriever ('optimized', 'efficient', 'high_performance', 'accurate').

    Returns:
        Callable[[str], List[str]]: A function that processes a query to retrieve context-based information.
    """
    
    def context_tool(
            query: str, informe_seleccionado=informe_seleccionado, config=config
    ) -> List[str]:
        result = None
        names = None
        docs = query
        if informe_seleccionado != "Todos los informes":
            docs += f" filter results for the report {informe_seleccionado}"

        # Check if we need to call LLM for context extraction (applies for optimized, high_performance, accurate)
        if config in ['Optimized', 'High Precision', 'Max Accuracy']:  # LLM context is required for these configs
            # Generate context prompt for LLM
            context_prompt = get_context_prompt(query=query)
            response = call_llm(
                prompt=context_prompt,
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=5000,
            )
            model = "ms-marco-MiniLM-L-12-v2"
            # Parse the LLM response to extract collections and n_values
            n_values, collections = parse_llm_response(response=response)
            max_length = 512

            if config == 'High Precision':
                n_values = {collection["name"]: 6 for collection in collections}  

            elif config == 'Max Accuracy':
                n_values = {collection["name"]: 12 for collection in collections}  

            # Check if collections contains report_names
            if isinstance(collections, list) and len(collections) > 0:
                if collections[0].get("name") == "report_names":
                    # If the collection is related to report names, fetch the report data
                    names = get_reports(qdrant_client=qdrant_client)

                # Otherwise, retrieve data from the specified collections
                ensemble_retriever = setup_retrievers(
                    qdrant_client=qdrant_client,
                    collections=collections,
                    n_values=n_values,
                    model=model,
                    max_length=max_length,
                )
                result = ensemble_retriever.invoke(input=docs)

        # Select retriever based on the configuration
        elif config == 'Max Speed':
            model = "ms-marco-TinyBERT-L-2-v2"
            n_values = {"Elements": 3}
            collections = [{"name": "Elements", "n": 3}]
            retriever = setup_fast_retriever(
                qdrant_client=qdrant_client,
                collections=collections,
                n_values=n_values,
                model=model,
                max_length=128,
            )
            result = retriever.invoke(input=docs)
        elif config == 'Efficient':
            model = "ms-marco-MiniLM-L-12-v2"
            n_values = {"Elements": 5}
            collections = [{"name": "Elements", "n": 5}]
            retriever = setup_retrievers(
                qdrant_client=qdrant_client,
                collections=collections,
                n_values=n_values,
                model=model,
                max_length=256,

            )
            result = retriever.invoke(input=docs)


        final_result = []
        if names is not None:
            final_result.append(str(names))
        if result is not None:
            final_result.append(result)

        final_result.append(
            "Must answer in the same language as the user's question."
        )

        if len(final_result) == 1:
            final_result = ["Error: Invalid collections"]

        return final_result

    return context_tool


def parse_llm_response(
        response: str,
) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    """
    Parses the response from the LLM to extract collections and n_values.

    Args:
        response (str): The response from the LLM to be parsed.

    Returns:
        Tuple[Dict[str, int], List[Dict[str, Any]]]: A tuple containing a dictionary
        of n_values and a list of collections.
    """
    try:
        response = response.strip()
        parsed_json = json.loads(s=response)
        collections = parsed_json.get("collections", [])
        n_values = {
            collection["name"]: collection["n"] for collection in collections
        }
        return n_values, collections
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing response: {e}")
        logger.error(f"Response that caused the error: {response}")
        return {}, []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {}, []
