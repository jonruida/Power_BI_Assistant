#!/bin/bash

# Construir la imagen de Docker
docker build -t assistant_1 .

# Ejecutar el contenedor con las configuraciones especificadas
docker run -d --env-file ./.env \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    -v "$(pwd)/src/services/llm/rerank_llms:/qdrant//src/services/llm/rerank_llms:z" \
    -v "$(pwd)/tests/performance:/qdrant//tests/performance:z" \
    -p 6333:6333 -p 8501:8501 -p 8089:8089\
    assistant_1