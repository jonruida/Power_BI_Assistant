#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit

"""
Power BI Assistant Suite App's Backend Server Configuration.

This script sets up the backend server of the Power BI Assistant Suite App using Flask, 
handling requests from the frontend, interacting with the Qdrant vector database, 
and generating dynamic responses via llama-3 models. It provides the API endpoints 
for querying reports, fetching insights, and supporting the chatbot functionality.
"""

import logging
import os
import time
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from qdrant_client import QdrantClient

from src.services.agent.core import Agent
from src.services.data.utils.database_utils_metadata import (
    DatabaseCreator as DatabaseCreator_metadata,
)
from src.services.data.utils.database_utils_table import (
    DatabaseCreator as DatabaseCreator_table,
)
from src.services.data.utils.database_utils_text import (
    DatabaseCreator_report_sum,
    DatabaseCreator_text_pages,
)
from src.services.report_generation.report_gen import inform_generator
from src.services.retrievers.selfq_retrievers import get_reports
from src.utils.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(name=__name__)

app = Flask(__name__)
qdrant_client = QdrantClient("localhost", port=6333)

agent = Agent(qdrant_client=qdrant_client)

# Define absolute paths to required directories
base_dir = "./src/services/data/etl_data"
json_reports_dir = os.path.join(base_dir, "json_reports")
page_reports_dir = os.path.join(base_dir, "page_reports")
sum_reports_dir = os.path.join(base_dir, "sum_reports")

# Create instances of DatabaseCreator using absolute paths
db_creator_tabular = DatabaseCreator_table(texts_folder=json_reports_dir)
db_creator_text_pages = DatabaseCreator_text_pages(
    texts_folder=page_reports_dir
)
db_creator_report_sum = DatabaseCreator_report_sum(texts_folder=sum_reports_dir)
db_creator_metadata = DatabaseCreator_metadata(texts_folder=json_reports_dir)


@app.route("/query", methods=["POST"])
def query() -> Optional[Dict[str, str]]:
    """
    Endpoint to handle user queries.

    This endpoint receives a user's query and generates a response by interacting with the
    backend services. It processes the query, retrieves the relevant data, and generates
    insights using llama-3 model.

    Request Body:
        {
            "query": <str>,
            "informe_seleccionado": <str>,
            "informes_disponibles": <list>
            "configuration": <str>, 
        }

    Returns:
        json: A JSON object with the assistant's response.
    """
    try:
        query_text: str = request.json.get("query")
        config: str = request.json.get("configuration")
        informe_seleccionado: str = request.json.get("informe_seleccionado")
        report_ids: List[str] = request.json.get("informes_disponibles")
        report_ids = ", ".join(report_ids)

        result = agent.run(
            query=query_text, informe_seleccionado=informe_seleccionado, config=config
        )

        if isinstance(result, str):
            response_data = {"response": result}
        else:
            response_data = {
                "response": result.get("result", "No response found.")
            }

        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error in /query: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "error": (
                        "An error occurred on the server. Please check the logs for more details."
                    )
                }
            ),
            500,
        )


@app.route("/get_reports", methods=["GET"])
def get_reports_route() -> Optional[Dict[str, List[str]]]:
    """
    Endpoint to fetch the available reports.

    This endpoint retrieves the list of reports available for querying,
    which will be displayed in the front-end for user selection.

    Returns:
        json: A JSON object containing the list of report IDs.
    """
    try:
        report_ids: str = get_reports(qdrant_client=qdrant_client)
        report_ids = report_ids.split(",")
        if report_ids:
            return jsonify({"report_ids": report_ids}), 200
        else:
            return jsonify({"report_ids": []}), 200
    except Exception as e:
        logger.error(f"Error in /get_reports: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/get_dates_by_id", methods=["GET"])
def get_dates_by_id() -> Optional[Dict[str, str]]:
    """
    Endpoint to fetch dates associated with a specific report ID.

    Request Parameters:
        id (str): The report ID for which dates are being requested.
                  This is a required query parameter.

    Returns:
        JSON: A dictionary containing report dates.
    """
    try:
        report_id: str = request.args.get("id")
        if not report_id:
            return jsonify({"error": "No ID provided"}), 400

        report_id = int(report_id)

        points = qdrant_client.retrieve(
            collection_name="upload_dates", ids=[report_id], with_payload=True
        )

        if points and len(points) > 0:
            dates = points[0].payload.get("page_content", {})
            return jsonify({"report_id": report_id, "dates": dates}), 200
        else:
            return jsonify({"error": "Point not found"}), 404
    except Exception as e:
        logger.error(f"Error in /get_dates_by_id: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/generate_report", methods=["POST"])
def generate_report() -> Optional[Dict[str, str]]:
    """
    Endpoint to generate a report based on user-provided data.

    This endpoint generates a summary report based on the selected report. It will return
    a detailed summary of the insights, KPIs, anomalies, and relevant data from the report.

    Request Body:
        {
            "report_id": <str>,
            "fecha": <str>,
            "formato": <str>, (optional, default="Summary"),
            "query": <str> (optional, default=None)
        }

    Returns:
        json: A JSON object containing the generated report.
    """
    try:
        data = request.json
        report_id: str = data.get("report_id")
        fecha: str = data.get("fecha")
        formato: str = data.get("formato", "Summary")
        query: Optional[str] = data.get("query", None)

        report_content = inform_generator(
            qdrant_client=qdrant_client,
            formato=formato,
            report_id=report_id,
            fecha=fecha,
            query=query,
        )

        return report_content, 200, {"Content-Type": "text/markdown"}
    except Exception as e:
        logger.error(f"Error in /generate_report: {str(e)}", exc_info=True)
        return {"error": str(e)}, 500


@app.route("/update_data", methods=["POST"])
def update_data() -> Optional[Dict[str, str]]:
    """
    Endpoint to update data for specific collections.

    This endpoint allows the client to trigger updates for different collections in the system.
    The available update types are 'all', 'tabular', 'report_summary', 'text_pages', and 'metadata'...
    """
    update_type: str = request.json.get("update_type")
    time.sleep(
        15
    )  # to ensure collections are initialized, otherwise error will be shown
    try:
        if update_type == "all":
            db_creator_tabular.process_and_upload_data()
            db_creator_text_pages.process_and_upload_data()
            db_creator_report_sum.process_and_upload_data()
            db_creator_metadata.process_upload_dates()
            db_creator_metadata.process_element_names()
            db_creator_metadata.process_report_names()
            return (
                jsonify({"message": "Data updated for all collections."}),
                200,
            )

        elif update_type in [
            "tabular",
            "report_summary",
            "text_pages",
            "metadata",
        ]:
            updater = {
                "tabular": db_creator_tabular.process_and_upload_data,
                "report_summary": db_creator_report_sum.process_and_upload_data,
                "text_pages": db_creator_text_pages.process_and_upload_data,
                "metadata": lambda: (
                    db_creator_metadata.process_upload_dates(),
                    db_creator_metadata.process_element_names(),
                    db_creator_metadata.process_report_names(),
                ),
            }
            updater[update_type]()
            return (
                jsonify(
                    {
                        "message": f"Data updated for the {update_type} collection."
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Invalid update type."}), 400
    except Exception as e:
        logger.error(f"Error in /update_data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
