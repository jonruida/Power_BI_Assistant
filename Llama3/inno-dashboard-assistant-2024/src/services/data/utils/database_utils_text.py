#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This module provides classes and methods to load, process, and upload report summaries and text pages
from JSON files to a Qdrant database. The reports and text pages are embedded using OpenAI's embedding
model from Langchain, and the data is stored in a Qdrant collection for efficient retrieval and analysis.

Classes:
    DatabaseCreator_report_sum: Handles loading, processing, and uploading report summaries to Qdrant.
    DatabaseCreator_text_pages: Handles loading, processing, and uploading text pages to Qdrant.

Dependencies:
    - qdrant_client: Client for interacting with the Qdrant database.
    - langchain_openai: Langchain's OpenAI model for generating embeddings.
    - tqdm: A progress bar library used to show progress during data processing.
    - os: Provides functions for interacting with the operating system (e.g., listing files).
    - json: Handles loading and parsing JSON files.
"""
import json
import logging
import os
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.utils.logging_config import setup_logging
from tqdm import tqdm
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_huggingface import HuggingFaceEmbeddings

# Definir los embeddings de HuggingFace
lc_embed_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
embed_model = LangchainEmbedding(lc_embed_model)

# Set up logging
setup_logging()
logger = logging.getLogger(name=__name__)


class DatabaseCreator_report_sum:
    """
    A class to load report summaries from JSON files, process them using OpenAI embeddings,
    and upload them to a Qdrant collection.

    Attributes:
        texts_folder (str): The directory where the JSON files are stored.
        collection_name (str): The name of the Qdrant collection to store the data.
        embedding_size (int): The size of the embedding vector.
        qdrant_client (QdrantClient): Qdrant client instance to interact with the Qdrant database.
        embedding_model (OpenAIEmbeddings): Langchain OpenAI embeddings model for processing text data.
        jsons (list): List of report summary data loaded from JSON files.
    """

    def __init__(self, texts_folder: str):
        """
        Initializes the DatabaseCreator_report_sum instance.

        Args:
            texts_folder (str): The directory where the JSON files are stored.
        """
        self.texts_folder = texts_folder
        self.collection_name = "report_sum"
        self.embedding_size = 1024
        self.qdrant_client = QdrantClient("localhost", port=6333)
        logger.info("[INFO] Client created for report_sum...")

        # Load report summaries from JSON files
        logger.info("[INFO] Loading report summaries from JSON files...")
        self.jsons = self.load_json_data()

        # Initialize Langchain with OpenAI embeddings model
        logger.info("[INFO] Loading the OpenAI model for embeddings...")
        self.embedding_model = embed_model

        # Verify and create the collection if it doesn't exist
        self.create_collection()

    def create_collection(self):
        """
        Verifies if the Qdrant collection exists, and creates it if not.

        This method attempts to fetch the collection from Qdrant and creates it if not found.
        """
        try:
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(
                f"[INFO] The collection '{self.collection_name}' already exists. No need to recreate it."
            )
        except Exception:
            logger.info(
                "[INFO] Creating Qdrant data collection for report summaries..."
            )
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_size, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=10
                ),
            )
            logger.info(
                f"[INFO] Collection '{self.collection_name}' created successfully."
            )

    def load_json_data(self) -> List:
        """
        Loads report summary data from JSON files in the specified folder.

        Reads the content and metadata from each JSON file, extracting relevant fields
        like "Report_Id" and "contenido".

        Returns:
            list: A list of dictionaries containing the content and metadata for each report.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        report_data = []

        for file in json_files:
            file_path = os.path.join(self.texts_folder, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            metadata = content["metadata"]
            summary_content = content["contenido"]

            report_data.append(
                {"content": summary_content, "metadata": metadata}
            )

        return report_data

    def process_and_upload_data(self):
        """
        Processes the report summaries, generates embeddings, and uploads the data to Qdrant.

        For each report summary, the content is embedded using the OpenAI embeddings model
        and uploaded to the Qdrant collection.
        """
        logger.info(
            "[INFO] Processing report summaries and uploading to Qdrant..."
        )
        points = []

        for idx, report in tqdm(enumerate(self.jsons), total=len(self.jsons)):
            content = report.get("content")
            metadata = report.get("metadata")

            # Embedding the summary content
            content_embedding = self.embedding_model.get_text_embedding(content)

            # Create a point and add it to the list of points to upload
            points.append(
                models.PointStruct(
                    id=idx,
                    vector=content_embedding,
                    payload={"page_content": content, "metadata": metadata},
                )
            )

        logger.info(
            f"[INFO] Uploading {len(points)} records to Qdrant for report summaries..."
        )
        self.qdrant_client.upload_points(
            collection_name=self.collection_name, points=points
        )
        logger.info("[INFO] Successfully uploaded report summaries!")


class DatabaseCreator_text_pages:
    """
    A class to load text pages from JSON files, process them using OpenAI embeddings,
    and upload them to a Qdrant collection.

    Attributes:
        texts_folder (str): The directory where the JSON files are stored.
        collection_name (str): The name of the Qdrant collection to store the data.
        embedding_size (int): The size of the embedding vector.
        qdrant_client (QdrantClient): Qdrant client instance to interact with the Qdrant database.
        embedding_model (OpenAIEmbeddings): Langchain OpenAI embeddings model for processing text data.
        jsons (list): List of text page data loaded from JSON files.
    """

    def __init__(self, texts_folder: str):
        """
        Initializes the DatabaseCreator_text_pages instance.

        Args:
            texts_folder (str): The directory where the JSON files are stored.
        """
        self.texts_folder = texts_folder
        self.collection_name = "text_pages"
        self.embedding_size = 1024
        self.qdrant_client = QdrantClient(location="localhost", port=6333)
        logger.info("[INFO] Client created for text_pages...")

        # Load text pages from JSON files
        logger.info("[INFO] Loading text pages from JSON files...")
        self.jsons = self.load_json_data()

        # Initialize Langchain with OpenAI embeddings model
        logger.info("[INFO] Loading the OpenAI model for embeddings...")
        self.embedding_model = embed_model

        # Verify and create the collection if it doesn't exist
        self.create_collection()

    def create_collection(self):
        """
        Verifies if the Qdrant collection exists, and creates it if not.

        This method attempts to fetch the collection from Qdrant and creates it if not found.
        """
        try:
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(
                f"[INFO] The collection '{self.collection_name}' already exists. No need to recreate it."
            )
        except Exception:
            logger.info(
                "[INFO] Creating Qdrant data collection for text pages..."
            )
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_size, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=10
                ),
            )
            logger.info(
                f"[INFO] Collection '{self.collection_name}' created successfully."
            )

    def load_json_data(self) -> List:
        """
        Loads text page data from JSON files in the specified folder.

        Reads the content and metadata from each JSON file, extracting relevant fields
        like "Report_Id" and "contenido".

        Returns:
            list: A list of dictionaries containing the content and metadata for each page.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        report_data = []

        for file in json_files:
            file_path = os.path.join(self.texts_folder, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            metadata = content["metadata"]
            pages_content = content["contenido"]

            report_data.append({"content": pages_content, "metadata": metadata})

        return report_data

    def process_and_upload_data(self):
        """
        Processes the text pages, generates embeddings, and uploads the data to Qdrant.

        For each text page, the content is embedded using the OpenAI embeddings model
        and uploaded to the Qdrant collection.
        """
        logger.info("[INFO] Processing text pages and uploading to Qdrant...")
        points = []

        for idx, page in tqdm(enumerate(self.jsons), total=len(self.jsons)):
            content = page.get("content")
            metadata = page.get("metadata")

            # Embedding the page content
            page_embedding = self.embedding_model.get_text_embedding(content)

            # Create a point and add it to the list of points to upload
            points.append(
                models.PointStruct(
                    id=idx,
                    vector=page_embedding,
                    payload={"page_content": content, "metadata": metadata},
                )
            )

        logger.info(
            f"[INFO] Uploading {len(points)} records to Qdrant for text pages..."
        )
        self.qdrant_client.upload_points(
            collection_name=self.collection_name, points=points
        )
        logger.info("[INFO] Successfully uploaded text pages!")
