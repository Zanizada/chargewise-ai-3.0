"""Ponto de partida LCEL funcional; a memória ainda é gerenciada pelo app."""
from src.modelos import FalhaModelo, Geracao, SaidaInvalida
from src.schemas.consulta_recarga import ConsultaRecarga


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
        except ImportError as exc:
            raise RuntimeError("Instale requirements-langchain.txt para usar --modo lcel.") from exc
        client_kwargs = {"timeout": config.timeout}
        if config.api_key:
            client_kwargs["headers"] = {"Authorization": "Bearer " + config.api_key}
        self.llm = ChatOllama(
            model=config.modelo, base_url=config.base_url,
            temperature=config.temperature, top_p=config.top_p,
            num_predict=config.max_tokens, format="json", client_kwargs=client_kwargs,
        )
        self.chain = construir_chain(self.llm)

    def gerar(self, sistema, historico, pergunta, contexto):
        from langchain_core.callbacks import BaseCallbackHandler
        from langchain_core.exceptions import OutputParserException

        class Captura(BaseCallbackHandler):
            mensagem = None
            def on_llm_end(self, response, **kwargs):
                self.mensagem = response.generations[0][0].message

        captura = Captura()
        try:
            resultado = self.chain.invoke(
                {"sistema": sistema, "historico": [(m["role"], m["content"]) for m in historico],
                 "pergunta": pergunta}, config={"callbacks": [captura]},
            )
        except OutputParserException as exc:
            raise SaidaInvalida(str(captura.mensagem.content) if captura.mensagem else "") from exc
        except Exception as exc:
            raise FalhaModelo("Falha na chamada LCEL. Confira conexão, modelo e dependências.") from exc
        mensagem = captura.mensagem
        uso = (mensagem.usage_metadata or {}) if mensagem else {}
        texto = str(mensagem.content) if mensagem else resultado.model_dump_json()
        return Geracao(texto, uso.get("input_tokens"), uso.get("output_tokens"), resultado)

# TODO S3-02: envolver a chain com RunnableWithMessageHistory e conectar memória limitada.
# Hoje o histórico é passado em MessagesPlaceholder e salvo manualmente pelo app.
