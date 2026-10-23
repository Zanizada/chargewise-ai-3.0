"""Fronteira documental, citações exatas e metadados controlados pelo servidor.

Não comprova entailment semântico: a revisão/RAGAS continua necessária.
"""
import re
import unicodedata
from src.guardrails.moderation import verificar_entrada
from src.guardrails.scope_validator import normalizar
from src.schemas.resposta_rag import Citacao


def texto_normalizado(texto):
    return ' '.join(unicodedata.normalize('NFKC', texto).split())


def documento_suspeito(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFKC', texto)
                    if unicodedata.category(c) != 'Cf')
    if verificar_entrada(texto):
        return True
    return bool(re.search(r'(?:<\s*/?\s*(?:system|assistant)|\[INST\]|\b(?:api[_ -]?key|chave secreta)\b|'
                          r'execute.{0,50}(?:comando|powershell|shell)|substitua.{0,40}instrucoes)',
                          normalizar(texto), re.I | re.S))


def validar_rag(saida, documentos):
    if saida.status != 'respondido':
        if saida.afirmacoes:
            raise ValueError('Abstenção não pode trazer afirmações factuais.')
        return [], []
    if not saida.afirmacoes:
        raise ValueError('Resposta factual precisa de afirmações e fontes.')
    por_id = {d.metadata['chunk_id']: d for d in documentos}
    citacoes, textos = [], []
    for afirmacao in saida.afirmacoes:
        if verificar_entrada(afirmacao.texto) or documento_suspeito(afirmacao.texto):
            raise ValueError('Saída insegura.')
        numeros = []
        refs_numeradas = []
        for ref in afirmacao.referencias:
            doc = por_id.get(ref.chunk_id)
            if doc is None or texto_normalizado(ref.trecho) not in texto_normalizado(doc.page_content):
                raise ValueError('Citação inexistente ou trecho não corresponde à fonte recuperada.')
            numeros.append(ref.trecho)
            meta = doc.metadata
            citation = Citacao(chunk_id=ref.chunk_id, document_id=meta['document_id'],
                titulo=meta['title'], pagina=meta['page'] or None, secao=meta['section'],
                origem=meta['source'], natureza=meta['nature'], trecho=ref.trecho)
            if citation not in citacoes:
                citacoes.append(citation)
            refs_numeradas.append(str(citacoes.index(citation) + 1))
        # Números novos não podem ser acrescentados à paráfrase citada.
        evidencias = ' '.join(numeros)
        for numero in re.findall(r'\b\d+(?:[.,]\d+)*\b', afirmacao.texto):
            if numero not in re.findall(r'\b\d+(?:[.,]\d+)*\b', evidencias):
                raise ValueError('Número sem suporte no trecho citado.')
        textos.append(afirmacao.texto.strip() + ' [' + ', '.join(refs_numeradas) + ']')
    return textos, citacoes
