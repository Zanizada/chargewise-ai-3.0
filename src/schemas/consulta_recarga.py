"""Primeiro contrato EV. Expanda com os campos necessários ao projeto."""
import math
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConsultaRecarga(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intencao: Literal["disponibilidade", "consumo", "cobranca", "sessao",
                      "agendamento", "suporte", "fora_escopo", "indefinida"]
    status: Literal["respondido", "dados_insuficientes", "recusado", "encaminhar"]
    resposta: str
    carregador_id: str | None = None
    energia_kwh: float | None = None
    valor_brl: float | None = None
    fontes: list[str] = Field(default_factory=list)
    encaminhamento: str | None = None

    @field_validator("resposta")
    @classmethod
    def resposta_nao_vazia(cls, valor):
        if not valor.strip():
            raise ValueError("A resposta não pode estar vazia.")
        return valor.strip()

    @field_validator("energia_kwh", "valor_brl", mode="before")
    @classmethod
    def medida_valida(cls, valor):
        if valor is None:
            return None
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("Medidas devem ser números JSON ou null.")
        if not math.isfinite(valor) or valor < 0:
            raise ValueError("Medidas devem ser finitas e não negativas.")
        return valor

    # TODO S3-01: acrescentar estado_carregador, potencia_kw e suas regras.
    # TODO S3-01: validar coerência entre status, fontes e encaminhamento.
