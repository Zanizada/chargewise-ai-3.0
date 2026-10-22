"""Scores são distâncias de cosseno: menor é mais próximo, não score de qualidade."""
from src.rag.vector_store import abrir_indice
from src.guardrails.scope_validator import normalizar


class Retriever:
    def __init__(self, config, embeddings=None):
        self.config = config
        self.store, self.manifest = abrir_indice(config, embeddings)

    def buscar(self, pergunta):
        # Categoria explicitamente pedida evita mistura de regimento com manual técnico.
        # Continua sendo busca semântica; nenhum gabarito é usado na recuperação.
        texto = normalizar(pergunta)
        categoria = next((cat for termo,cat in [('regimento','regimento'),('faq','faq'),
                         ('tabela','tarifa')] if termo in texto), None)
        filtro = {'category':categoria} if categoria else None
        resultados = self.store.similarity_search_with_score(pergunta, k=self.config.k, filter=filtro)
        return [(doc, float(dist)) for doc, dist in resultados
                if float(dist) <= self.config.max_distance]
