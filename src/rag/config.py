"""Configuração RAG: nenhum segredo é serializado em manifestos."""
from dataclasses import dataclass, field
from pathlib import Path
import math
import os
from urllib.parse import urlsplit
from dotenv import load_dotenv
from src.config import RAIZ


def validar_url(valor):
    url = urlsplit(valor)
    if (url.scheme not in {'http', 'https'} or not url.hostname or url.username
            or url.password or url.query or url.fragment):
        raise ValueError('Endpoint deve ser HTTP(S), sem credenciais/query/fragmento.')


@dataclass(frozen=True)
class RAGConfig:
    base_url: str = 'http://localhost:11434'
    modelo: str = 'gpt-oss:120b'
    api_key: str = field(default='', repr=False)
    embedding_url: str = 'http://localhost:11434'
    embedding_model: str = 'nomic-embed-text'
    embedding_key: str = field(default='', repr=False)
    knowledge_dir: Path = RAIZ / 'data/knowledge_base'
    persist_dir: Path = RAIZ / 'data/chroma'
    prompt: str = 'v2'
    k: int = 4
    chunk_size: int = 900
    chunk_overlap: int = 150
    max_distance: float = 0.55
    temperature: float = 0
    top_p: float = 0.9
    max_tokens: int = 2048
    timeout: float = 90
    max_history_turns: int = 4
    max_context_chars: int = 6000

    def __post_init__(self):
        validar_url(self.base_url)
        validar_url(self.embedding_url)
        if self.prompt not in {'v1', 'v2'}:
            raise ValueError('Prompt RAG deve ser v1 ou v2.')
        if not self.modelo.strip() or not self.embedding_model.strip():
            raise ValueError('Modelos não podem ser vazios.')
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError('Overlap deve ser menor que chunk_size e não negativo.')
        if min(self.k, self.max_tokens, self.timeout, self.max_history_turns, self.max_context_chars) <= 0:
            raise ValueError('Limites RAG devem ser positivos.')
        if not all(math.isfinite(v) for v in (self.temperature, self.top_p, self.timeout, self.max_distance)):
            raise ValueError('Parâmetros devem ser finitos.')
        if not 0 <= self.temperature <= 2 or not 0 < self.top_p <= 1 or not 0 <= self.max_distance <= 2:
            raise ValueError('Parâmetros RAG fora do intervalo.')

    def publico(self):
        return {k: getattr(self, k) for k in ('modelo', 'embedding_model', 'prompt', 'k',
                'chunk_size', 'chunk_overlap', 'max_distance', 'temperature', 'top_p',
                'max_tokens', 'timeout', 'max_history_turns', 'max_context_chars')}


def carregar_rag_config(**overrides):
    load_dotenv(RAIZ / '.env', override=False)
    cfg = dict(
        base_url=os.getenv('RAG_BASE_URL', os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')).rstrip('/'),
        modelo=os.getenv('RAG_MODEL', os.getenv('OLLAMA_MODEL', 'gpt-oss:120b')),
        api_key=os.getenv('RAG_API_KEY') or os.getenv('OLLAMA_API_KEY', ''),
        embedding_url=os.getenv('EMBEDDING_BASE_URL', 'http://localhost:11434').rstrip('/'),
        embedding_model=os.getenv('EMBEDDING_MODEL', 'nomic-embed-text'),
        embedding_key=os.getenv('EMBEDDING_API_KEY', ''),
        persist_dir=Path(os.getenv('RAG_PERSIST_DIR', str(RAIZ / 'data/chroma'))).resolve(),
        prompt=os.getenv('RAG_PROMPT', 'v2'), k=int(os.getenv('RAG_K', '4')),
        chunk_size=int(os.getenv('RAG_CHUNK_SIZE', '900')),
        chunk_overlap=int(os.getenv('RAG_CHUNK_OVERLAP', '150')),
        max_distance=float(os.getenv('RAG_MAX_DISTANCE', '0.55')),
        temperature=float(os.getenv('RAG_TEMPERATURE', '0')),
        top_p=float(os.getenv('RAG_TOP_P', '0.9')),
        max_tokens=int(os.getenv('RAG_MAX_TOKENS', '2048')),
        timeout=float(os.getenv('RAG_TIMEOUT', '90')),
    )
    cfg.update(overrides)
    return RAGConfig(**cfg)
