"""Configuração central. Paths independem da pasta de onde você executou."""
import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    modo: str = "demo"
    base_url: str = "http://localhost:11434"
    modelo: str = "gpt-oss:120b"
    api_key: str = field(default="", repr=False)
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 512
    timeout: float = 90
    max_turnos: int = 6
    prompt_versao: str = "v2"
    contar_tokens: bool = False

    def __post_init__(self):
        if self.modo not in {"demo", "manual", "lcel"}:
            raise ValueError("Modo deve ser demo, manual ou lcel.")
        if self.prompt_versao not in {"v1", "v2"}:
            raise ValueError("Prompt deve ser v1 ou v2.")
        url = urlsplit(self.base_url)
        if url.scheme not in {"http", "https"} or not url.hostname:
            raise ValueError("OLLAMA_BASE_URL deve ser um endereço HTTP(S).")
        if url.username or url.password or url.query or url.fragment:
            raise ValueError("Use URL sem credenciais, query ou fragmento.")
        if not math.isfinite(self.temperature) or not 0 <= self.temperature <= 2:
            raise ValueError("TEMPERATURE deve estar entre 0 e 2.")
        if not math.isfinite(self.top_p) or not 0 < self.top_p <= 1:
            raise ValueError("TOP_P deve estar entre 0 (exclusivo) e 1.")
        if (not math.isfinite(self.timeout) or self.timeout <= 0
                or self.max_tokens < 1 or self.max_turnos < 1):
            raise ValueError("Timeout, limite de saída e número de turnos devem ser positivos.")
        if not self.modelo.strip():
            raise ValueError("Informe OLLAMA_MODEL.")


def carregar_config(modo=None, prompt=None):
    load_dotenv(RAIZ / ".env", override=False)
    return Config(
        modo=modo or os.getenv("CHARGEWISE_MODO", "demo"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        modelo=os.getenv("OLLAMA_MODEL", "gpt-oss:120b"),
        api_key=os.getenv("OLLAMA_API_KEY", ""),
        temperature=float(os.getenv("TEMPERATURE", "0.2")),
        top_p=float(os.getenv("TOP_P", "0.9")),
        max_tokens=int(os.getenv("MAX_TOKENS", "512")),
        timeout=float(os.getenv("TIMEOUT_SEGUNDOS", "90")),
        max_turnos=int(os.getenv("MAX_TURNOS", "6")),
        prompt_versao=prompt or os.getenv("PROMPT_VERSAO", "v2"),
        contar_tokens=os.getenv("CONTAR_TOKENS", "false").lower() == "true",
    )
