# Executar a interface

Na raiz do projeto, com Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-sprint04-lock.txt
Copy-Item .env.example .env  # somente se .env ainda não existir
# Configure chaves somente no arquivo local. Não cole em chats/logs.
.\.venv\Scripts\python.exe -m src.rag.obter_manual
.\.venv\Scripts\python.exe -m src.rag.ingest
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py --server.address 127.0.0.1
```

Acesse http://localhost:8501. Nomic local precisa estar instalado e Ollama aberto.
Geração cloud usa `RAG_BASE_URL=https://ollama.com`, `RAG_MODEL=gpt-oss:120b` e chave.
O PDF oficial é opcional/local. `EMBEDDING_BASE_URL` independente
permite configurar outro endpoint. Acesso por localhost é a forma
de apresentação definida pelo usuário.

Antes da ingestão, instale o Ollama e execute `ollama pull nomic-embed-text`.
Mantenha o serviço Ollama aberto. Configure `RAG_API_KEY` somente no `.env` local.

Para validar uma instalação nova, siga estes passos em uma cópia limpa do repositório,
com ambiente virtual e índice próprios. Baixe o manual, faça a ingestão e consulte
tarifa, regimento e uma pergunta sem resposta na base. Confira fontes na interface.
Compare o fingerprint do corpus com o registrado nos scores antes de afirmar que os
resultados anteriores são reproduzíveis: o download pode disponibilizar outro PDF.
Não é necessário refazer a avaliação só por publicar arquivos; mudanças no corpus,
prompt ou pipeline exigem nova avaliação para atribuir scores à versão alterada.

Verificação de 16/10: instalação em ambiente independente com o lock, manual baixado,
98 chunks, reingestão sem duplicação, 44 testes, consultas reais e interface AppTest
com citações passaram. O fingerprint coincide com os scores RAG publicados.
Veja `docs/verificacao_instalacao_limpa.json`; snapshot local publicável, sem copiar `.env`.

Limpar conversa afeta apenas a sessão atual. Reiniciar não apaga o índice.
Sem índice, a aplicação mostra instrução útil, não reingere automaticamente.
O modo operacional usa os defaults anteriores e mantém dados simulados.
