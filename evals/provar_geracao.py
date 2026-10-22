"""Prova de autenticação e geração dos modelos selecionados, sem imprimir respostas."""
from datetime import datetime, timezone
import json
import httpx
from src.config import RAIZ
from src.rag.config import carregar_rag_config


def main():
    cfg = carregar_rag_config()
    resultados = {'data_utc': datetime.now(timezone.utc).isoformat(), 'modelos': []}
    for modelo in ['gpt-oss:120b', 'gemma4:31b']:
        try:
            with httpx.Client(timeout=90, headers={'Authorization':'Bearer ' + cfg.api_key}) as c:
                r = c.post(cfg.base_url + '/api/chat', json={'model': modelo,
                    'stream':False, 'messages':[{'role':'user','content':'Responda apenas OK.'}],
                    'options':{'temperature':0,'num_predict':128}})
            data = r.json() if r.is_success else {}
            resultados['modelos'].append({'modelo':modelo,'http':r.status_code,
                'gerou_conteudo':bool(data.get('message',{}).get('content')),
                'tokens_entrada':data.get('prompt_eval_count'),'tokens_saida':data.get('eval_count')})
        except Exception as exc:
            resultados['modelos'].append({'modelo':modelo,'erro':type(exc).__name__})
    path = RAIZ/'docs/prova_geracao.json'
    with path.open('x',encoding='utf-8') as f:
        json.dump(resultados,f,ensure_ascii=False,indent=2)
    print(json.dumps(resultados,indent=2))


if __name__ == '__main__':
    main()
