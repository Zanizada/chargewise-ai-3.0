"""RAGAS real em .venv-evals; saídas separadas preservam coleta bruta.

python -m evals.avaliar_rag --arquivo evals/rag_runs/RUN.json
"""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
import math
from pathlib import Path
import logging
from ragas import EvaluationDataset, evaluate
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_ollama import ChatOllama, OllamaEmbeddings
from src.rag.config import carregar_rag_config


def avaliar(path):
    run = json.loads(path.read_text(encoding='utf-8'))
    cfg = carregar_rag_config()
    llm = LangchainLLMWrapper(ChatOllama(model='gpt-oss:120b', base_url=cfg.base_url,
        temperature=0, num_predict=4096,
        client_kwargs={'timeout':120,'headers':{'Authorization':'Bearer '+cfg.api_key}}))
    emb = LangchainEmbeddingsWrapper(OllamaEmbeddings(model=cfg.embedding_model,
        base_url=cfg.embedding_url,client_kwargs={'timeout':90,'trust_env':False}))
    casos, indices = [], []
    for i,r in enumerate(run['registros']):
        if r['caso']['grupo'] == 'respondivel' and r['resultado']['status'] == 'respondido':
            casos.append({'user_input':r['caso']['pergunta'], 'response':r['resultado']['resposta'],
                'retrieved_contexts':[c['texto'] for c in r['resultado']['contextos']]})
            indices.append(i)
        elif r['caso']['grupo'] == 'respondivel':
            r['revisao'].update(answer_relevancy=0,faithfulness=None,
                metodo='protocolo_abstencao_ou_erro',avaliador='regra publicada',
                justificativa='Pergunta respondível não recebeu resposta; relevância fim a fim zero, faithfulness N/A.')
    if casos:
        resultado = evaluate(EvaluationDataset.from_list(casos),
            metrics=[Faithfulness(llm=llm),ResponseRelevancy(llm=llm,embeddings=emb)],
            run_config=RunConfig(timeout=120,max_retries=1,max_workers=2),
            raise_exceptions=False,show_progress=True)
        for i,score in zip(indices,resultado.scores):
            rev=run['registros'][i]['revisao']
            for nome in ('faithfulness','answer_relevancy'):
                val=score.get(nome)
                rev[nome] = float(val) if val is not None and math.isfinite(float(val)) else None
            rev.update(metodo='RAGAS',avaliador='gpt-oss:120b',
                data=datetime.now(timezone.utc).isoformat(),justificativa='Métricas computadas por RAGAS; juiz automatizado, não revisão humana.')
    run['avaliador']={'metodo':'RAGAS','versao':version('ragas'),'modelo':'gpt-oss:120b',
        'temperature':0,'num_predict':4096,'embedding_model':cfg.embedding_model,
        'strictness':3,'max_workers':2,'max_retries':1,'limite':'Juiz automatizado; mesmo modelo da geração GPT-OSS pode introduzir viés.'}
    target=path.with_name(path.stem+'_avaliado.json')
    with target.open('x',encoding='utf-8') as f:
        json.dump(run,f,ensure_ascii=False,indent=2,allow_nan=False)
    print('Avaliação salva:',target.name,flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--arquivo',type=Path)
    parser.add_argument('--todos',type=Path)
    args=parser.parse_args()
    logging.getLogger('ragas').setLevel(logging.CRITICAL)
    paths=[args.arquivo] if args.arquivo else sorted(args.todos.glob('*.json')) if args.todos else []
    if not paths:
        parser.error('Informe --arquivo ou --todos DIRETORIO.')
    for path in paths:
        if not path.stem.endswith('_avaliado') and not path.with_name(path.stem+'_avaliado.json').exists():
            avaliar(path)


if __name__ == '__main__':
    main()
