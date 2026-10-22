"""Diagnóstico redigido de capacidades do endpoint, sem copiar corpo de erro."""
import httpx
import json
from src.rag.config import carregar_rag_config


def main():
    cfg = carregar_rag_config()
    for model in ['gpt-oss:120b','gemma4:31b']:
        for formato in [True,False]:
            payload = {'model':model,'stream':False,'messages':[
                {'role':'system','content':'Responda apenas JSON com status ok.'},
                {'role':'user','content':'Confirme.'}],
                'options':{'temperature':0,'top_p':0.9,'num_predict':256}}
            if formato:
                payload['format']='json'
            with httpx.Client(timeout=60,headers={'Authorization':'Bearer '+cfg.api_key}) as c:
                r=c.post(cfg.base_url+'/api/chat',json=payload)
            data=r.json()
            # Flags conhecidas para investigação sem expor o corpo.
            err=str(data.get('error','')).lower()
            print(model,'format_json',formato,'HTTP',r.status_code,
                  'flags',[w for w in ['format','json','unsupported','think','schema'] if w in err],
                  'conteudo',bool(data.get('message',{}).get('content')))
    from src.rag.service import ServicoRAG
    bot=ServicoRAG(carregar_rag_config(modelo='gemma4:31b'))
    contextos=[{'texto':d.page_content,'metadata':d.metadata,'distancia':dist}
               for d,dist in bot.retriever.buscar('Qual é a tarifa simulada ARM?')]
    m=bot.chain.invoke({'pergunta':'Qual é a tarifa simulada ARM?','historico':[],
                        'contexto':json.dumps(contextos,ensure_ascii=False)})
    texto=str(m.content).strip()
    print('resposta_complexa','comprimento',len(texto),'fence',texto.startswith('```'),
          'inicio_objeto',texto.startswith('{'),'fim_objeto',texto.endswith('}'),
          'tokens',m.usage_metadata)


if __name__ == '__main__':
    main()
