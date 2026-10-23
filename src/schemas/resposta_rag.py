"""Contrato documental independente dos campos financeiros operacionais."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ReferenciaModelo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_id: str = Field(min_length=1)
    trecho: str = Field(min_length=12, max_length=900)


class Afirmacao(BaseModel):
    model_config = ConfigDict(extra='forbid')
    texto: str = Field(min_length=1, max_length=1000)
    referencias: list[ReferenciaModelo] = Field(min_length=1, max_length=4)


class SaidaRAG(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['respondido', 'dados_insuficientes', 'recusado']
    afirmacoes: list[Afirmacao] = Field(default_factory=list, max_length=6)


class Citacao(BaseModel):
    chunk_id: str
    document_id: str
    titulo: str
    pagina: int | None
    secao: str
    origem: str
    natureza: str
    trecho: str


class RespostaRAG(BaseModel):
    status: Literal['respondido', 'dados_insuficientes', 'recusado', 'erro']
    resposta: str
    citacoes: list[Citacao] = Field(default_factory=list)
    modelo: str
    prompt: str
    prompt_sha256: str
    latencia_segundos: float = 0
    tokens_entrada: int | None = None
    tokens_saida: int | None = None
    contextos: list[dict] = Field(default_factory=list)
    documentos_excluidos: int = 0
    erro_codigo: str | None = None
