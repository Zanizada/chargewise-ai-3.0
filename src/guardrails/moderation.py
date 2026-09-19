"""Exemplos de bloqueios explícitos. Cobertura parcial, a ampliar com avaliações."""
import re
from src.guardrails.scope_validator import normalizar
from src.schemas.consulta_recarga import ConsultaRecarga


def verificar_entrada(pergunta):
    texto = normalizar(pergunta)
    ataques = [r"ignore (as |todas as )?(regras|instrucoes)",
               r"revele .*prompt", r"finja que nao (tem|existem) regras"]
    if any(re.search(padrao, texto) for padrao in ataques):
        return ConsultaRecarga(intencao="fora_escopo", status="recusado",
                               resposta="Não vou alterar as regras do assistente. Posso ajudar com consultas de recarga GoodWe.")
    restritos = {
        "eletricista habilitado": ("burlar protecao", "ligar os fios", "abrir o quadro"),
        "profissional jurídico habilitado": ("parecer juridico", "devo processar"),
        "profissional financeiro habilitado": ("onde investir", "qual investimento"),
    }
    for profissional, termos in restritos.items():
        if any(termo in texto for termo in termos):
            return ConsultaRecarga(intencao="fora_escopo", status="encaminhar",
                                   resposta=f"Não forneço esse aconselhamento. Procure um {profissional}.",
                                   encaminhamento=profissional)
    return None

# TODO S3-04: adicionar casos indiretos, variações e validação de saída.
# Não bloquear toda ocorrência de "ignore": ela pode ser uma correção legítima.
