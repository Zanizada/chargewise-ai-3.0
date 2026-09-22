"""Heurística simples usada no demo. Não é um classificador confiável de escopo."""
import unicodedata


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def identificar_intencao(pergunta):
    texto = normalizar(pergunta)
    grupos = [
        ("cobranca", ("cobrad", "cobranc", "custou", "valor", "paguei")),
        ("consumo", ("consum", "este mes", "mensal")),
        ("agendamento", ("reserv", "agend", "horario")),
        ("suporte", ("suporte", "falha", "nao inicia", "erro")),
        ("sessao", ("ultima sessao", "ultima recarga")),
        ("disponibilidade", ("disponiv", "livre", "ocupad")),
    ]
    for intencao, termos in grupos:
        if any(termo in texto for termo in termos):
            return intencao
    return "indefinida"

# TODO S3-04: avaliar escopo com histórico e medir falsos bloqueios.
