"""Chunking reproduzível em caracteres com IDs vinculados ao documento."""
from hashlib import sha256
from langchain_text_splitters import RecursiveCharacterTextSplitter


def dividir_documentos(documentos, config):
    splitter = RecursiveCharacterTextSplitter(chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap, separators=['\n\n', '\n', '. ', ' ', ''])
    chunks = splitter.split_documents(documentos)
    for i, chunk in enumerate(chunks):
        identidade = f"{chunk.metadata['document_id']}:{chunk.metadata['document_sha256']}:{chunk.metadata['page']}:{chunk.metadata['section']}:{i}:{chunk.page_content}"
        chunk.metadata['chunk_id'] = sha256(identidade.encode()).hexdigest()[:24]
    return chunks
