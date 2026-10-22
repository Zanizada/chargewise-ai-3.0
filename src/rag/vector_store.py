"""Coleções por fingerprint: índice novo só se torna ativo após ingestão completa."""
from hashlib import sha256
import json
from pathlib import Path
from chromadb.config import Settings
from langchain_chroma import Chroma
from src.rag.embeddings import criar_embeddings


def abrir_store(config, collection, embeddings=None):
    return Chroma(collection_name=collection, persist_directory=str(config.persist_dir),
        embedding_function=embeddings if embeddings is not None else criar_embeddings(config),
        client_settings=Settings(anonymized_telemetry=False),
        collection_metadata={'hnsw:space': 'cosine'})


def indexar(config, chunks, embeddings=None):
    descricao = {'embedding_model': config.embedding_model,
        'embedding_endpoint': config.embedding_url,
        'chunk_size': config.chunk_size, 'chunk_overlap': config.chunk_overlap,
        'chunks': [{'id': c.metadata['chunk_id'], 'hash': sha256(c.page_content.encode()).hexdigest()}
                   for c in chunks]}
    fingerprint = sha256(json.dumps(descricao, sort_keys=True).encode()).hexdigest()
    collection = 'chargewise_' + fingerprint[:20]
    config.persist_dir.mkdir(parents=True, exist_ok=True)
    store = abrir_store(config, collection, embeddings)
    # Upsert dos mesmos IDs: uma ingestão interrompida pode ser retomada.
    existentes = set(store.get()['ids'])
    pendentes = [c for c in chunks if c.metadata['chunk_id'] not in existentes]
    for start in range(0, len(pendentes), 24):
        lote = pendentes[start:start + 24]
        store.add_documents(lote, ids=[c.metadata['chunk_id'] for c in lote])
    if len(store.get()['ids']) != len(chunks):
        raise RuntimeError('Quantidade de chunks no índice não confere.')
    manifesto = {'fingerprint': fingerprint, 'collection': collection,
                 **descricao, 'count': len(chunks)}
    destino = config.persist_dir / 'active.json'
    temporario = destino.with_suffix('.tmp')
    temporario.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding='utf-8')
    temporario.replace(destino)
    return manifesto


def abrir_indice(config, embeddings=None):
    path = config.persist_dir / 'active.json'
    if not path.exists():
        raise RuntimeError('Índice ausente. Execute python -m src.rag.ingest primeiro.')
    meta = json.loads(path.read_text(encoding='utf-8'))
    for k, value in [('embedding_model', config.embedding_model),
                     ('embedding_endpoint', config.embedding_url),
                     ('chunk_size', config.chunk_size), ('chunk_overlap', config.chunk_overlap)]:
        if meta[k] != value:
            raise RuntimeError('Configuração diverge do índice. Refaça a ingestão explicitamente.')
    store = abrir_store(config, meta['collection'], embeddings)
    if len(store.get()['ids']) != meta['count']:
        raise RuntimeError('Índice incompleto. Refaça a ingestão.')
    return store, meta
