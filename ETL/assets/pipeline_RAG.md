```mermaid
graph TD

   J[User makes a query]
    J --> |LLM + EnsembleRetriever process the query|K[Self Querying]
    K --> K1[LLM generates metadata filter]
    K1 --> K2[Similarity search in text_chunks, top 5]
    K1 --> K3[Similarity search in table_elements, top 10]
    
    K2 --> R1[Rerank with mini LLM for text_chunks, top 1]
    K3 --> R2[Rerank with mini LLM for table_elements, top 5]
    
    R1 --> M1[Filtered results from text_chunks]
    R2 --> M2[Filtered results from table_elements]
    
    M1 --> M[Combine retrievers with EnsembleRetriever]
    M2 --> M
    
    M --> N[Generate response with context]


    ```
