"""Adaptador Ollama; falhas não são substituídas por vetores falsos."""
from langchain_ollama import OllamaEmbeddings


def criar_embeddings(config):
    kwargs = {'timeout': config.timeout, 'trust_env': False}
    if config.embedding_key:
        kwargs['headers'] = {'Authorization': 'Bearer ' + config.embedding_key}
    return OllamaEmbeddings(model=config.embedding_model, base_url=config.embedding_url,
                            client_kwargs=kwargs)
