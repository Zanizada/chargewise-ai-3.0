"""Histórico manual: base de aprendizado, ainda NÃO é memória LangChain."""
from copy import deepcopy


class MemoriaSessoes:
    def __init__(self, max_turnos=6):
        if max_turnos < 1:
            raise ValueError("max_turnos deve ser positivo.")
        self.max_turnos = max_turnos
        self.sessoes = {}

    def obter(self, session_id):
        # Retorna cópia: uma chamada não deve modificar a memória acidentalmente.
        return deepcopy(self.sessoes.get(session_id, []))

    def salvar(self, session_id, pergunta, resposta_json):
        mensagens = self.sessoes.setdefault(session_id, [])
        mensagens.extend([
            {"role": "user", "content": pergunta},
            {"role": "assistant", "content": resposta_json},
        ])
        self.sessoes[session_id] = mensagens[-2 * self.max_turnos:]

    def limpar(self, session_id):
        self.sessoes.pop(session_id, None)

    # TODO S3-02: integrar RunnableWithMessageHistory + ConversationTokenBufferMemory.
    # TODO S3-02: trocar limite de turnos por orçamento de tokens e política de resumo.
    # Não salvar duas vezes ao adicionar a memória automática do LangChain.
