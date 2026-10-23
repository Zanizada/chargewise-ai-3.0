# Fluxograma do ChargeWise AI

Representa a implementação atual, incluindo terminal e interface Streamlit.
GitHub renderiza os diagramas Mermaid abaixo. Não representa uma prova histórica
de entrega da Sprint 1.

## Visão geral

```mermaid
flowchart TD
    U[Usuário: morador ou administração] --> I[Terminal ou interface Streamlit]
    I --> T{Tipo de consulta}
    T -->|Documental| D[Serviço RAG]
    T -->|Operacional simulada| O[Chatbot operacional]
    D --> RD[Resposta com documento, seção ou página e trecho]
    O --> RO[Resposta estruturada com fontes do cenário simulado]
    RD --> U
    RO --> U
```

## Consulta operacional e núcleo LCEL

```mermaid
flowchart TD
    E[Pergunta e identificador de sessão] --> V[Validar tamanho e sessão]
    V --> G{Moderação detecta ataque ou aconselhamento restrito?}
    G -->|Sim| R[Recusar ou orientar profissional habilitado]
    G -->|Não| H[Obter histórico da sessão e cenário simulado]
    H --> P[System prompt versionado + schema JSON + contexto]
    P --> M{Modo configurado}
    M -->|LCEL| C[ChatPromptTemplate + histórico]
    C --> L[ChatOllama]
    L --> S[PydanticOutputParser]
    S --> F[Validar fontes e campos contra o contexto]
    F --> A{Saída aceita?}
    A -->|Sim| B[RunnableWithMessageHistory registra turno validado]
    B --> N[ConversationTokenBufferMemory limita tokens e remove turnos antigos]
    N --> RS[Resumo determinístico dos assuntos descartados, sem fatos ou valores]
    RS --> X[Exibir resposta]
    A -->|Não| ER[Exibir falha sem salvar turno nem substituir por demo]
    M -->|Manual| HTTP[API Ollama via HTTP]
    M -->|Demo| DEMO[Regras determinísticas sem IA]
    HTTP --> PV[Validar schema, fontes e campos]
    DEMO --> PV
    PV --> OK{Saída aceita?}
    OK -->|Sim| HM[Salvar histórico limitado por turnos]
    HM --> X
    OK -->|Não| ER
```

Falhas de conexão e parsing também seguem para a saída de erro. A memória LCEL
atual resume assuntos dos turnos descartados por regras; o resumo compartilha o
orçamento de tokens e não permite reconstruir perguntas exatas. Recusas da moderação não chamam LLM.
Tiktoken estima tokens; contadores do endpoint são registrados quando disponíveis.

## Consulta documental RAG

```mermaid
flowchart TD
    KB[Documentos públicos e manual opcional local] --> LD[PyMuPDFLoader ou leitura Markdown]
    LD --> CH[Chunking recursivo e metadados por página ou seção]
    CH --> EM[Embeddings Nomic locais]
    EM --> DB[(Chroma persistente)]
    Q[Pergunta e sessão] --> GU{Moderação ou fora de domínio reconhecido?}
    GU -->|Sim| RE[Recusa ou orientação segura]
    GU -->|Não| BUS[Busca semântica com Nomic local e top-k]
    DB --> BUS
    BUS --> FIL[Filtrar trechos suspeitos e limitar contexto]
    FIL --> EV{Há evidência recuperada?}
    EV -->|Não| AB[Informar dados insuficientes]
    EV -->|Sim| PR[Prompt RAG versionado + contexto + histórico limitado]
    PR --> LL[ChatOllama no Cloud]
    LL --> VA[Validar JSON, referências, trechos literais e números]
    VA --> SU{Resposta válida?}
    SU -->|Não| ERR[Informar erro sem salvar histórico]
    SU -->|Sim| ST{Status respondido?}
    ST -->|Não| ABR[Exibir recusa ou dados insuficientes]
    ST -->|Sim| SAVE[Salvar turno no histórico da sessão]
    SAVE --> UI[Exibir afirmações e citações na interface ou CLI]
```

Citações válidas e filtros são controles técnicos; não garantem correção semântica
universal. Qualidade é avaliada separadamente com RAGAS e revisão das respostas.
