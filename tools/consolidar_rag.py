"""Publica somente scores/metadados; trechos de PDF protegido ficam no run local."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.config import RAIZ
from evals.comparar_rag import resumo, comparar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=Path, default=RAIZ/'evals/rag_runs/final')
    parser.add_argument('--scores', type=Path, default=RAIZ/'evals/scores')
    parser.add_argument('--relatorio', type=Path, default=RAIZ/'docs/resultados_rag')
    args = parser.parse_args()
    paths=sorted(args.runs.glob('*_avaliado.json'))
    if len(paths)<4:
        raise SystemExit('As quatro avaliações finais precisam terminar antes de consolidar.')
    destino=args.scores
    destino.mkdir(parents=True,exist_ok=True)
    runs={}
    tabelas=[]
    for path in paths:
        run=json.loads(path.read_text(encoding='utf-8'))
        key=(run['config']['modelo'],run['config']['prompt'])
        if key in runs:
            raise SystemExit('Há mais de um run para a mesma condição; selecione um experimento por diretório.')
        runs[key]=run
        summary=resumo(run)
        public={'modelo':key[0],'prompt':key[1],'config':run['config'],
            'data_coleta_utc':run.get('data_utc'),'repeticao':run.get('repeticao'),
            'run_sha256':sha256(path.read_bytes()).hexdigest(),
            'hash_casos':run['hash_casos'],'indice_fingerprint':run['indice']['fingerprint'],
            'prompt_sha256':run['prompt_sha256'],'pipeline_sha256':run.get('pipeline_sha256'),
            'avaliador':run.get('avaliador'),'resumo':summary,
            'por_caso':[{'id':r['caso']['id'],'grupo':r['caso']['grupo'],
                'status':r['resultado']['status'],'status_esperado':r['caso']['status'],
                'fontes':[{'document_id':c['document_id'],'pagina':c['pagina'],'secao':c['secao']}
                          for c in r['resultado']['citacoes']],
                'latencia_segundos':r['resultado']['latencia_segundos'],
                'tokens_entrada':r['resultado']['tokens_entrada'],
                'tokens_saida':r['resultado']['tokens_saida'],
                'documentos_excluidos':r['resultado']['documentos_excluidos'],
                'erro_codigo':r['resultado'].get('erro_codigo'),'revisao':r['revisao']}
                for r in run['registros']]}
        name=key[0].replace(':','_')+'_'+key[1]+'.json'
        (destino/name).write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
        tabelas.append({'modelo':key[0],'prompt':key[1],**summary})
    comparacoes=[]
    for model in sorted({key[0] for key in runs}):
        if (model,'v1') in runs and (model,'v2') in runs:
            comparacoes.append({'modelo':model,**comparar(runs[(model,'v1')],runs[(model,'v2')])})
    output={'metodo':'RAGAS 0.4.3; relevância zero por protocolo em falhas/abstenções respondíveis',
        'limites':'Uma repetição por condição; juiz GPT-OSS também é modelo avaliado. Não comprova significância estatística.',
        'experimentos':tabelas,'comparacoes':comparacoes}
    args.relatorio.parent.mkdir(parents=True, exist_ok=True)
    args.relatorio.with_suffix('.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Resultados RAG Sprint 04','',output['metodo'],'',output['limites'],'',
        '| Modelo | Prompt | Faithfulness (avaliados/13) | Answer relevancy (avaliados/13) | Status esperado /24 | Falhas |',
        '|---|---|---|---|---|---|']
    for row in tabelas:
        f,r=row['faithfulness'],row['answer_relevancy']
        def formatar(x):
            return f"{x['media']:.4f} ({x['avaliados']}/{x['total']})" if x['media'] is not None else 'N/A'
        lines.append(f"| {row['modelo']} | {row['prompt']} | {formatar(f)} | {formatar(r)} | {row['status_esperado']}/24 | {row['falhas']} |")
    lines+=['','## Comparações controladas','']
    for c in comparacoes:
        lines.append(f"- {c['modelo']}: deltas {c['deltas']}; ganho comprovado segundo o critério conservador: {c['ganho_comprovado']}.")
    lines+=['',f'Scores por caso: `{destino.as_posix()}`. Runs brutos locais: `{args.runs.as_posix()}`, ignorados pelo Git por conterem trechos de manual com restrição de reprodução pública. Reproduza com o downloader e protocolo. Não há notas humanas inventadas.']
    args.relatorio.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(output,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
