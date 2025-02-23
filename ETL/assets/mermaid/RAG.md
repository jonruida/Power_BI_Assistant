flowchart TB
 subgraph subGraph0["."]
        D["fa:fa-filter SelfQueryRetriever"]
        n1["fa:fa-search Filtrar documentos por metadatos"]
        C["fa:fa-search Recuperador por similitud semántica"]
        A["fa:fa-database Base de datos de 6 colecciones"]
        E["fa:fa-sort Reclasificador: <br>Reordenar resultados por relevancia"]
  end
    D --> n1 & C
    n1 --> A
    C --> A
    A --> E
    E --> F["fa:fa-lightbulb Generar contexto para el modelo LLM"]
    F --> G["fa:fa-comments Generar respuestas a consultas"]
    B["fa:fa-vector-square Consulta"] --> D
    style D fill:#FFC107,stroke:#FFA000,color:#000000
    style n1 fill:#8BC34A,stroke:#689F38,color:#FFFFFF
    style C fill:#8BC34A,stroke:#689F38,color:#FFFFFF
    style A fill:#FF5722,stroke:#E64A19,color:#FFFFFF
    style E fill:#9C27B0,stroke:#7B1FA2,color:#FFFFFF
    style F fill:#00BCD4,stroke:#0097A7,color:#FFFFFF
    style G fill:#FF9800,stroke:#F57C00,color:#000000
    style B fill:#03A9F4,stroke:#0288D1,color:#FFFFFF
