#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This module contains the `DatabaseCreator` class, which is responsible for:
- Loading JSON files from a specified folder.
- Extracting key performance indicators (KPIs), charts, and tables from the JSON content.
- Creating and configuring a collection in Qdrant.
- Generating embeddings for the extracted data using OpenAI's model via Langchain.
- Uploading the processed data to a Qdrant vector database.
"""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

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


class DatabaseCreator:
    """
    Class responsible for loading JSON files, extracting relevant data, and uploading it to Qdrant.

    Attributes:
        texts_folder (str): Path to the directory containing the JSON files to process.
        collection_name (str): Name of the collection in Qdrant where the data will be stored.
        embedding_size (int): Size of the embedding used for Qdrant vectors.
        qdrant_client (QdrantClient): Qdrant client to interact with the database.
        embedding_model (OpenAIEmbeddings): Langchain model to generate embeddings using OpenAI.
    """

    def __init__(self, texts_folder: str):
        """
        Initializes the class with the folder path for texts and sets up the Qdrant client and embedding model.

        Args:
            texts_folder (str): Path to the directory containing the JSON files to process.
        """
        self.texts_folder = texts_folder
        self.collection_name = "table_elements"
        self.embedding_size = 1024
        self.qdrant_client = QdrantClient(location="localhost", port=6333)
        logger.info(" Client created...")

        # Initialize Langchain with OpenAI Embeddings
        logger.info(" Loading the OpenAI model for embeddings...")
        self.embedding_model = embed_model

        # Verify and create collection
        self.create_collection()

    def extract_json_from_file(
            self, file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extracts JSON from a given file. If the file contains delimited JSON content,
        it is extracted and loaded.

        Args:
            file_path (str): Path to the file from which JSON will be extracted.

        Returns:
            Optional[Dict[str, Any]]: Extracted JSON content, or None if extraction fails.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Search for JSON-delimited block
            match = re.search(r"json(.*?)", content, re.DOTALL)
            if match:
                # Extract the content inside the delimited block
                json_content = match.group(1).strip()
            else:
                # If no delimiters, use entire content
                json_content = content.strip().strip('"')

            # Remove unnecessary characters like escape sequences
            json_content = json_content.replace("\\n", " ").strip()
            json_content = json_content.replace("\\", "").strip()

            # Attempt to load the JSON
            try:
                return json.loads(s=json_content)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                return None

    def create_collection(self) -> None:
        """
        Creates the collection in Qdrant if it doesn't exist. If the collection already exists,
        no action is taken.

        Returns:
            None
        """
        try:
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(
                f"The collection '{self.collection_name}' already exists. No need to create it."
            )
        except Exception:
            logger.info(" Creating Qdrant data collection...")
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
                f"Collection '{self.collection_name}' created successfully."
            )

    # Configure logger to show warnings
    logging.basicConfig(level=logging.WARNING)

    def load_json_data(self) -> List[Dict[str, Any]]:
        """
        Loads and processes JSON files from the specified folder, extracting KPIs, tables, and charts.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing processed data from the JSON files.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        report_data = []

        # Iterate over JSON files with tqdm to show progress
        for file in tqdm(json_files, desc="Loading JSON files"):
            file_path = os.path.join(self.texts_folder, file)
            content = self.extract_json_from_file(file_path)

            # Use .get() method to avoid missing key errors
            report_id = content.get("report_id", "Unknown")
            insertion_date = content.get("date", "Unknown")
            page_number = content.get("page", "Unknown")  # Extract page number
            detected_elements = content.get("detected_elements", {})

            # Store KPIs, charts, and tables
            for kpi in detected_elements.get("KPIs", []):
                try:
                    report_data.append(
                        {
                            "report_id": report_id,
                            "insertion_date": insertion_date,
                            "page": page_number,  # Add page number here
                            "type": "KPI",
                            "title": kpi.get(
                                "kpi_title", None
                            ),  # Use None if not present
                            "content": kpi.get(
                                "kpi_description", None
                            ),  # Use None if not present
                            "value": kpi.get(
                                "kpi_value", None
                            ),  # Use None if not present
                            "columns": None,
                            "rows": None,
                        }
                    )
                except KeyError as e:
                    logging.warning(
                        f"Missing key {e} in KPI for file {file}. Using None for missing values."
                    )

            for chart in detected_elements.get("charts", []):
                try:
                    report_data.append(
                        {
                            "report_id": report_id,
                            "insertion_date": insertion_date,
                            "page": page_number,  # Add page number here
                            "type": "Chart",
                            "title": chart.get(
                                "visualization_title", None
                            ),  # Use None if not present
                            "content": chart.get(
                                "visualization_description", None
                            ),  # Use None if not present
                            "value": chart.get(
                                "values", None
                            ),  # Use None if not present
                            "columns": chart.get("metrics_displayed", None),
                            "rows": None,
                        }
                    )
                except KeyError as e:
                    logging.warning(
                        f"Missing key {e} in chart for file {file}. Using None for missing values."
                    )

            for table in detected_elements.get("tables", []):
                try:
                    report_data.append(
                        {
                            "report_id": report_id,
                            "insertion_date": insertion_date,
                            "page": page_number,  # Add page number here
                            "type": "Table",
                            "title": table.get(
                                "table_title", None
                            ),  # Use None if not present
                            "content": table.get(
                                "table_description", None
                            ),  # Use None if not present
                            "value": None,
                            "columns": table.get(
                                "columns", None
                            ),  # Use None if not present
                            "rows": table.get(
                                "rows", None
                            ),  # Use None if not present
                        }
                    )
                except KeyError as e:
                    logging.warning(
                        f"Missing key {e} in table for file {file}. Using None for missing values."
                    )

        return report_data

    def process_and_upload_data(self) -> None:
        """
        Processes the JSON data, generates corresponding embeddings, and uploads them to Qdrant.

        Returns:
            None
        """
        logger.info(" Processing data and uploading to Qdrant...")
        points = []

        # Load the JSON data
        report_data = self.load_json_data()

        # Iterate over reports with tqdm to show progress
        for idx, report in tqdm(
                enumerate(report_data),
                total=len(report_data),
                desc="Processing and embedding data",
        ):
            report_id = report.get("report_id")
            insertion_date = report.get("insertion_date")
            page_number = report.get("page")  # Extract page number
            content = report.get("content")
            element_title = report.get("title")
            element_type = report.get("type")

            # Create text for embedding
            embedding_input = (
                f"{element_title} | {insertion_date} | {report_id} | {content}"
            )

            # Create embedding for content
            chunk_embedding = self.embedding_model.get_text_embedding(
                embedding_input
            )

            points.append(
                models.PointStruct(
                    id=idx,
                    vector=chunk_embedding,
                    payload={
                        "metadata": {
                            "Id": report_id,
                            "type": element_type,
                            "title": element_title,
                            "insertion_year": (
                                insertion_date.split("-")[0]
                                if insertion_date != "Unknown"
                                else None
                            ),
                            "insertion_month": (
                                insertion_date.split("-")[1]
                                if insertion_date != "Unknown"
                                else None
                            ),
                            "insertion_day": (
                                insertion_date.split("-")[2]
                                if insertion_date != "Unknown"
                                else None
                            ),
                            "page": page_number,  # Add page number here
                        },
                        "page_content": json.dumps(report),
                    },
                )
            )

        # Upload points to Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name, points=points
        )
        logger.info(" Data successfully uploaded to Qdrant.")
