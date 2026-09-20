"""Cadeia LCEL com saída validada antes da gravação automática do histórico."""
from src.modelos import FalhaModelo, Geracao, SaidaInvalida
from src.schemas.consulta_recarga import ConsultaRecarga
from src.guardrails.output_validator import validar_saida, RespostaNaoConfiavel


def construir_chain(llm):
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import PydanticOutputParser
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{sistema}"), MessagesPlaceholder("historico"),
        ("human", "{pergunta}"),
    ])
    parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)
    return prompt | llm | parser


class ClienteLCEL:
    def __init__(self, config):
        try:
            from langchain_ollama import ChatOllama
            from src.chain.memoria_lcel import MemoriaLCEL
            from langchain_core.runnables import RunnableLambda, RunnablePassthrough
            from langchain_core.runnables.history import RunnableWithMessageHistory
            from langchain_core.messages import AIMessage
        except ImportError as exc:
            raise RuntimeError("Instale requirements-langchain.txt para usar --modo lcel.") from exc
        client_kwargs = {"timeout": config.timeout}
        if config.api_key:
            client_kwargs["headers"] = {"Authorization": "Bearer " + config.api_key}
        from src.chain.tokens import contar_mensagens

        class OllamaContado(ChatOllama):
            def get_num_tokens_from_messages(self, messages, tools=None):
                return contar_mensagens([
                    {"role": "user" if m.type == "human" else "assistant", "content": m.content}
                    for m in messages
                ]) if messages else 0

        self.llm = OllamaContado(
            model=config.modelo, base_url=config.base_url,
            temperature=config.temperature, top_p=config.top_p,
            num_predict=config.max_tokens, format="json", client_kwargs=client_kwargs,
        )
        self.memoria = MemoriaLCEL(self.llm, config.max_tokens_memoria)

        def preparar_saida(dados):
            resultado = validar_saida(dados["resultado"], dados["contexto"])
            return {"validada": resultado, "mensagem": AIMessage(content=resultado.model_dump_json())}

        self.chain = RunnableWithMessageHistory(
            RunnablePassthrough.assign(resultado=construir_chain(self.llm)) | RunnableLambda(preparar_saida),
            self.memoria.historico, input_messages_key="pergunta",
            history_messages_key="historico", output_messages_key="mensagem",
        )

    def gerar(self, sistema, historico, pergunta, contexto, *, session_id):
        from langchain_core.callbacks import BaseCallbackHandler
        from langchain_core.exceptions import OutputParserException

        class Captura(BaseCallbackHandler):
            mensagem = None
            def on_llm_end(self, response, **kwargs):
                self.mensagem = response.generations[0][0].message

        captura = Captura()
        memoria = self.memoria.historico(session_id)
        memoria.erro = None
        try:
            resultado = self.chain.invoke(
                {"sistema": sistema, "pergunta": pergunta, "contexto": contexto},
                config={"callbacks": [captura], "configurable": {"session_id": session_id}},
            )
            # Erros em listeners podem ser apenas registrados pelo LangChain.
            if memoria.erro is not None:
                raise memoria.erro
            resultado = resultado["validada"]
        except RespostaNaoConfiavel:
            raise
        except OutputParserException as exc:
            raise SaidaInvalida(str(captura.mensagem.content) if captura.mensagem else "") from exc
        except Exception as exc:
            raise FalhaModelo("Falha na chamada LCEL. Confira conexão, modelo e dependências.") from exc
        mensagem = captura.mensagem
        uso = (mensagem.usage_metadata or {}) if mensagem else {}
        texto = str(mensagem.content) if mensagem else resultado.model_dump_json()
        return Geracao(texto, uso.get("input_tokens"), uso.get("output_tokens"), resultado)
