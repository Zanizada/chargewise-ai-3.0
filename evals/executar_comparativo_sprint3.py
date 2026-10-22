"""Experimento atual manual/LCEL e v1/v2; não reconstrói uma entrega histórica."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
from importlib.metadata import version
from src.app import Chatbot
from src.config import RAIZ, carregar_config
from src.contexto import carregar_contexto
from src.rag.config import carregar_rag_config
from evals.executar import conferir_campos


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def resumo(registros):
    chamadas = [r for r in registros if r['resultado']['origem'] != 'guardrail']
    def media(campo):
        valores = [r['resultado'][campo] for r in chamadas if r['resultado'][campo] is not None]
        return {'media': mean(valores) if valores else None, 'cobertura': len(valores), 'total': len(chamadas)}
    campos_total = sum(len(r['caso']['esperado']['campos']) for r in registros)
    campos_ok = sum(sum(r['resultado']['resposta'] is not None and
        r['resultado']['resposta'].get(k) == v for k, v in r['caso']['esperado']['campos'].items())
        for r in registros)
    return {'total': len(registros), 'turnos_com_modelo': len(chamadas),
        'falhas': sum(not r['resultado']['sucesso'] for r in registros),
        'checagens_ok': sum(r['checagem_campos_basica'] for r in registros),
        'schema_e_evidencias_validos': sum(r['resultado']['sucesso'] for r in chamadas),
        'campos_corretos': campos_ok, 'campos_total': campos_total,
        'latencia_todos_media': mean(r['resultado']['latencia_segundos'] for r in registros),
        'latencia_modelo': media('latencia_segundos'),
        'tokens_entrada_servico': media('tokens_entrada_servico'),
        'tokens_saida_servico': media('tokens_saida_servico'),
        'tokens_entrada_estimados': media('tokens_entrada_estimados')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--condicoes', nargs='+', default=['manual:v1','lcel:v1','lcel:v2','lcel:v4'])
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=False)
    rag = carregar_rag_config()
    if not rag.api_key and 'ollama.com' in rag.base_url:
        raise RuntimeError('Chave cloud não configurada no ambiente local.')
    casos_path = RAIZ/'evals/casos.json'
    casos = json.loads(casos_path.read_text(encoding='utf-8'))
    fontes = ['src/app.py', 'src/modelos.py', 'src/chain/builder.py',
              'src/chain/memoria_lcel.py', 'src/guardrails/output_validator.py',
              'src/schemas/consulta_recarga.py']
    codigo = {p: digest(RAIZ/p) for p in fontes}
    for condicao in args.condicoes:
        modo, prompt = condicao.split(':')
        cfg = replace(carregar_config(modo, prompt), base_url=rag.base_url,
            modelo=rag.modelo, api_key=rag.api_key, temperature=0, top_p=0.9,
            max_tokens=2048, timeout=45, contar_tokens=True,
            max_turnos=6, max_tokens_memoria=2048)
        bot = Chatbot(cfg)
        dados = {'tipo_execucao':'chamada_modelo', 'data_utc':datetime.now(timezone.utc).isoformat(),
            'origem_base':'Referência manual atual; não é prova de entrega histórica da Sprint 2.',
            'modo':modo, 'prompt':prompt, 'modelo':cfg.modelo,
            'hash_casos':digest(casos_path), 'hash_contextos':digest(RAIZ/'evals/contextos_simulados.json'),
            'prompt_sha256':digest(RAIZ/f'Prompts/system_prompt_{prompt}.md'),
            'codigo_sha256':codigo,
            'parametros':{'temperature':0,'top_p':0.9,'max_tokens':2048,'timeout':45,
                'memoria_manual_turnos':6,'memoria_lcel_tokens':2048,'reserva_resumo_max_tokens':128,
                'repeticoes':1,'retries':0},
            'dependencias':{p:version(p) for p in ['langchain-core','langchain-ollama','pydantic','tiktoken']},
            'limites':['Uma repetição; sem significância estatística.',
                'Manual e LCEL têm políticas de memória diferentes; medição do refactory completo.',
                'Validade de schema e evidências conjunta, não métrica isolada de parsing.',
                'Avaliação qualitativa assistida por IA deve ser revisada pela equipe.'],
            'registros':[]}
        destino = args.saida/f'{modo}_{prompt}.json'
        for caso in casos:
            resultado = bot.responder(caso['pergunta'], caso['grupo'] or caso['id'], carregar_contexto(caso['cenario']))
            dados['registros'].append({'caso':caso,'resultado':resultado.para_dict(),
                'checagem_campos_basica':conferir_campos(resultado,caso['esperado']),
                'nota_qualidade_humana':None,'justificativa_humana':None})
            dados['resumo'] = resumo(dados['registros'])
            destino.write_text(json.dumps(dados,ensure_ascii=False,indent=2),encoding='utf-8')
            print(modo,prompt,caso['id'],'OK' if dados['registros'][-1]['checagem_campos_basica'] else 'REVISAR',flush=True)
        print('CONCLUIDO',modo,prompt,json.dumps(dados['resumo']),flush=True)


if __name__ == '__main__':
    main()
