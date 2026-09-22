"""Dois provedores simples: simulação determinística e chamada manual ao Ollama."""
from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.guardrails.scope_validator import identificar_intencao, normalizar
from src.schemas.consulta_recarga import ConsultaRecarga


class FalhaModelo(RuntimeError):
    pass


class SaidaInvalida(FalhaModelo):
    def __init__(self, texto):
        super().__init__("O modelo retornou uma saída incompatível com o schema.")
        self.texto = texto


@dataclass
class Geracao:
    texto: str
    tokens_entrada: int | None = None
    tokens_saida: int | None = None
    validada: ConsultaRecarga | None = None


def mensagens_chat(sistema, historico, pergunta):
    return [{"role": "system", "content": sistema}, *historico,
            {"role": "user", "content": pergunta}]


class ClienteOllama:
    def __init__(self, config):
        self.config = config

    def gerar(self, sistema, historico, pergunta, contexto):
        cfg = self.config
        payload = {
            "model": cfg.modelo, "stream": False, "format": "json",
            "messages": mensagens_chat(sistema, historico, pergunta),
            "options": {"temperature": cfg.temperature, "top_p": cfg.top_p,
                        "num_predict": cfg.max_tokens},
        }
        headers = {"Content-Type": "application/json"}
        if cfg.api_key:
            headers["Authorization"] = "Bearer " + cfg.api_key
        req = Request(cfg.base_url + "/api/chat",
                      data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urlopen(req, timeout=cfg.timeout) as resposta:
                dados = json.load(resposta)
            if not isinstance(dados, dict):
                raise FalhaModelo("Resposta do serviço deve ser um objeto JSON.")
            if dados.get("error"):
                raise FalhaModelo("O serviço retornou erro. Confira modelo e configuração.")
            texto = dados["message"]["content"]
            if not isinstance(texto, str) or not texto.strip():
                raise FalhaModelo("O serviço retornou conteúdo vazio.")
            return Geracao(texto, dados.get("prompt_eval_count"), dados.get("eval_count"))
        except HTTPError as exc:
            # Não reproduzir corpo da resposta: pode conter dados/credenciais do serviço.
            raise FalhaModelo(f"Ollama respondeu HTTP {exc.code}. Confira acesso e nome do modelo.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise FalhaModelo("Sem conexão com Ollama ou tempo de resposta excedido.") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise FalhaModelo("Resposta do serviço Ollama em formato inesperado.") from exc


class ClienteDemo:
    """Não usa IA. Só responde a exemplos predefinidos com os dados da fixture."""
    def gerar(self, sistema, historico, pergunta, contexto):
        texto = normalizar(pergunta)
        intencao = identificar_intencao(pergunta)
        resposta = ConsultaRecarga(intencao=intencao, status="dados_insuficientes",
                                   resposta="Não há dados suficientes no cenário. Informe a consulta de recarga que deseja realizar.")
        if "repita minha primeira pergunta" in texto:
            perguntas = [m["content"] for m in historico if m["role"] == "user"]
            resposta.resposta = ("Primeira pergunta ainda retida: " + perguntas[0]
                                 if perguntas else "Não há perguntas anteriores nesta sessão.")
            resposta.status = "respondido" if perguntas else "dados_insuficientes"
        elif intencao == "disponibilidade" and contexto.get("carregadores"):
            livres = [c["id"] for c in contexto["carregadores"] if c["estado"] == "disponivel"]
            resposta.resposta = "Disponíveis no cenário simulado: " + (", ".join(livres) or "nenhum") + "."
            resposta.carregador_id = livres[0] if len(livres) == 1 else None
            resposta.status, resposta.fontes = "respondido", ["carregadores"]
        elif intencao == "consumo" and contexto.get("consumo_mensal"):
            dado = contexto["consumo_mensal"]
            resposta.energia_kwh, resposta.valor_brl = dado["energia_kwh"], dado["valor_brl"]
            resposta.resposta = f"No período simulado: {dado['energia_kwh']} kWh e R$ {dado['valor_brl']:.2f}."
            resposta.status, resposta.fontes = "respondido", ["consumo_mensal"]
        elif intencao in {"cobranca", "sessao"} and contexto.get("ultima_sessao"):
            dado = contexto["ultima_sessao"]
            resposta.resposta = f"Sessão simulada {dado['id']}, {dado['inicio']}: {dado['energia_kwh']} kWh e R$ {dado['valor_brl']:.2f}."
            resposta.energia_kwh, resposta.valor_brl = dado["energia_kwh"], dado["valor_brl"]
            resposta.carregador_id = dado["carregador_id"]
            resposta.status, resposta.fontes = "respondido", ["ultima_sessao"]
        elif intencao == "agendamento":
            resposta.resposta = "Esta base não efetiva reservas e não possui agenda disponível. Consulte a administração do condomínio."
        elif intencao == "suporte":
            resposta.resposta = "Procure a administração do condomínio ou suporte técnico responsável. Não realize intervenções elétricas."
            resposta.status, resposta.encaminhamento = "encaminhar", "administração ou suporte técnico"
        elif any(p in texto for p in ["poema", "painel do carro", "zeladoria", "futebol"]):
            resposta.intencao, resposta.status = "fora_escopo", "recusado"
            resposta.resposta = "Atendo consultas sobre recarga compartilhada GoodWe. Esse pedido está fora do escopo."
        return Geracao(resposta.model_dump_json())
