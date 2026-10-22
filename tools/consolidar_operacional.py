"""Consolida medições reais e revisão IA explícita, sem criar notas humanas."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
from evals.executar_comparativo_sprint3 import resumo

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--revisao',type=Path,required=True)
    parser.add_argument('--saida',type=Path,default=ROOT/'evals/sprint3_results.json')
    args = parser.parse_args()
    revisao = json.loads(args.revisao.read_text(encoding='utf-8'))
    resultados = []
    referencia = None
    for condicao in ['manual_v1','lcel_v1','lcel_v2','lcel_v4']:
        path = args.runs/(condicao+'.json')
        run = json.loads(path.read_text(encoding='utf-8'))
        identidade = (run['hash_casos'],run['hash_contextos'],run['codigo_sha256'],
                      run['modelo'],run['parametros'])
        if referencia is None:
            referencia = identidade
        if identidade != referencia or len(run['registros']) != 19:
            raise ValueError('Condições incompatíveis ou coleta incompleta.')
        notas = revisao['condicoes'][condicao]
        revistos = []
        for r in run['registros']:
            nota = notas[r['caso']['id']]
            if nota['nota'] not in [0,1,2] or not nota['justificativa'].strip():
                raise ValueError('Revisão ausente ou inválida.')
            revistos.append({'id':r['caso']['id'],**nota})
        metricas = resumo(run['registros'])
        metricas['qualidade_ia_media_0_2'] = mean(n['nota'] for n in revistos)
        resultados.append({'condicao':condicao,'run':path.resolve().relative_to(ROOT).as_posix(),
            'run_sha256':sha256(path.read_bytes()).hexdigest(),'metricas':metricas,
            'revisao_ia':revistos})
    dados = {'descricao':'Experimento atual; referência manual não representa entrega histórica da Sprint 2.',
        'modelo':run['modelo'],'parametros':run['parametros'],'hash_casos':run['hash_casos'],
        'hash_contextos':run['hash_contextos'],'codigo_sha256':run['codigo_sha256'],
        'metodo_qualitativo':revisao['metodo'],'rubrica':revisao['rubrica'],
        'revisao_humana':'Pendente; notas são assistidas por IA, não atribuídas aos integrantes.',
        'limites':['Uma repetição, 19 casos; sem significância estatística.',
            'Quatro turnos por condição são resolvidos por guardrails sem modelo.',
            'Tokens do serviço em LCEL só estão disponíveis em saídas aceitas; cobertura explícita.',
            'Comparação manual/LCEL usa mesmo prompt v1; ganho de prompt usa LCEL v1/v2/v4.',
            'Referência manual e LCEL usam políticas de memória diferentes.'],
        'condicoes':resultados}
    with args.saida.open('x',encoding='utf-8') as f:
        json.dump(dados,f,ensure_ascii=False,indent=2)
    linhas = ['# Comparação operacional — Sprints 2/3', '',
        'Coleta real atual com GPT-OSS 120B no Ollama Cloud. Referência manual executada',
        'agora; não reconstrói nem comprova uma entrega histórica. Notas qualitativas',
        'abaixo foram atribuídas por revisão assistida por IA (Codex), pendentes de revisão humana.', '',
        '| Condição | Checagens /19 | Falhas /19 | Qualidade IA (0–2) | Latência todos (s) | Tokens entrada estimados (15 turnos) | Campos corretos /6 | Saídas aceitas com modelo /15 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for e in resultados:
        m = e['metricas']
        linhas.append(f"| {e['condicao']} | {m['checagens_ok']} | {m['falhas']} | {m['qualidade_ia_media_0_2']:.4f} | {m['latencia_todos_media']:.4f} | {m['tokens_entrada_estimados']['media']:.2f} | {m['campos_corretos']} | {m['schema_e_evidencias_validos']} |")
    linhas += ['', '## Interpretação e parâmetros', '',
        'Comparar manual v1 com LCEL v1 isola a mudança de integração/memória, mantendo',
        'o prompt; não se deve atribuir ao LCEL o ganho obtido ao trocar também o prompt.',
        'LCEL v1, v2 e v4 foram avaliados com o mesmo código, casos, contexto e parâmetros.',
        'temperature=0; top_p=0,9; max_tokens=2048; timeout=45 s; sem retries.',
        'Manual retém 6 turnos; LCEL tem 2048 tokens totais, até 128 reservados ao resumo',
        'determinístico de assuntos. Os casos de memória incluem três turnos e outra sessão.', '',
        'O índice de campos usa os seis campos explicitamente previstos no conjunto,',
        'não todas as afirmações em linguagem natural. Saída aceita combina schema e',
        'validação de evidências; não é uma taxa isolada de parsing. Latência inclui',
        'aplicação e rede. Uma repetição não estabelece superioridade geral.', '',
        'Tokens estimados têm cobertura 15/15 em cada condição. Os contadores reais',
        'do serviço e suas coberturas estão no JSON consolidado; não comparar médias',
        'com cobertura diferente como se fossem a mesma população.', '',
        'Runs de diagnóstico anteriores foram preservados em diretório separado. Não',
        'foram usados para substituir seletivamente falhas da coleta final.', '',
        '## Evidências', '',
        '- `evals/sprint3_results.json`: métricas, hashes, limitações e notas por caso.',
        '- `evals/revisao_operacional_ia.json`: decisões qualitativas e justificativas.',
        '- `evals/operacional_runs/20261016_final/`: perguntas, respostas, saídas rejeitadas e medições.',
        '- `evals/operacional_runs/20261016_controlado/`: diagnóstico anterior aos controles adicionais.', '',
        '## Cinco casos da Sprint 2 — LCEL v4', '',
        '| Caso | Pergunta | Resposta exibida | Avaliação IA | Justificativa |',
        '|---|---|---|---|---|']
    final = json.loads((args.runs/'lcel_v4.json').read_text(encoding='utf-8'))
    for r in final['registros'][:5]:
        n = revisao['condicoes']['lcel_v4'][r['caso']['id']]
        resposta = r['resultado']['resposta']
        texto = resposta['resposta'] if resposta else 'Falha: '+str(r['resultado']['erro'])
        def celula(s):
            return str(s).replace('|','/').replace('\n',' ')
        classe = {0:'Inadequada',1:'Parcialmente adequada',2:'Adequada'}[n['nota']]
        linhas.append('| '+' | '.join(map(celula,[r['caso']['id'],r['caso']['pergunta'],texto,classe,n['justificativa']]))+' |')
    (ROOT/'docs/comparativo_operacional.md').write_text('\n'.join(linhas)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
