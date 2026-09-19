"""Histórico LCEL com orçamento de tokens e descarte de turnos antigos.

Não gera resumo: ao exceder o orçamento, descarta os turnos mais antigos.
Isso evita introduzir fatos sintetizados como se fossem dados operacionais.
"""
from copy import deepcopy

from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage


class HistoricoLimitado(BaseChatMessageHistory):
    def __init__(self, llm, limite):
        self.buffer = ConversationTokenBufferMemory(
            llm=llm, max_token_limit=limite, return_messages=True,
            input_key="pergunta", output_key="resposta",
        )
        self.erro = None

    @property
    def messages(self):
        return self.buffer.chat_memory.messages

    def add_messages(self, messages):
        anterior = deepcopy(self.messages)
        self.erro = None
        try:
            if len(messages) != 2 or not isinstance(messages[0], HumanMessage):
                raise ValueError("Esperado um turno completo de pergunta e resposta.")
            self.buffer.save_context(
                {"pergunta": messages[0].content}, {"resposta": messages[1].content}
            )
            # O buffer clássico corta mensagens individuais. Remover uma resposta
            # órfã preserva pares completos, inclusive quando um turno não cabe.
            while self.messages and not isinstance(self.messages[0], HumanMessage):
                self.messages.pop(0)
        except Exception as exc:
            self.buffer.chat_memory.messages = anterior
            self.erro = exc
            raise

    def clear(self):
        self.buffer.clear()
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
        return [{"role": "user" if m.type == "human" else "assistant", "content": m.content}
                for m in self.historico(session_id).messages]

    def limpar(self, session_id):
        # Limpar o objeto também invalida referências mantidas pela cadeia.
        if session_id in self.sessoes:
            self.sessoes[session_id].clear()
