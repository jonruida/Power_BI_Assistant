#!/bin/bash

# Construir la imagen de Docker
docker build -t assistant .

# Ejecutar el contenedor con las configuraciones especificadas
docker run -d --env-file ./.env \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    -v "$(pwd)/src/services/llm/rerank_llms:/qdrant/src/services/llm/rerank_llms:z" \
    -v "$(pwd)/tests/performance/assistant_qa:/qdrant/tests/performance/assistant_qa:z" \
    -v "$(pwd)/tests/performance/flask_server:/qdrant/tests/performance/flask_server:z" \
    -p 6633:6333 -p 8601:8501 -p 8689:8089 \
    assistant