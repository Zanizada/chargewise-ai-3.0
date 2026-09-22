"""Barreiras determinísticas de entrada; cobertura limitada a padrões conhecidos."""
import re
import unicodedata
from src.guardrails.scope_validator import normalizar
from src.schemas.consulta_recarga import ConsultaRecarga


def verificar_entrada(pergunta):
    texto = normalizar(unicodedata.normalize("NFKC", pergunta))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Cf")
    texto = " ".join(texto.split())
    ataques = [
        r"\b(?:ignore|ignorar|desconsidere|esqueca|ignore all|disregard)\b.{0,60}\b(?:regras|instrucoes|instructions|rules)\b",
        r"\b(?:revele|mostre|exiba|imprima|repita|reveal|show)\b.{0,60}\b(?:system prompt|prompt (?:do sistema|interno|original)|instrucoes (?:internas|do sistema))\b",
        r"\brevele\b.{0,60}\bprompt\b",
        r"\bfinja que nao (?:tem|existem) regras\b",
        r"\b(?:ative|entre|act as|enable)\b.{0,30}\b(?:modo desenvolvedor|developer mode|dan)\b",
        r"\b(?:sem restricoes|sem filtros)\b.{0,30}\b(?:responda|responder)\b",
    ]
    if any(re.search(padrao, texto) for padrao in ataques):
        return ConsultaRecarga(intencao="fora_escopo", status="recusado",
            resposta="Não vou alterar as regras do assistente. Posso ajudar com consultas de recarga GoodWe.")

    restritos = {
        "eletricista habilitado": [
            r"\b(?:burlar|desativar|remover|anular|contornar)\b.{0,45}\b(?:protecao|aterramento|disjuntor|intertravamento)\b",
            r"\b(?:ligar|conectar|emendar|trocar|cortar)\b.{0,25}\b(?:fios|fiacao)\b",
            r"\babrir\b.{0,20}\bquadro\b",
        ],
        "profissional jurídico habilitado": [r"\bparecer juridico\b", r"\bdevo processar\b",
            r"\b(?:como|quero)\b.{0,30}\bprocessar\b", r"\b(?:redija|elabore)\b.{0,30}\bpeticao\b"],
        "profissional financeiro habilitado": [r"\bonde investir\b", r"\bqual investimento\b",
            r"\b(?:recomende|indique)\b.{0,30}\b(?:investimento|acoes|fundos)\b"],
    }
    for profissional, padroes in restritos.items():
        if any(re.search(padrao, texto) for padrao in padroes):
            return ConsultaRecarga(intencao="fora_escopo", status="encaminhar",
                resposta=f"Não forneço esse aconselhamento. Procure um {profissional}.",
                encaminhamento=profissional)
    return None
