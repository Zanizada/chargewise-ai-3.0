"""Somente documentos inventariados: paths e hashes conferidos antes da leitura."""
import hashlib
import json
import re
from pathlib import Path
from langchain_core.documents import Document


def inventario(root):
    root = Path(root).resolve()
    entries = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))['documents']
    ids = [e['id'] for e in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs duplicados no inventário.')
    return entries


def carregar_documentos(root):
    root = Path(root).resolve()
    documentos = []
    for entry in inventario(root):
        path = (root / entry['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Documento fora da base autorizada.')
        if not path.exists() and entry.get('optional'):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if entry.get('sha256') and entry['sha256'] != digest:
            raise ValueError(f"Hash divergente: {entry['id']}. Atualize o inventário após revisão.")
        meta = {k: entry[k] for k in ('id', 'title', 'source', 'revision', 'nature', 'category')}
        meta['document_id'] = meta.pop('id')
        meta.update(document_sha256=digest, source_path=entry['path'])
        if path.suffix.lower() == '.pdf':
            from langchain_community.document_loaders import PyMuPDFLoader
            pages = PyMuPDFLoader(str(path)).load()
            if not pages or not any(p.page_content.strip() for p in pages):
                raise ValueError(f"PDF sem texto extraível: {entry['id']}.")
            for page in pages:
                if page.page_content.strip():
                    documentos.append(Document(page_content=page.page_content,
                        metadata={**meta, 'page': int(page.metadata.get('page', 0)) + 1,
                                  'section': 'Página do documento'}))
        elif path.suffix.lower() in {'.md', '.txt'}:
            texto = path.read_text(encoding='utf-8')
            partes = re.split(r'(?m)^(?=## )', texto)
            for parte in partes:
                if parte.strip():
                    secao = parte.splitlines()[0].lstrip('# ').strip()
                    documentos.append(Document(page_content=parte.strip(),
                        metadata={**meta, 'page': 0, 'section': secao}))
        else:
            raise ValueError('Formato documental não suportado.')
    if not documentos:
        raise ValueError('Base de conhecimento vazia.')
    return documentos
