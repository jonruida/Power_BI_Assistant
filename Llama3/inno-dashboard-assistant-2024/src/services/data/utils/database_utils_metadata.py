#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
This module defines the DatabaseCreator class to manage collections in the Qdrant database,
used to store and process report data extracted from JSON files. The class includes
methods to create collections, process report names, KPIs, charts, tables, and upload dates,
and convert strings to integers based on ASCII values.

Functions:
- `extract_json_from_file`: Extracts and returns JSON data from a given file.
- `create_collections`: Creates the necessary collections in the Qdrant database.
- `string_to_int_ascii`: Converts a string to an integer by summing the ASCII codes of its characters.
- `process_report_names`: Processes report names and stores them in Qdrant.
- `process_element_names`: Processes and stores unique elements (KPIs, charts, tables) in Qdrant.
- `process_upload_dates`: Processes and stores upload dates in Qdrant.
"""

import json
import logging
import os
import re
from collections import defaultdict

from langchain_openai import OpenAIEmbeddings
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
    A class to create and manage collections in Qdrant database for processing and storing report data.

    Attributes:
        texts_folder (str): The folder containing JSON files with report data.
        qdrant_client (QdrantClient): Client to interact with the Qdrant database.
        embedding_model (OpenAIEmbeddings): Model used to generate embeddings for report data.
        embedding_size (int): The size of the embedding vectors.
    """

    def __init__(self, texts_folder: str):
        """
        Initializes the DatabaseCreator instance.

        Args:
            texts_folder (str): The folder containing the JSON files.
        """
        self.texts_folder = texts_folder
        self.qdrant_client = QdrantClient(location="localhost", port=6333)
        logger.info("[INFO] Client created...")
        self.embedding_model = embed_model
        self.embedding_size = (
            1024  # Change this according to the embedding size you use
        )

        # Create necessary collections
        self.create_collections()

    def extract_json_from_file(self, file_path: str):
        """
        Extracts JSON content from a given file.

        Args:
            file_path (str): Path to the file from which JSON content is extracted.

        Returns:
            dict or None: The extracted JSON data, or None if there is an error.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Search for the block delimited by 'json'
            match = re.search(r"json(.*?)", content, re.DOTALL)
            if match:
                json_content = match.group(1).strip()
            else:
                json_content = content.strip().strip('"')

            json_content = json_content.replace("\\n", " ").strip()
            json_content = json_content.replace("\\", "").strip()

            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                return None

    def create_collections(self):
        """
        Creates the necessary collections in Qdrant.
        """
        # Collection for report names, without embedding
        try:
            self.qdrant_client.get_collection("report_names")
            logger.info(
                f"[INFO] The collection 'report_names' already exists. It will not be recreated."
            )
        except Exception:
            logger.info(
                "[INFO] Creating Qdrant data collection: report_names..."
            )
            self.qdrant_client.create_collection(
                collection_name="report_names",
                vectors_config=models.VectorParams(
                    size=1, distance=models.Distance.EUCLID
                ),  # No embedding
            )
            logger.info(
                "[INFO] 'report_names' collection created successfully."
            )

        # Collection for element names, with embedding
        try:
            self.qdrant_client.get_collection("element_names")
            logger.info(
                f"[INFO] The collection 'element_names' already exists. It will not be recreated."
            )
        except Exception:
            logger.info(
                "[INFO] Creating Qdrant data collection: element_names..."
            )
            self.qdrant_client.create_collection(
                collection_name="element_names",
                vectors_config=models.VectorParams(
                    size=self.embedding_size, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=10
                ),
            )
            logger.info(
                "[INFO] 'element_names' collection created successfully."
            )

        # Collection for upload dates, with embedding
        try:
            self.qdrant_client.get_collection("upload_dates")
            logger.info(
                f"[INFO] The collection 'upload_dates' already exists. It will not be recreated."
            )
        except Exception:
            logger.info(
                "[INFO] Creating Qdrant data collection: upload_dates..."
            )
            self.qdrant_client.create_collection(
                collection_name="upload_dates",
                vectors_config=models.VectorParams(
                    size=self.embedding_size, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=10
                ),
            )
            logger.info(
                "[INFO] 'upload_dates' collection created successfully."
            )

    def string_to_int_ascii(self, s: str) -> int:
        """
        Converts a string to an integer by summing the ASCII codes of its characters.

        Args:
            s (str): The string to convert.

        Returns:
            int: The resulting integer.
        """
        return sum(ord(char) for char in s)

    def process_report_names(self):
        """
        Processes and stores the names of reports.

        It extracts all report IDs from the JSON files and updates the 'report_names'
        collection in Qdrant.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        all_report_ids = set()  # Set to accumulate unique report IDs

        # Iterate through all JSON files and accumulate report_ids
        for file in tqdm(json_files, desc="Loading JSON files"):
            file_path = os.path.join(self.texts_folder, file)
            content = self.extract_json_from_file(file_path)

            if content:
                report_id = content.get("report_id", "Unknown")
                all_report_ids.add(report_id)

        # Get existing IDs from the 'report_names' collection
        try:
            existing_point = self.qdrant_client.scroll(
                collection_name="report_names", limit=1
            ).points[0]
            existing_report_ids = set(
                existing_point.payload.get("page_content", [])
            )
        except Exception:
            existing_report_ids = set()

        # Calculate the unique report_ids not in Qdrant
        new_report_ids = all_report_ids - existing_report_ids

        # If there are new IDs, update the point in Qdrant
        if new_report_ids:
            updated_point = models.PointStruct(
                id=0,
                vector=[0.0],  # Minimum vector
                payload={
                    "page_content": list(existing_report_ids | new_report_ids)
                },
            )
            self.qdrant_client.upsert(
                collection_name="report_names", points=[updated_point]
            )
            logger.info(
                f"[INFO] Updated 'report_names' collection with {len(new_report_ids)} new report IDs."
            )
        else:
            logger.info("[INFO] No new report IDs to add.")

    def process_element_names(self):
        """
        Processes and stores unique elements (KPIs, charts, tables) per ReportID in Qdrant.

        Extracts KPIs, charts, and tables from the report data and uploads them to the
        'element_names' collection.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        unique_elements = defaultdict(
            lambda: {"KPIs": set(), "Charts": set(), "Tables": set()}
        )

        # Load JSONs and extract elements
        for file in tqdm(json_files, desc="Processing JSON files"):
            file_path = os.path.join(self.texts_folder, file)
            content = self.extract_json_from_file(file_path)

            if content:
                report_id = content.get("report_id", "Unknown")
                detected_elements = content.get("detected_elements", {})

                # Store KPI, chart, and table titles without duplicates
                unique_elements[report_id]["KPIs"].update(
                    kpi.get("kpi_title", "Untitled (KPI)")
                    for kpi in detected_elements.get("KPIs", [])
                )
                unique_elements[report_id]["Charts"].update(
                    chart.get("visualization_title", "Untitled (Chart)")
                    for chart in detected_elements.get("charts", [])
                )
                unique_elements[report_id]["Tables"].update(
                    table.get("table_title", "Untitled (Table)")
                    for table in detected_elements.get("tables", [])
                )

        # Create points and upload them to Qdrant
        points = []
        for report_id, elements in unique_elements.items():
            hashed_id = self.string_to_int_ascii(s=report_id)
            report_id_embedding = self.embedding_model.get_text_embedding(
                json.dumps(report_id)
            )

            point = models.PointStruct(
                id=hashed_id,
                vector=report_id_embedding,
                payload={
                    "page_content": json.dumps(
                        {  # Convert to JSON string
                            "report_id": report_id,
                            "KPIs": list(elements["KPIs"]),
                            "Charts": list(elements["Charts"]),
                            "Tables": list(elements["Tables"]),
                        }
                    )
                },
            )
            points.append(point)

        if points:
            self.qdrant_client.upsert(
                collection_name="element_names", points=points
            )
            logger.info(
                f"[INFO] Uploaded {len(points)} new element entries to 'element_names' collection."
            )

    def process_upload_dates(self):
        """
        Processes and stores upload dates grouped by ReportID in Qdrant.

        It extracts dates of insertion from the JSON files and updates
        the 'upload_dates' collection in Qdrant.
        """
        json_files = [
            f for f in os.listdir(self.texts_folder) if f.endswith(".json")
        ]
        upload_dates = defaultdict(set)

        # Iterate through JSON files and accumulate insertion dates
        for file in tqdm(json_files, desc="Loading JSON files"):
            file_path = os.path.join(self.texts_folder, file)
            content = self.extract_json_from_file(file_path)

            if content:
                report_id = content.get("report_id", os.path.splitext(file)[0])
                insertion_date = content.get("date", "Unknown")
                upload_dates[report_id].add(insertion_date)

        # Convert dates to embeddings and store in Qdrant
        points = []
        for report_id, dates in upload_dates.items():
            report_id_embedding = self.embedding_model.get_text_embedding(
                json.dumps(report_id)
            )
            point = models.PointStruct(
                id=self.string_to_int_ascii(s=report_id),
                vector=report_id_embedding,
                payload={
                    "page_content": json.dumps({"dates": list(dates)}),
                    "metadata": {"report_id": report_id},
                },
            )
            points.append(point)

        # Upload the points
        self.qdrant_client.upload_points(
            collection_name="upload_dates", points=points
        )
        logger.info(
            f"[INFO] Uploaded {len(points)} new upload date entries to 'upload_dates' collection."
        )
