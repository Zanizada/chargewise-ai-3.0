"""Coleta inicial de evidências; qualidade humana continua pendente."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform

from src.app import Chatbot
from src.config import RAIZ, carregar_config
from src.contexto import carregar_contexto


def conferir_campos(resultado, esperado):
    if not resultado.sucesso:
        return False
    dados = resultado.resposta.model_dump()
    ok = dados["status"] == esperado["status"]
    ok = ok and all(dados.get(campo) == valor for campo, valor in esperado["campos"].items())
    if esperado["trecho"]:
        ok = ok and esperado["trecho"].casefold() in dados["resposta"].casefold()
    return ok


def main():
    parser = argparse.ArgumentParser(description="Avaliação inicial do ChargeWise")
    parser.add_argument("--modo", choices=["demo", "manual", "lcel"], default="demo")
    parser.add_argument("--prompt", choices=["v1", "v2"], default="v2")
    parser.add_argument("--arquivo", type=Path)
    args = parser.parse_args()
    config = carregar_config(args.modo, args.prompt)
    agora = datetime.now(timezone.utc)
    nome = f"resultados_{args.modo}_{agora.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    destino = args.arquivo or RAIZ / "evals" / nome
    if args.modo == "demo" and destino.name == "sprint3_results.json":
        parser.error("Resultados de demonstração devem manter nome de demo; não são eval de IA.")
    casos_bytes = (RAIZ / "evals/casos.json").read_bytes()
    casos = json.loads(casos_bytes)
    bot = Chatbot(config)
    registros = []
    for caso in casos:
        contexto = carregar_contexto(caso["cenario"])
        resultado = bot.responder(caso["pergunta"], caso["grupo"] or caso["id"], contexto)
        registro = {
            "caso": caso, "resultado": resultado.para_dict(),
            "checagem_campos_basica": conferir_campos(resultado, caso["esperado"]),
            "nota_qualidade_humana": None, "justificativa_humana": None,
            "hash_contexto": sha256(json.dumps(contexto, sort_keys=True).encode()).hexdigest(),
        }
        registros.append(registro)
        print(caso["id"], "checagem OK" if registro["checagem_campos_basica"] else "revisar")
    versoes = {}
    for pacote in ["pydantic", "python-dotenv", "langchain-core", "langchain-ollama", "tiktoken"]:
        try:
            versoes[pacote] = version(pacote)
        except Exception:
            versoes[pacote] = None
    dados = {
        "origem_base": "Criada agora; Sprint 2 não implementada pelo grupo.",
        "tipo_execucao": "demo_sem_ia" if args.modo == "demo" else "chamada_modelo",
        "data_utc": agora.isoformat(), "modo": args.modo,
        "modelo_solicitado": None if args.modo == "demo" else config.modelo,
        "prompt": args.prompt, "python": platform.python_version(), "dependencias": versoes,
        "parametros": {"temperature":config.temperature,"top_p":config.top_p,
                       "max_tokens":config.max_tokens,"ollama_num_predict":config.max_tokens,
                       "max_turnos":config.max_turnos,"timeout":config.timeout},
        "metodo_estimativa_tokens": "tiktoken cl100k_base sobre mensagens JSON" if config.contar_tokens else None,
        "hash_casos":sha256(casos_bytes).hexdigest(),
        "limites": "Checagens básicas não representam nota de qualidade nem segurança completa. Não houve retries automáticos.",
        "resumo": {"total":len(registros),
                   "falhas_execucao":sum(not r["resultado"]["sucesso"] for r in registros),
                   "checagens_campos_ok":sum(r["checagem_campos_basica"] for r in registros)},
        "registros":registros,
    }
    destino.parent.mkdir(parents=True,exist_ok=True)
    # Não sobrescreve um experimento anterior acidentalmente.
    with destino.open("x",encoding="utf-8") as arquivo:
        json.dump(dados,arquivo,ensure_ascii=False,indent=2)
    print("Arquivo:",destino.resolve())
    print("A avaliação qualitativa e as métricas agregadas do relatório ainda precisam ser concluídas.")
    return 0 if all(r["checagem_campos_basica"] for r in registros) else 1


if __name__ == "__main__":
    raise SystemExit(main())

# TODO S3-06: adicionar repetições, comparações e métricas com denominadores explícitos.
# TODO S3-06: nota de qualidade deve ser avaliada, não deduzida só pela presença de palavras.
