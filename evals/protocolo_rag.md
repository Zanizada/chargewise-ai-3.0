# Protocolo Sprint 04

Congelar `rag_cases.json`, fontes e índice antes de coletar. Baseline v1 e iteração v2
usam mesmo modelo/corpus/parâmetros. Comparar dois modelos sob v1/v2 separadamente.
Rodar preferencialmente três repetições; uma repetição deve ter limite declarado.

`python -m evals.executar_rag --modelos gpt-oss:120b NOME_SEGUNDO_MODELO --prompts v1 v2`

Os JSONs guardam contextos, citações, tokens, tempo, parâmetros, hashes e slots de
revisão, nunca chaves. Falhas e recusas não são descartadas. Perguntas independentes
têm sessão própria; R23 compartilha sessão com R01, R24 tem outra sessão.
Fixtures adversariais substituem os trechos de busca somente no caso declarado.

Revisar sem conhecer o nome do modelo, se possível. Preencher `revisao` conforme
`rubrica_manual.md` ou gerar arquivo avaliado separado com RAGAS. Preservar run bruto.
`python -m evals.comparar_rag ANTES.json DEPOIS.json` exige mesmos dados/parâmetros.
Null não é nota zero e impede declarar ganho. Não confundir status esperado com F/R.

PDF/regimento/tarifa usam dados acadêmicos confirmados pelos documentos presentes.
As perguntas não prometem especificações ausentes. Páginas/seções são gabaritos.
