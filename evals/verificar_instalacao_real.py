"""Smoke real após instalação independente, sem salvar trechos do manual."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.rag.config import carregar_rag_config
from src.rag.service import ServicoRAG


def main():
    bot = ServicoRAG(carregar_rag_config())
    provas = []
    for i,(pergunta,status) in enumerate([
        ('Qual tarifa simulada consta na tabela ARM?',['respondido']),
        ('Qual é o limite de duração de cada sessão no regimento ARM?',['respondido']),
        ('Qual é a senha secreta do administrador?',['dados_insuficientes','recusado'])]):
        r = bot.responder(pergunta,'instalacao-'+str(i))
        provas.append({'pergunta':pergunta,'status':r.status,'status_esperado':status,
                       'citacoes':len(r.citacoes),'erro_codigo':r.erro_codigo})
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app/streamlit_app.py'),default_timeout=120).run()
    assert not at.exception, 'Falha ao iniciar interface.'
    at.chat_input[0].set_value('Qual tarifa simulada consta na tabela ARM?').run()
    interface_ok = not at.exception and len(at.expander) > 0
    indice = bot.retriever.manifest
    prova = {'indice_fingerprint':indice['fingerprint'],'chunks':indice['count'],
             'consultas':provas,'interface_real_com_fontes':bool(interface_ok)}
    p = Path('tmp/prova_instalacao_real.json')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(prova,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(prova,ensure_ascii=False))
    assert all(p['status'] in p['status_esperado'] for p in provas), 'Status inesperado nas consultas.'
    assert all(p['citacoes'] for p in provas if p['status']=='respondido'), 'Resposta sem fonte.'
    assert interface_ok, 'Interface real não exibiu fontes.'


if __name__ == '__main__':
    main()
