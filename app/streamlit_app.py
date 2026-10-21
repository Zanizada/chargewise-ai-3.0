"""Interface: histórico/bots por navegador; nenhuma chave é enviada ao frontend."""
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from src.rag.config import carregar_rag_config
from src.rag.service import ServicoRAG
from src.app import Chatbot
from src.config import carregar_config
from src.contexto import carregar_contexto

st.set_page_config(page_title='ChargeWise AI', page_icon='⚡', layout='centered')
st.title('⚡ ChargeWise AI')
st.caption('GoodWe EV Challenge · Sprint 04 · projeto acadêmico')
trilha = st.sidebar.radio('Consulta', ['Documentos de recarga', 'Operação simulada'])
st.sidebar.caption('Regimento, FAQ e tarifas são exemplos acadêmicos. Não há controle de equipamentos.')
if 'session_id' not in st.session_state:
    st.session_state.session_id = uuid4().hex
    st.session_state.conversas = {}
if st.sidebar.button('Limpar conversa'):
    for nome in ('rag', 'operacional'):
        bot = st.session_state.get(nome)
        if bot:
            if nome == 'rag':
                bot.limpar(st.session_state.session_id)
            else:
                bot.memoria.limpar(st.session_state.session_id)
    st.session_state.conversas = {}
    st.rerun()


def exibir_fontes(citacoes):
    if not citacoes:
        st.caption('Sem fonte documental para esta resposta.')
    for i, c in enumerate(citacoes, 1):
        local = f"página {c['pagina']}" if c['pagina'] else c['secao']
        with st.expander(f"[{i}] {c['titulo']} · {local}"):
            st.text(c['trecho'])
            st.caption(f"Natureza: {c['natureza']}")
            # Exibir origem como texto: não executar HTML nem links fornecidos pelo LLM.
            st.text(c['origem'])


conversa = st.session_state.conversas.setdefault(trilha, [])
for mensagem in conversa:
    with st.chat_message(mensagem['role']):
        st.text(mensagem['content'])
        if mensagem['role'] == 'assistant' and trilha == 'Documentos de recarga':
            exibir_fontes(mensagem.get('citacoes', []))

pergunta = st.chat_input('Pergunte sobre a base ou os registros simulados', max_chars=2000)
if pergunta:
    conversa.append({'role': 'user', 'content': pergunta})
    with st.chat_message('user'):
        st.text(pergunta)
    with st.chat_message('assistant'), st.spinner('Consultando as fontes…'):
        try:
            if trilha == 'Documentos de recarga':
                if 'rag' not in st.session_state:
                    st.session_state.rag = ServicoRAG(carregar_rag_config())
                resultado = st.session_state.rag.responder(pergunta, st.session_state.session_id)
                texto = resultado.resposta
                fontes = [c.model_dump() for c in resultado.citacoes]
                st.text(texto)
                exibir_fontes(fontes)
                conversa.append({'role': 'assistant', 'content': texto, 'citacoes': fontes})
            else:
                st.info('Dados fictícios. Nenhuma reserva, cobrança ou ação em equipamento é realizada.')
                if 'operacional' not in st.session_state:
                    st.session_state.operacional = Chatbot(carregar_config())
                resultado = st.session_state.operacional.responder(pergunta,
                    st.session_state.session_id, carregar_contexto())
                texto = resultado.resposta.resposta if resultado.sucesso else resultado.erro
                st.text(texto)
                if resultado.sucesso:
                    st.caption('Fontes simuladas: ' + ', '.join(resultado.resposta.fontes))
                conversa.append({'role': 'assistant', 'content': texto})
        except Exception:
            texto = 'Não foi possível iniciar a consulta. Confira a configuração e faça a ingestão da base antes de usar o RAG.'
            st.error(texto)
            conversa.append({'role': 'assistant', 'content': texto})
