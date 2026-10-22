"""Scanner redigido de árvore e blobs históricos. Nunca imprime valores."""
import json
from pathlib import Path
import re
import subprocess
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]


def main():
    secrets=[v.encode() for k,v in dotenv_values(ROOT/'.env').items()
             if ('KEY' in k or 'TOKEN' in k) and v and len(v)>=16]
    pattern=re.compile(rb'(?:sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|'
        rb'(?:API_KEY|api_key)[\s"\x27:=]+([A-Za-z0-9_-]{32,}))')
    encontrados=[]
    def verificar(data,local):
        if any(s in data for s in secrets) or pattern.search(data):
            encontrados.append(local)
    files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    for name in files:
        p=ROOT/name
        if p.is_file() and p.name!='.env':
            verificar(p.read_bytes(),name)
    objects=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=ROOT,text=True).splitlines()
    total=0
    for row in objects:
        fields=row.split(' ',1)
        if len(fields)!=2:
            continue
        oid,name=fields
        tipo=subprocess.check_output(['git','cat-file','-t',oid],cwd=ROOT,text=True).strip()
        if tipo=='blob':
            total+=1
            data=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
            verificar(data,oid[:12]+':'+name)
    result={'metodo':'chaves atuais por igualdade e padrões de chave privada/token/atribuição',
        'arquivos_arvore':len(files),'blobs_historicos':total,
        'ocorrencias_redigidas':encontrados,
        'limites':'Não detecta todo segredo possível. Nenhum valor foi divulgado. Revisão humana antes de publicar.'}
    (ROOT/'docs/verificacao_segredos.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return int(bool(encontrados))


if __name__=='__main__':
    raise SystemExit(main())
