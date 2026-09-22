"""Confere campos estruturados e valores explícitos contra o contexto.

Não é um verificador semântico completo do texto livre nem de especificações
de produtos. Não autoriza ações sobre equipamentos, reservas ou pagamentos.
"""
from decimal import Decimal, InvalidOperation
import re
from src.guardrails.moderation import verificar_entrada


class RespostaNaoConfiavel(RuntimeError):
    def __init__(self):
        super().__init__("Resposta rejeitada: não foi possível confirmar os dados nas fontes fornecidas.")


def validar_saida(resposta, contexto):
    if resposta.status == "respondido" and verificar_entrada(resposta.resposta) is not None:
        raise RespostaNaoConfiavel()
    fontes_permitidas = {"carregadores", "consumo_mensal", "ultima_sessao"}
    fontes = resposta.fontes
    if len(fontes) != len(set(fontes)):
        raise RespostaNaoConfiavel()
    if any(f not in fontes_permitidas or not contexto.get(f) for f in fontes):
        raise RespostaNaoConfiavel()

    registros = []
    for fonte in fontes:
        dado = contexto[fonte]
        if fonte == "carregadores":
            if not isinstance(dado, list) or any(not isinstance(c, dict) for c in dado):
                raise RespostaNaoConfiavel()
            registros.extend({"carregador_id": c.get("id")} for c in dado)
        else:
            if not isinstance(dado, dict):
                raise RespostaNaoConfiavel()
            registros.append(dado)

    campos = {k: getattr(resposta, k) for k in ("carregador_id", "energia_kwh", "valor_brl")
              if getattr(resposta, k) is not None}
    # Um único registro precisa sustentar a combinação inteira: não misturar
    # energia mensal com valor de outra sessão, mesmo citando as duas fontes.
    if campos and not any(all(dado.get(k) == v for k, v in campos.items()) for dado in registros):
        raise RespostaNaoConfiavel()
    esperado = {"consumo": "consumo_mensal", "sessao": "ultima_sessao",
                "disponibilidade": "carregadores"}
    if resposta.status == "respondido" and resposta.intencao == "cobranca":
        if not set(fontes).intersection({"consumo_mensal", "ultima_sessao"}):
            raise RespostaNaoConfiavel()
    if resposta.status == "respondido" and resposta.intencao in esperado:
        if esperado[resposta.intencao] not in fontes:
            raise RespostaNaoConfiavel()
        if resposta.intencao != "disponibilidade":
            dado = contexto[esperado[resposta.intencao]]
            if not isinstance(dado, dict) or any(dado.get(k) != v for k, v in campos.items()):
                raise RespostaNaoConfiavel()

    # Quantias e energia no texto precisam ter correspondência nos campos
    # já conferidos; casos ambíguos falham de forma conservadora.
    numero = r"\d+(?:[.,]\d+)*"
    for padrao, campo in [(rf"R\$\s*({numero})", "valor_brl"),
                          (rf"({numero})\s*kWh\b", "energia_kwh")]:
        for trecho in re.findall(padrao, resposta.resposta, flags=re.IGNORECASE):
            if "," in trecho:
                trecho = trecho.replace(".", "").replace(",", ".")
            try:
                valor = Decimal(trecho)
            except InvalidOperation:
                raise RespostaNaoConfiavel() from None
            informado = getattr(resposta, campo)
            if informado is None or valor != Decimal(str(informado)):
                raise RespostaNaoConfiavel()
    return resposta
