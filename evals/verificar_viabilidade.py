"""Provas reais com saídas redigidas: nunca imprimir chave ou corpo de erros."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import httpx
from src.config import RAIZ
from src.rag.config import carregar_rag_config


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--saida', type=Path, default=RAIZ / 'docs/viabilidade_modelos.json')
    args = p.parse_args()
    cfg = carregar_rag_config()
    result = {'data_utc': datetime.now(timezone.utc).isoformat(), 'chave_configurada': bool(cfg.api_key)}
    for nome, url, key in [('geracao', cfg.base_url, cfg.api_key),
                           ('embedding', cfg.embedding_url, cfg.embedding_key)]:
        headers = {'Authorization': 'Bearer ' + key} if key else {}
        try:
            with httpx.Client(timeout=60, headers=headers, trust_env=False) as client:
                r = client.get(url + '/api/tags')
                result[nome] = {'http': r.status_code,
                    'modelos': [m['name'] for m in r.json().get('models', [])] if r.is_success else []}
                if nome == 'embedding':
                    r = client.post(url + '/api/embed', json={'model': cfg.embedding_model,
                        'input': ['recarga de veículos elétricos', 'tarifa simulada']})
                    vs = r.json().get('embeddings', []) if r.is_success else []
                    result[nome].update(embed_http=r.status_code, vetores=len(vs),
                        dimensoes=[len(v) for v in vs])
        except Exception as exc:
            result[nome] = {'erro': 'endpoint inacessível ou resposta inválida', 'classe': type(exc).__name__}
    # Cloud Nomic é requisito separado; registrar a prova, mesmo se o índice usa local.
    try:
        with httpx.Client(timeout=30, headers={'Authorization': 'Bearer ' + cfg.api_key}) as c:
            r = c.post('https://ollama.com/api/embed', json={'model':'nomic-embed-text', 'input':'recarga'})
        result['nomic_cloud'] = {'http': r.status_code, 'disponivel': r.is_success}
    except Exception:
        result['nomic_cloud'] = {'disponivel': False, 'erro': 'endpoint inacessível'}
    with args.saida.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
