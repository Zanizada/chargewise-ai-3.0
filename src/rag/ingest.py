"""python -m src.rag.ingest: ingestão explícita, nunca acionada pela interface."""
import json
from src.rag.config import carregar_rag_config
from src.rag.loader import carregar_documentos
from src.rag.chunking import dividir_documentos
from src.rag.vector_store import indexar


def main():
    config = carregar_rag_config()
    try:
        chunks = dividir_documentos(carregar_documentos(config.knowledge_dir), config)
        meta = indexar(config, chunks)
        print(json.dumps({'collection': meta['collection'], 'count': meta['count'],
                          'fingerprint': meta['fingerprint']}, indent=2))
    except Exception:
        raise SystemExit('Ingestão falhou. Confira fontes, versões e endpoint de embeddings. Nenhuma credencial foi exibida.')


if __name__ == '__main__':
    main()
