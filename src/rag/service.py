"""Serviço único para interface, CLI e avaliações. Memória por instância/sessão."""
import json
import re
from time import perf_counter
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from pydantic import ValidationError
from src.guardrails.moderation import verificar_entrada
from src.guardrails.scope_validator import normalizar
from src.guardrails.rag_validator import documento_suspeito, validar_rag
from src.schemas.resposta_rag import SaidaRAG, RespostaRAG
from src.rag.prompt_rag import carregar_prompt, construir_prompt
from src.rag.retriever import Retriever


class ServicoRAG:
    def __init__(self, config, retriever=None, llm=None):
        self.config = config
        self.retriever = retriever if retriever is not None else Retriever(config)
        self.prompt_texto, self.prompt_hash = carregar_prompt(config.prompt)
        self.sessoes = {}
        if llm is None:
            kwargs = {'timeout': config.timeout}
            if config.api_key:
                kwargs['headers'] = {'Authorization': 'Bearer ' + config.api_key}
            llm = ChatOllama(model=config.modelo, base_url=config.base_url, temperature=config.temperature,
                top_p=config.top_p, num_predict=config.max_tokens, format='json', client_kwargs=kwargs)
        self.chain = construir_prompt(self.prompt_texto) | llm

    def limpar(self, session_id):
        self.sessoes.pop(session_id, None)

    def responder(self, pergunta, session_id):
        inicio = perf_counter()
        if not pergunta.strip() or len(pergunta) > 2000 or not session_id.strip() or len(session_id) > 80:
            raise ValueError('Pergunta deve ter 1–2000 caracteres; sessão, 1–80.')
        pergunta = pergunta.strip()
        base = dict(modelo=self.config.modelo, prompt=self.config.prompt, prompt_sha256=self.prompt_hash)
        contextos, excluidos = [], 0

        def resultado(status, texto, **kwargs):
            return RespostaRAG(status=status, resposta=texto, latencia_segundos=perf_counter() - inicio,
                contextos=contextos, documentos_excluidos=excluidos, **base, **kwargs)

        bloqueio = verificar_entrada(pergunta)
        if bloqueio:
            return resultado('recusado', bloqueio.resposta)
        if re.search(r'\b(?:futebol|campeonato|poema|horoscopo|receita culinaria)\b', normalizar(pergunta)):
            return resultado('recusado', 'Esse pedido está fora do contexto de recarga da base.')
        try:
            historico = self.sessoes.get(session_id, [])
            # Só perguntas anteriores entram na busca; respostas não são fonte factual.
            consulta = pergunta
            if historico and any(p in pergunta.lower() for p in ('ele ', 'esse ', 'este ', 'e qual', 'e o ', 'e a ')):
                consulta = historico[-2].content + '\n' + pergunta
            docs, total = [], 0
            for doc, distancia in self.retriever.buscar(consulta):
                if documento_suspeito(doc.page_content):
                    excluidos += 1
                    continue
                if total + len(doc.page_content) > self.config.max_context_chars:
                    continue
                total += len(doc.page_content)
                docs.append(doc)
                contextos.append({'texto': doc.page_content, 'metadata': doc.metadata, 'distancia': distancia})
            if not docs:
                return resultado('dados_insuficientes', 'Não há fonte suficiente na base para responder à pergunta.')
            mensagem = self.chain.invoke({'pergunta': pergunta, 'historico': historico,
                'contexto': json.dumps(contextos, ensure_ascii=False)})
            bruto = str(mensagem.content).strip()
            # Alguns endpoints cloud ignoram format=json e cercam JSON com Markdown.
            # Aceitar só cerca completa; nunca tentar reparar JSON truncado ou extrair
            # objetos de prosa arbitrária, que esconderia falhas de geração.
            cerca = re.fullmatch(r'```(?:json)?\s*(.*?)\s*```', bruto, flags=re.S | re.I)
            if cerca:
                bruto = cerca.group(1)
            saida = SaidaRAG.model_validate_json(bruto)
            textos, citacoes = validar_rag(saida, docs)
            uso = mensagem.usage_metadata or {}
            if saida.status != 'respondido':
                texto = ('Esse pedido está fora do contexto de recarga da base.' if saida.status == 'recusado'
                         else 'Não há fonte suficiente na base para responder à pergunta.')
            else:
                texto = '\n\n'.join(textos)
            resposta = resultado(saida.status, texto, citacoes=citacoes,
                tokens_entrada=uso.get('input_tokens'), tokens_saida=uso.get('output_tokens'))
            if saida.status == 'respondido':
                self.sessoes[session_id] = (historico + [HumanMessage(content=pergunta),
                    AIMessage(content=texto)])[-2 * self.config.max_history_turns:]
            return resposta
        except Exception as exc:
            # Não expor mensagens do endpoint/modelo, que podem conter credenciais/dados.
            codigo = type(exc).__name__
            if isinstance(exc, ValidationError):
                primeiro = exc.errors(include_input=False, include_context=False)[0]
                permitidos = {'status','afirmacoes','texto','referencias','chunk_id','trecho'}
                local = [str(p) if isinstance(p,int) or p in permitidos else 'campo_desconhecido'
                         for p in primeiro['loc']]
                codigo += ':' + str(primeiro['type']) + ':' + '.'.join(local)
            return resultado('erro', 'Não foi possível confirmar a resposta. Confira o índice, o modelo e a conexão.',
                             erro_codigo=codigo)
