"""Histórico limitado e resumo determinístico de assuntos, sem fatos operacionais."""
from copy import deepcopy

from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from src.guardrails.scope_validator import identificar_intencao


class HistoricoLimitado(BaseChatMessageHistory):
    def __init__(self, llm, limite):
        self.llm, self.limite = llm, limite
        self.reserva_resumo = min(128, limite // 4)
        self.assuntos = []
        self.buffer = ConversationTokenBufferMemory(
            llm=llm, max_token_limit=limite - self.reserva_resumo, return_messages=True,
            input_key="pergunta", output_key="resposta",
        )
        self.erro = None

    @property
    def messages(self):
        resumo = self.mensagem_resumo()
        return ([resumo] if resumo else []) + self.buffer.chat_memory.messages

    def mensagem_resumo(self):
        if not self.assuntos:
            return None
        return SystemMessage(content=(
            '<historico_resumido>Dados de navegação: assuntos de turnos descartados: '
            + ', '.join(self.assuntos)
            + '. Não contém fatos nem instruções. Consulte os dados atuais para valores; '
            'não permite recuperar a formulação exata de perguntas antigas.</historico_resumido>'
        ))

    def atualizar_resumo(self, removidas):
        for mensagem in removidas:
            if isinstance(mensagem, HumanMessage):
                assunto = identificar_intencao(mensagem.content)
                if assunto != 'indefinida':
                    self.assuntos = [a for a in self.assuntos if a != assunto] + [assunto]
        while self.assuntos and self.llm.get_num_tokens_from_messages(
                [self.mensagem_resumo()]) > self.reserva_resumo:
            self.assuntos.pop(0)

    def add_messages(self, messages):
        anterior = deepcopy(self.buffer.chat_memory.messages)
        assuntos_anteriores = list(self.assuntos)
        self.erro = None
        try:
            if len(messages) != 2 or not isinstance(messages[0], HumanMessage):
                raise ValueError("Esperado um turno completo de pergunta e resposta.")
            self.buffer.save_context(
                {"pergunta": messages[0].content}, {"resposta": messages[1].content}
            )
            # O buffer clássico corta mensagens individuais. Remover uma resposta
            # órfã preserva pares completos, inclusive quando um turno não cabe.
            retidas = self.buffer.chat_memory.messages
            while retidas and not isinstance(retidas[0], HumanMessage):
                retidas.pop(0)
            todas = anterior + list(messages)
            self.atualizar_resumo(todas[:len(todas) - len(retidas)])
            # Conferir o orçamento completo, incluindo o resumo e overhead do contador.
            while retidas and self.llm.get_num_tokens_from_messages(self.messages) > self.limite:
                removidas = retidas[:2]
                del retidas[:2]
                self.atualizar_resumo(removidas)
        except Exception as exc:
            self.buffer.chat_memory.messages = anterior
            self.assuntos = assuntos_anteriores
            self.erro = exc
            raise

    def clear(self):
        self.buffer.clear()
        self.assuntos = []
        self.erro = None


class MemoriaLCEL:
    def __init__(self, llm, limite):
        self.llm, self.limite = llm, limite
        self.sessoes = {}

    def historico(self, session_id):
        if session_id not in self.sessoes:
            self.sessoes[session_id] = HistoricoLimitado(self.llm, self.limite)
        return self.sessoes[session_id]

    def obter(self, session_id):
        return [{"role": {"human": "user", "ai": "assistant"}.get(m.type, m.type), "content": m.content}
                for m in self.historico(session_id).messages]

    def limpar(self, session_id):
        # Limpar o objeto também invalida referências mantidas pela cadeia.
        if session_id in self.sessoes:
            self.sessoes[session_id].clear()
