"""python -m src.rag.cli --pergunta 'Qual é a tarifa simulada?'"""
import argparse
from src.rag.config import carregar_rag_config
from src.rag.service import ServicoRAG


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pergunta', required=True)
    p.add_argument('--prompt', choices=['v1', 'v2'], default='v2')
    args = p.parse_args()
    bot = ServicoRAG(carregar_rag_config(prompt=args.prompt))
    resposta = bot.responder(args.pergunta, 'cli')
    print(resposta.model_dump_json(indent=2))
    return int(resposta.status == 'erro')


if __name__ == '__main__':
    raise SystemExit(main())
