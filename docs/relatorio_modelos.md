# Relatório de modelos — ChargeWise AI

> Revalidação RAG de 21/10/2026: `resultados_rag_20261021.md`. Quatro condições (GPT-OSS/Gemma, prompts v1/v2), com resultados antigos preservados. As configurações efetivas e hashes estão nos scores datados em `evals/scores/20261021/`.

> Atualização de 16/10/2026: as pendências e comandos históricos da seção Sprint 03
> abaixo descrevem os runs antigos. Nova comparação operacional com GPT-OSS,
> manual v1 e LCEL v1/v2/v4, está em [comparativo_operacional.md](comparativo_operacional.md).
> Resultados atuais em `evals/sprint3_results.json`; notas assistidas por IA e revisão
> humana.

Data: 21/09/2026. Evidências reais disponíveis; avaliação qualitativa humana e consolidação completa pendentes.

## Método e configuração

Comparação descritiva de duas execuções, com uma repetição por modelo. Os hashes dos casos e contextos coincidem. O hash do arquivo system_prompt_v3.md difere; portanto, a etiqueta v3 não identifica o mesmo conteúdo nos dois testes. Qwen foi executado localmente e GPT-OSS no Ollama Cloud. Não é possível atribuir diferenças exclusivamente ao modelo, à arquitetura ou ao prompt.

| Parâmetro | Qwen3 8B | GPT-OSS 120B |
|---|---|---|
| Modelo solicitado | qwen3:8b | gpt-oss:120b |
| Serviço | Ollama local | Ollama Cloud |
| Endpoint | http://localhost:11434 | https://ollama.com |
| Modo / prompt | LCEL / v3 | LCEL / v3, conteúdo diferente |
| temperature / top_p | 0,2 / 0,9 | 0,2 / 0,9 |
| max_tokens (num_predict) | 2048 | 2048 |
| Timeout / retries máximos | 120 s / 1 | 120 s / 1 |
| Memória / resumo / contexto | 1500 / 200 / 8192 tokens | 1500 / 200 / 8192 tokens |
| format=json | Sim | Sim |
| Python | 3.13.2 | 3.12.10 |
| Repetições / casos | 1 / 29 | 1 / 29 |

## Resultados medidos

| Métrica | Qwen3 8B local | GPT-OSS 120B cloud |
|---|---:|---:|
| Casos avaliados | 29 | 29 |
| Checagens básicas aprovadas | 27/29 (93,10%) | 26/29 (89,66%) |
| Falhas de execução/validação | 2 | 1 |
| Turnos com chamada ao modelo | 21 | 21 |
| Tentativas, incluindo retries | 29 | 23 |
| Latência média — todos os turnos (s) | 7,23 | 1,24 |
| Latência média — turnos com modelo (s) | 9,99 | 1,72 |
| Tokens de entrada/turno com modelo | 3001,10 | 2090,52 |
| Tokens de saída/turno com modelo | 632,24 | 389,86 |
| Schema válido por tentativa | 28/29 (96,55%) | 23/23 (100%) |
| Schema válido na primeira tentativa | 20/21 (95,24%) | 21/21 (100%) |
| Acurácia dos campos esperados | 12/12 (100%) | 9/12 (75%) |
| Nota qualitativa humana (0–2) | Não avaliada | Não avaliada |

As médias de tokens somam as tentativas do mesmo turno e usam os 21 turnos com contadores completos do serviço. Não são médias por tentativa. A latência dos turnos com modelo inclui processamento da aplicação e retries; não é uma medição isolada do tempo de inferência. Os oito turnos sem chamada também entram na taxa geral de checagens e na latência de todos os turnos.

A acurácia dos campos tem denominador de 12 campos explicitamente previstos nos casos; não significa aprovação de todas as respostas. As falhas do Qwen não contradizem seus 100% nessa métrica, pois os casos em questão não possuem esses campos esperados. Schema válido verifica estrutura, não veracidade.

## Falhas e interpretação

- Qwen: M03 (recuperar a primeira pergunta) e E06 (potência da vaga 15) foram rejeitados após validação de formato/evidências.
- GPT-OSS: F01 (estado da vaga 12) foi rejeitado. F02 e F03 produziram saídas, mas reprovaram as checagens esperadas na sequência de potência. A perda do primeiro turno prejudica o contexto da sequência; a investigação causal completa não foi realizada.
- Nesta execução, Qwen obteve mais checagens aprovadas; GPT-OSS teve menor latência medida e maior taxa de schema válido. Não há vencedor geral comprovado.
- O texto operacional exibido é renderizado por regras após validar os campos do LLM. As tentativas brutas devem ser lidas para avaliar o comportamento do modelo, além da resposta final controlada.

## Evidências e rastreabilidade

- [Qwen: execução original](../evals/runs/real_20260921T224455481243Z.json)
- [GPT-OSS: execução original](../evals/runs/gpt_oss_120b_20260921T230755Z.json)
- [Manifesto de comparação](comparativo_execucoes.json)

Os dois JSONs originais foram preservados byte a byte. O manifesto mantém as configurações e hashes de cada execução separadamente. Não foram fabricadas notas humanas nem resultados da baseline.
---

## Sprint 04 — comparação RAG independente

Os dados acima pertencem à Sprint 03 e não demonstram qualidade do RAG implementado.
A nova avaliação usa 24 perguntas fixas, corpus/índice e pipeline comuns, dois prompts
RAG e uma repetição por condição. Coleta e scores são reais; consultar
[resultados_rag.md](resultados_rag.md) e [scores por caso](../evals/scores/).

| Parâmetro | GPT-OSS 120B | Gemma4 31B |
|---|---|---|
| Modelo do endpoint | gpt-oss:120b | gemma4:31b |
| Geração | Ollama Cloud | Ollama Cloud |
| temperature | 0 | 0 |
| k / distância máxima de cosseno | 4 / 0,55 | 4 / 0,55 |
| top_p | 0,9 | 0,9 |
| max_tokens / num_predict | 2048 | 2048 |
| Timeout / retry de geração | 90 s / nenhum | 90 s / nenhum |
| Embeddings | Nomic local, 768 dimensões | Mesmo índice e modelo |
| Chunking | 900 caracteres, overlap 150 | Igual |
| Contexto / histórico | 6000 caracteres / 4 turnos | Igual |
| Prompts / casos | RAG v1 e v2 / 24 | Igual |

RAGAS 0.4.3 rodou em ambiente isolado devido a import incompatível com a stack nova.
Juiz GPT-OSS 120B com temperature 0, num_predict 4096, Nomic local, strictness 3,
max_workers 2 e max_retries 1. O juiz também é um dos modelos avaliados: registrar viés.
Faithfulness usa suporte no contexto; relevância usa ResponseRelevancy. Recusa/falha
em pergunta respondível recebe relevância fim a fim 0 e faithfulness N/A conforme
protocolo, sem fingir que esse zero foi retornado pelo RAGAS.

Gemma demonstrou saída cercada em Markdown: parser aceita somente cerca completa,
sem reparar truncamento. A comparação final foi reexecutada com adaptador comum para
os dois modelos. Um ConnectTimeout no Gemma v2 foi mantido e reduz cobertura/relevância;
não houve reexecução seletiva para ocultar falha. Os primeiros runs problemáticos
permanecem locais como diagnóstico e não definem superioridade geral do modelo.

O catálogo não apresentou Gemma4 26B; a variante 31B disponível foi usada conforme
autorização da equipe. Nomic cloud respondeu HTTP 401; geração cloud não comprova
embeddings cloud.  Não se declara bônus de serviços distintos por usar dois modelos
do mesmo Ollama. Comparações são descritivas; uma repetição não sustenta significância.
