"""Coleta RAG real. Não fabrica notas e não sobrescreve runs.

python -m evals.executar_rag --modelos gpt-oss:120b gemma4:31b --prompts v1 v2
"""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
from langchain_core.documents import Document
from src.config import RAIZ
from src.rag.config import carregar_rag_config
from src.rag.service import ServicoRAG
from src.rag.retriever import Retriever


class RetrieverCaso:
    def __init__(self, original):
        self.original = original
        self.fixture = None

    def buscar(self, pergunta):
        if self.fixture:
            doc = Document(page_content=self.fixture,
                metadata={'chunk_id': 'fixture-ataque', 'document_id': 'fixture-ataque',
                    'title': 'Documento adversarial de teste', 'source': 'evals/fixtures',
                    'nature': 'teste', 'page': 1, 'section': 'ataque'})
            return [(doc, 0.0)]
        return self.original.buscar(pergunta)


def coletar(config, casos, repeticao):
    retriever = RetrieverCaso(Retriever(config))
    bot = ServicoRAG(config, retriever=retriever)
    registros = []
    for caso in casos:
        fixture = caso.get('fixture')
        retriever.fixture = ((RAIZ / 'evals/fixtures' / fixture).read_text(encoding='utf-8')
                            if fixture else None)
        resultado = bot.responder(caso['pergunta'], caso.get('sessao') or caso['id'])
        registros.append({'caso': caso, 'resultado': resultado.model_dump(),
            'revisao': {'avaliador': None, 'data': None, 'metodo': None,
                        'faithfulness': None, 'answer_relevancy': None,
                        'justificativa': None, 'afirmacoes': []}})
        print(caso['id'], resultado.status, flush=True)
    return {'tipo': 'rag_real', 'data_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'repeticao': repeticao,
        'config': config.publico(), 'indice': retriever.original.manifest,
        'prompt_sha256': bot.prompt_hash,
        'pipeline_sha256': sha256(b''.join(p.read_bytes() for p in sorted((RAIZ/'src/rag').glob('*.py')))
            + (RAIZ/'src/guardrails/rag_validator.py').read_bytes()).hexdigest(),
        'hash_casos': sha256((RAIZ / 'evals/rag_cases.json').read_bytes()).hexdigest(),
        'dependencias': {p: version(p) for p in ['langchain-core', 'langchain-ollama',
             'chromadb', 'langchain-chroma', 'pymupdf']}, 'registros': registros}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--modelos', nargs='+', default=['gpt-oss:120b'])
    parser.add_argument('--prompts', nargs='+', choices=['v1', 'v2'], default=['v1', 'v2'])
    parser.add_argument('--repeticoes', type=int, default=1)
    parser.add_argument('--saida', type=Path, default=RAIZ / 'evals/rag_runs')
    args = parser.parse_args()
    if args.repeticoes < 1:
        parser.error('Repetições devem ser positivas.')
    config = carregar_rag_config()
    casos = json.loads((RAIZ / 'evals/rag_cases.json').read_text(encoding='utf-8'))
    args.saida.mkdir(parents=True, exist_ok=True)
    for modelo in args.modelos:
        for prompt in args.prompts:
            for rep in range(1, args.repeticoes + 1):
                dados = coletar(replace(config, modelo=modelo, prompt=prompt), casos, rep)
                agora = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                nome_modelo = ''.join(c if c.isalnum() else '_' for c in modelo)
                path = args.saida / f'{nome_modelo}_{prompt}_{agora}.json'
                with path.open('x', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                print('Run salvo:', path.name, flush=True)


if __name__ == '__main__':
    main()
