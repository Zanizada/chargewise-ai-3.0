"""Copia apenas arquivos publicáveis e instala em ambiente/índice independentes."""
from datetime import datetime, timezone
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from src.rag.config import carregar_rag_config

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reusar', action='store_true',
        help='Sincroniza código final e revalida o ambiente independente já instalado.')
    args = parser.parse_args()
    cfg = carregar_rag_config()
    destino = ROOT/'tmp/reproducao_20261016'
    destino.mkdir(parents=True, exist_ok=args.reusar)
    arquivos = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],
        cwd=ROOT,text=True).splitlines()
    copiados = 0
    for nome in arquivos:
        origem = ROOT/nome
        if nome == '.env' or not origem.is_file():
            continue
        alvo = destino/nome
        alvo.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(origem,alvo)
        copiados += 1
    python = destino/'.venv/Scripts/python.exe'
    env = os.environ.copy()
    env.pop('PYTHONPATH',None)
    env.update({'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1',
        'RAG_BASE_URL':cfg.base_url,'RAG_MODEL':cfg.modelo,'RAG_API_KEY':cfg.api_key,
        'EMBEDDING_BASE_URL':cfg.embedding_url,'EMBEDDING_MODEL':cfg.embedding_model,
        'EMBEDDING_API_KEY':cfg.embedding_key,'RAG_PERSIST_DIR':str(destino/'data/chroma'),
        'ANONYMIZED_TELEMETRY':'False'})
    relatorio = ROOT/'docs/verificacao_instalacao_limpa.json'
    registros = (json.loads(relatorio.read_text(encoding='utf-8'))['etapas']
                 if args.reusar and relatorio.exists() else [])
    if args.reusar:
        registros.append({'etapa':'sincronizacao_codigo_final','exit_code':0})
    def executar(nome,cmd,timeout):
        print('INICIO',nome,flush=True)
        r = subprocess.run(cmd,cwd=destino,env=env,capture_output=True,text=True,
            encoding='utf-8',errors='replace',timeout=timeout)
        # Log local; nunca publica ambiente ou configuração com chaves.
        (destino/f'{nome}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        registros.append({'etapa':nome,'exit_code':r.returncode})
        print('FIM',nome,'exit_code',r.returncode,flush=True)
        salvar()
        if r.returncode:
            raise RuntimeError('Falha em '+nome+'; conferir log local redigido antes de publicar.')
    def salvar():
        (ROOT/'docs/verificacao_instalacao_limpa.json').write_text(json.dumps({
            'data_utc':datetime.now(timezone.utc).isoformat(),'arquivos_copiados':copiados,
            'env_copiado':False,'ambiente_novo':True,'indice_novo':True,
            'etapas':registros,'origem':'Snapshot público da árvore local, ainda não é clone publicado.',
            'limites':'Credenciais injetadas somente no processo. Ollama local já instalado. PDFs e vídeo não revisados.'},
            ensure_ascii=False,indent=2),encoding='utf-8')
    if not args.reusar:
        executar('venv',[sys._base_executable,'-m','venv',str(destino/'.venv')],120)
        executar('dependencias',[str(python),'-m','pip','install','--disable-pip-version-check','-r','requirements-sprint04-lock.txt'],900)
    executar('pip_check',[str(python),'-m','pip','check'],60)
    executar('testes_componentes',[str(python),'-m','unittest',
        'evals.verificar_componentes','evals.verificar_memoria_resumo',
        'evals.verificar_saida_operacional','evals.verificar_rag',
        'evals.verificar_interface','evals.verificar_comparacao'],120)
    executar('manual',[str(python),'-m','src.rag.obter_manual'],90)
    executar('ingestao',[str(python),'-m','src.rag.ingest'],180)
    executar('ingestao_reabertura',[str(python),'-m','src.rag.ingest'],180)
    executar('consultas_interface',[str(python),'-m','evals.verificar_instalacao_real'],240)
    prova = json.loads((destino/'tmp/prova_instalacao_real.json').read_text(encoding='utf-8'))
    salvar()
    path = ROOT/'docs/verificacao_instalacao_limpa.json'
    dados = json.loads(path.read_text(encoding='utf-8'))
    dados['prova'] = prova
    dados['resultado_final'] = 'aprovado'
    dados['historico_de_falhas'] = 'Etapas anteriores são preservadas; resultado final exige sucesso de todos os comandos da última validação.'
    publicado = json.loads((ROOT/'evals/scores/gpt-oss_120b_v2.json').read_text(encoding='utf-8'))
    dados['fingerprint_igual_scores_rag_publicados'] = prova['indice_fingerprint'] == publicado['indice_fingerprint']
    dados['codigo_sha256'] = {str(p.relative_to(destino)).replace('\\','/'):
        sha256(p.read_bytes()).hexdigest() for pasta in ['src','app']
        for p in (destino/pasta).rglob('*.py')}
    path.write_text(json.dumps(dados,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
