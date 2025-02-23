#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This module sets up various retrievers for collections in Qdrant, 
each configured with a contextual compression mechanism and 
integrated with OpenAI embeddings. The retrievers are used to 
retrieve and rank documents from different collections 
like "Report Summaries", "Elements", "Text Pages", "element_names",
and "upload_dates". The function `setup_retrievers` sets up these 
retrievers, applies compression, and then combines them into an
`EnsembleRetriever` for effective querying. 

Unlike selfq_retrievers.py, this module is intended to implement
retieval without SelfQuerying.

The retrievers utilize Flashrank for reranking documents and Qdrant 
as the vector store for retrieving relevant documents.
"""

import os
from typing import Dict, List

from flashrank import Ranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_qdrant.qdrant import QdrantVectorStore

# Definir los embeddings de HuggingFace
lc_embed_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
embedding_model = lc_embed_model

def setup_retrievers(
        qdrant_client: object,
        collections: List[Dict[str, str]],
        n_values: Dict[str, int],
        model: str,
        max_length: int = 128
) -> EnsembleRetriever:
    """
    Sets up retrievers for different collections in Qdrant and
    configures contextual compression.

    This function sets up retrievers for various collections such as
    "Report Summaries", "Elements", "Text Pages", "element_names",
    and "upload_dates" using Qdrant vector stores and OpenAI embeddings.
    It also configures Flashrank for re-ranking documents and applies
    contextual compression to each retriever. The function then
    combines all retrievers into an `EnsembleRetriever`.

    **Self Querying is not applied in this function.**

    Args:
        qdrant_client (object): The Qdrant client to interact with the
                        Qdrant service.
        collections (List[Dict[str, str]]): A list of collection dictionaries
                        containing collection names.
        n_values (Dict[str, int]): A dictionary containing the number of top
                        results to return for each collection.

    Returns:
        EnsembleRetriever: The retriever ensemble with weighted retrievers
        for each collection.
    """
    # Initialize the list of retrievers and their corresponding weights
    retrievers = []
    weights = []
    # Define model name and initialize necessary clients
    model_name = model
    cache_dir = "src/services/llm/rerank_llms"
    model_name = model
    flashrank_client = Ranker(model_name=model_name,cache_dir=cache_dir)

    for collection in collections:
        collection_name = collection["name"]
        n = n_values.get(collection_name, 0)

        if collection_name == "Report Summaries":
            # Set up vector store and retriever for Report Summaries
            vector_store_summaries = QdrantVectorStore(
                client=qdrant_client,
                collection_name="report_sum",
                embedding=embedding_model,
            )
            retriever_summaries = vector_store_summaries.as_retriever(
                search_kwargs={"k": 10}
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

        elif collection_name == "Elements":
            # Set up vector store and retriever for Elements
            vector_store_tabular = QdrantVectorStore(
                client=qdrant_client,
                collection_name="table_elements",
                embedding=embedding_model,
            )
            retriever_tabular = vector_store_tabular.as_retriever(
                search_kwargs={"k": 10}
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

        elif collection_name == "Text Pages":
            # Set up vector store and retriever for Text Pages
            vector_store_text = QdrantVectorStore(
                client=qdrant_client,
                collection_name="text_pages",
                embedding=embedding_model,
            )
            retriever_text = vector_store_text.as_retriever(
                search_kwargs={"k": 10}
            )
            compressor_text = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_text = ContextualCompressionRetriever(
                base_compressor=compressor_text, base_retriever=retriever_text
            )
            retrievers.append(compression_retriever_text)
            weights.append(0.2)

        elif collection_name == "element_names":
            # Set up vector store and retriever for Element Names
            vector_store_metadata = QdrantVectorStore(
                client=qdrant_client,
                collection_name="element_names",
                embedding=embedding_model,
            )
            retriever_metadata = vector_store_metadata.as_retriever(
                search_kwargs={"k": 10}
            )
            compressor_metadata = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_metadata = ContextualCompressionRetriever(
                base_compressor=compressor_metadata,
                base_retriever=retriever_metadata,
            )
            retrievers.append(compression_retriever_metadata)
            weights.append(0.2)

        # Configuration for 'upload_dates' collection
        elif "upload_dates" == collection_name:
            vector_store_dates = QdrantVectorStore(
                client=qdrant_client,
                collection_name="upload_dates",
                embedding=embedding_model,
            )
            retriever_dates = vector_store_dates.as_retriever(
                search_kwargs={"k": 10}
            )
            compressor_dates = FlashrankRerank(
                client=flashrank_client, top_n=n, model=model_name
            )
            compression_retriever_dates = ContextualCompressionRetriever(
                base_compressor=compressor_dates, base_retriever=retriever_dates
            )
            retrievers.append(compression_retriever_dates)
            weights.append(0.2)

    # Create and return the EnsembleRetriever with the selected retrievers and their weights
    ensemble_retriever = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights,  # Adjusted weights for active collections
    )
    return ensemble_retriever
