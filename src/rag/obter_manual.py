"""Baixa manual oficial somente para leitura local, nunca para distribuição pública."""
from pathlib import Path
from urllib.request import urlopen
from src.config import RAIZ

URL = 'https://en.goodwe.com/Ftp/EN/Downloads/User%20Manual/GW_HCA%20Series_User%20Manual-EN.pdf'


def main():
    destino = RAIZ / 'data/knowledge_base/local/goodwe_hca_manual.pdf'
    if destino.exists():
        print('Cópia local já existe; não sobrescrita.')
        return
    with urlopen(URL, timeout=60) as response:
        content = response.read(20_000_001)
    if not content.startswith(b'%PDF') or len(content) > 20_000_000:
        raise ValueError('Download não corresponde a PDF permitido.')
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(content)
    print('Manual salvo em local/ (ignorado pelo Git). Não distribuir sem autorização.')


if __name__ == '__main__':
    main()
