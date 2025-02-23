#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This script configures a set of retrievers for different collections 
in Qdrant and sets up compression for efficient retrieval. It includes 
functions to set up retrievers, fetch report IDs, and handle metadata 
in Qdrant collections. The retrievers are combined using an EnsembleRetriever
to allow multiple retrievers to contribute to the final result with 
assigned weights.

Implements SelfQuerying and Flashrank Rerank.
"""

import logging

from flashrank import Ranker
from langchain_groq import ChatGroq
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.qdrant import QdrantTranslator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant.qdrant import QdrantVectorStore
from src.utils.logging_config import setup_logging
from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_qdrant.qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


# Definir los embeddings de HuggingFace
lc_embed_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
embedding_model = lc_embed_model

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


def setup_retrievers(
    qdrant_client: object, collections, n_values: dict, model: str, max_length: int = 256
) -> EnsembleRetriever:
    """
    Configures retrievers for different collections in Qdrant and sets up
    compression for retrievals.

    Args:
        qdrant_client (QdrantClient): The Qdrant client instance for d
                                    atabase interaction.
        collections (list): A list of collection configurations.
        n_values (dict): A dictionary of collection names and their
                        corresponding top 'n' values for ranking.
        model (str): name of ultra ligth llm .onnx model used to rerank
                    selfquery documents

    Returns:
        EnsembleRetriever: A retriever that combines the results of
        multiple retrievers with specified weights.
    """

    retrievers = []
    weights = []
    llm_re = ChatGroq(
    model_name="llama-3.3-70b-specdec",
    groq_api_key=api_key,
    temperature=0)
    cache_dir = "src/services/llm/rerank_llms"
    model_name = model
    flashrank_client = Ranker(model_name=model_name, cache_dir=cache_dir,max_length=max_length)
    names = get_reports(qdrant_client)

    for collection in collections:
        collection_name = collection["name"]
        n = n_values.get(collection_name, 0)
        print(n)
        print(collection_name)

        if "element_names" == collection_name:
            vector_store_metadata = QdrantVectorStore(
                client=qdrant_client,
                collection_name="element_names",
                embedding=embedding_model,
            )

            retriever_metadata = SelfQueryRetriever.from_llm(
                llm=llm_re,
                vectorstore=vector_store_metadata,
                document_contents="General report description",
                metadata_field_info=[
                    AttributeInfo(
                        name="report_id",
                        description=(
                            f"The report IDs are unique names of each section or global report that can "
                            f"include many dashboards. You MUST ONLY choose report ID names from the "
                            f"following list '{names}'. If any other ReportId is named, DO NOT include "
                            f"them in the filter."
                        ),
                        type="string",
                    ),
                ],
                structured_query_translator=QdrantTranslator(
                    metadata_key="metadata"
                ),
                search_kwargs={"k": 2},
                verbose=False,
            )

            compressor_metadata = FlashrankRerank(
                client=flashrank_client, top_n=1, model=model_name
            )
            compression_retriever_metadata = ContextualCompressionRetriever(
                base_compressor=compressor_metadata,
                base_retriever=retriever_metadata,
            )

            retrievers.append(compression_retriever_metadata)
            weights.append(0.2)

        if "Report Summaries" == collection_name:
            vector_store_summaries = QdrantVectorStore(
                client=qdrant_client,
                collection_name="report_sum",
                embedding=embedding_model,
            )

            retriever_summaries = SelfQueryRetriever.from_llm(
                llm=llm_re,
                vectorstore=vector_store_summaries,
                document_contents="Summary of the report",
                metadata_field_info=[
                    AttributeInfo(
                        name="Report_Id",
                        description=(
                            f"The report IDs are unique names of each section or global report that can "
                            f"include many dashboards. You MUST ONLY choose report ID names from the "
                            f"following list '{names}'. If any other ReportId is named, DO NOT include "
                            f"them in the filter."
                        ),
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_year",
                        description="The year the report was inserted",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_month",
                        description="The month the report was inserted; 2 digits",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_day",
                        description="The day the report was inserted; 2 digits",
                        type="string",
                    ),
                ],
                structured_query_translator=QdrantTranslator(
                    metadata_key="metadata"
                ),
                search_kwargs={"k": 2},
                verbose=False,
            )

            compressor_summaries = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_summaries = ContextualCompressionRetriever(
                base_compressor=compressor_summaries,
                base_retriever=retriever_summaries,
            )

            retrievers.append(compression_retriever_summaries)
            weights.append(0.3)

        if "Elements" == collection_name:
            vector_store_tabular = QdrantVectorStore(
                client=qdrant_client,
                collection_name="table_elements",
                embedding=embedding_model,
            )

            retriever_tabular = SelfQueryRetriever.from_llm(
                llm=llm_re,
                vectorstore=vector_store_tabular,
                document_contents="Report content",
                metadata_field_info=[
                    AttributeInfo(
                        name="Id",
                        description=(
                            f"The Ids are unique report IDs of each section or global report that can "
                            f"include many dashboards. You MUST ONLY choose report ID names from the "
                            f"following list '{names}'. If any other ReportId is named, DO NOT include "
                            f"them in the filter."
                        ),
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_year",
                        description="The year the report was inserted",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_month",
                        description="The month the report was inserted; 2 digits",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_day",
                        description="The day the report was inserted; 2 digits",
                        type="string",
                    ),
                ],
                structured_query_translator=QdrantTranslator(
                    metadata_key="metadata"
                ),
                search_kwargs={"k": 20},
                verbose=False,
            )

            compressor_tabular = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_tabular = ContextualCompressionRetriever(
                base_compressor=compressor_tabular,
                base_retriever=retriever_tabular,
            )

            retrievers.append(compression_retriever_tabular)
            weights.append(0.3)

        if "Text Pages" == collection_name:
            vector_store_text = QdrantVectorStore(
                client=qdrant_client,
                collection_name="text_pages",
                embedding=embedding_model,
            )

            retriever_text = SelfQueryRetriever.from_llm(
                llm=llm_re,
                vectorstore=vector_store_text,
                document_contents="Report content",
                metadata_field_info=[
                    AttributeInfo(
                        name="Report_Id",
                        description=(
                            f"The report IDs are unique names of each section or global report that can "
                            f"include many dashboards. You MUST ONLY choose report ID names from the "
                            f"following list '{names}'. If any other ReportId is named, DO NOT include "
                            f"them in the filter."
                        ),
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_year",
                        description="The year the report was inserted",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_month",
                        description="The month the report was inserted; 2 digits",
                        type="string",
                    ),
                    AttributeInfo(
                        name="insertion_day",
                        description="The day the report was inserted; 2 digits",
                        type="string",
                    ),
                ],
                structured_query_translator=QdrantTranslator(
                    metadata_key="metadata"
                ),
                search_kwargs={"k": 8},
                verbose=False,
            )

            compressor_text = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_text = ContextualCompressionRetriever(
                base_compressor=compressor_text, base_retriever=retriever_text
            )

            retrievers.append(compression_retriever_text)
            weights.append(0.2)

        if "upload_dates" == collection_name:
            vector_store_dates = QdrantVectorStore(
                client=qdrant_client,
                collection_name="upload_dates",
                embedding=embedding_model,
            )

            retriever_dates = SelfQueryRetriever.from_llm(
                llm=llm_re,
                vectorstore=vector_store_dates,
                document_contents="Upload dates information of the report",
                metadata_field_info=[
                    AttributeInfo(
                        name="report_id",
                        description=(
                            f"The report IDs are unique names of each section or global report that can "
                            f"include many dashboards. You MUST ONLY choose report ID names from the "
                            f"following list '{names}'. If any other ReportId is named, DO NOT include "
                            f"them in the filter."
                        ),
                        type="string",
                    ),
                ],
                structured_query_translator=QdrantTranslator(
                    metadata_key="metadata"
                ),
                search_kwargs={"k": 2},
                verbose=False,
            )

            compressor_dates = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_dates = ContextualCompressionRetriever(
                base_compressor=compressor_dates, base_retriever=retriever_dates
            )

            retrievers.append(compression_retriever_dates)
            weights.append(0.2)

    ensemble_retriever = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights,  # Adjusted weights based on active collections
    )
    return ensemble_retriever


def get_reports(qdrant_client: object) -> str:
    """
    Retrieves report IDs from the Qdrant client by scrolling through the 'report_names' collection.

    This function retrieves the report IDs from the metadata stored in Qdrant by scrolling
    through the collection and extracting the page content. If successful, it returns a
    comma-separated string of unique report IDs.

    Args:
        qdrant_client (QdrantClient): The client to interact with the Qdrant service.

    Returns:
        str: A comma-separated string of report IDs if successful, or an error message if an exception occurs.
    """
    try:
        # Decompose the tuple: the first element is the points, the second is the cursor
        points, cursor = qdrant_client.scroll(
            collection_name="report_names",
            limit=1,
            with_payload=True,  # Ensure to get the payload if needed
        )

        if points:
            # Extract metadata from the first point
            names = points[0].payload.get("page_content", {})

            # Get only the report IDs from the key '0'
            report_ids = sorted(
                set(item for item in names if isinstance(item, str))
            )

            # Convert the list of IDs into a comma-separated string
            report_ids_string = ",".join(report_ids)

            return report_ids_string  # Return the string instead of jsonify

        else:
            logger.warning("No points found in Qdrant.")
            return ""  # Return an empty string if no points are found

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return (
            f"Error: {str(e)}"  # Return an error string if an exception occurs
        )
