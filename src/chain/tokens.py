"""Contagem opcional: estimativa, não tokenizer oficial dos modelos Ollama."""
from functools import lru_cache
import json


@lru_cache(maxsize=1)
def encoding():
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except Exception as exc:
        raise RuntimeError(
            "Não foi possível carregar tiktoken/encoding. Instale as dependências "
            "opcionais e confira a conexão ou desative CONTAR_TOKENS."
        ) from exc


def contar_mensagens(mensagens):
    texto = json.dumps(mensagens, ensure_ascii=False)
    return len(encoding().encode(texto, disallowed_special=()))

# TODO S3-02: usar um contador consistente ao limitar a memória.
# A contagem acima inclui a serialização JSON; não é a contagem exata do serviço.
