"""Fixtures simuladas; não há integração com banco ou equipamentos reais."""
import json
from src.config import RAIZ


def carregar_contexto(cenario="padrao"):
    dados = json.loads((RAIZ / "evals/contextos_simulados.json").read_text(encoding="utf-8"))
    if cenario not in dados:
        raise ValueError("Cenário desconhecido. Use padrao ou sem_dados.")
    return dados[cenario]

# TODO S3-03: criar mais snapshots e selecionar contexto por consulta.
# session_id NÃO autentica usuários; a base usa somente um morador fictício.
