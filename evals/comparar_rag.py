"""Comparação que rejeita conjuntos, índices e parâmetros incompatíveis."""
import argparse
import json
from pathlib import Path


def resumo(run):
    registros = run['registros']
    resp = [r for r in registros if r['caso']['grupo'] == 'respondivel']
    def media(campo):
        valores = [r['revisao'][campo] for r in resp if r['revisao'][campo] is not None]
        return {'media': sum(valores)/len(valores) if valores else None,
                'avaliados': len(valores), 'total': len(resp)}
    return {'faithfulness': media('faithfulness'), 'answer_relevancy': media('answer_relevancy'),
        'fonte_esperada_no_contexto': {
            'acertos': sum(bool(set(r['caso']['fontes']) & {c['metadata']['document_id']
                for c in r['resultado']['contextos']}) for r in resp), 'total': len(resp)},
        'total': len(registros), 'falhas': sum(r['resultado']['status'] == 'erro' for r in registros),
        'status_esperado': sum(r['resultado']['status'] == r['caso']['status'] for r in registros),
        'respostas_factuais': sum(r['resultado']['status'] == 'respondido' for r in registros),
        'com_citacao': sum(bool(r['resultado']['citacoes']) for r in registros),
        'latencia_media': sum(r['resultado']['latencia_segundos'] for r in registros)/len(registros)}


def comparar(a, b):
    if a['hash_casos'] != b['hash_casos'] or a['indice']['fingerprint'] != b['indice']['fingerprint']:
        raise ValueError('Conjunto ou índice mudou; comparação de ganho inválida.')
    if a.get('pipeline_sha256') != b.get('pipeline_sha256'):
        raise ValueError('Pipeline mudou; não atribuir ganho exclusivamente ao prompt.')
    if a.get('avaliador') != b.get('avaliador'):
        raise ValueError('Avaliador diferente; comparação de score inválida.')
    for campo in ('k', 'chunk_size', 'chunk_overlap', 'temperature', 'top_p', 'max_tokens',
                  'max_distance', 'max_context_chars', 'max_history_turns'):
        if a['config'][campo] != b['config'][campo]:
            raise ValueError(f'Parâmetro diferente: {campo}.')
    antes, depois = resumo(a), resumo(b)
    deltas = {}
    for campo in ('faithfulness', 'answer_relevancy'):
        x, y = antes[campo], depois[campo]
        completos = x['avaliados'] == x['total'] and y['avaliados'] == y['total']
        deltas[campo] = (y['media'] - x['media'] if completos else None)
    return {'antes': antes, 'depois': depois, 'deltas': deltas,
        'ganho_comprovado': all(v is not None and v >= 0 for v in deltas.values())
                           and any(v is not None and v > 0 for v in deltas.values())}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('antes', type=Path)
    p.add_argument('depois', type=Path)
    args = p.parse_args()
    runs = [json.loads(path.read_text(encoding='utf-8')) for path in (args.antes, args.depois)]
    print(json.dumps(comparar(*runs), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
