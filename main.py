"""Execute: python main.py --modo demo"""
import argparse

from src.app import Chatbot
from src.config import carregar_config
from src.contexto import carregar_contexto


def main():
    parser = argparse.ArgumentParser(description="ChargeWise AI — base incremental")
    parser.add_argument("--modo", choices=["demo", "manual", "lcel"])
    parser.add_argument("--prompt", choices=["v1", "v2"])
    parser.add_argument("--cenario", choices=["padrao", "sem_dados"], default="padrao")
    parser.add_argument("--pergunta", help="Executa uma pergunta e encerra")
    parser.add_argument("--json", action="store_true", help="Exibe a resposta estruturada")
    args = parser.parse_args()
    try:
        config = carregar_config(args.modo, args.prompt)
        contexto = carregar_contexto(args.cenario)
        bot = Chatbot(config)
        sessao = "demo-1"
        print(f"ChargeWise | modo={config.modo} | dados SIMULADOS")
        if config.modo == "demo":
            print("DEMO por regras: não usa IA e não comprova desempenho de modelos.")
        else:
            print(f"Modelo solicitado: {config.modelo}")
        print("Comandos: /sair, /limpar, /sessao NOME, /historico")
        while True:
            pergunta = args.pergunta if args.pergunta is not None else input(f"[{sessao}] Você: ")
            if pergunta == "/sair":
                return 0
            if pergunta == "/limpar":
                bot.memoria.limpar(sessao)
                print("Sessão limpa.")
            elif pergunta.startswith("/sessao "):
                nome = pergunta[len("/sessao "):].strip()
                if not nome or len(nome) > 80:
                    print("Use um identificador de 1 a 80 caracteres.")
                else:
                    sessao = nome
                    print(f"Sessão selecionada: {sessao}")
            elif pergunta == "/historico":
                for mensagem in bot.memoria.obter(sessao):
                    print(mensagem["role"] + ": " + mensagem["content"])
            else:
                try:
                    resultado = bot.responder(pergunta, sessao, contexto)
                    if not resultado.sucesso:
                        print("Falha: " + resultado.erro)
                        if args.pergunta is not None:
                            return 1
                    else:
                        print(resultado.resposta.model_dump_json(indent=2) if args.json
                              else "ChargeWise: " + resultado.resposta.resposta)
                except ValueError as exc:
                    print(str(exc))
                    if args.pergunta is not None:
                        return 1
            if args.pergunta is not None:
                return 0
    except (ValueError, RuntimeError, OSError) as exc:
        print("Não foi possível iniciar: " + str(exc))
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nAté mais!")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
