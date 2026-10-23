# Relatório RAG — Sprint 04

> Revalidação em 21/10/2026: resultados independentes em `resultados_rag_20261021.md`, com scores por caso em `evals/scores/20261021/`. Os números do corpo abaixo descrevem a coleta original, preservada para comparação. Testes locais: 44 aprovados em `testes_20261021_rede.txt`. Nomic local e a interpretação de duas versões RAG foram confirmados por Miguel.

## Base e procedência

`data/knowledge_base/manifest.json` inventaria manual GoodWe HCA V1.3 (cópia local
ignorada pelo Git), síntese curta de referência, regimento ARM, FAQ e tarifa simulados,
além do guia acadêmico em PDF. A equipe confirmou o uso de documentos simulados.
ChargeGrid/EV ChargeOps não são tratados como produtos comerciais com especificações
inventadas. A cópia oficial não pode ser distribuída sem autorização; o downloader
permite leitura local. PDFs históricos não são usados como corpus de recarga.

## Pipeline e chunking

PyMuPDFLoader preserva número de página (base 1). Markdown é dividido por seção.
RecursiveCharacterTextSplitter: 900 caracteres, overlap 150, separadores parágrafo,
linha, frase e espaço. Nomic gera vetores de 768 dimensões; busca e ingestão usam o
mesmo modelo. Índice Chroma persistente: 98 chunks na primeira ingestão local com
manual. IDs determinísticos; reingestão evita duplicação e embeddings desnecessários.
Mudança de fonte gera coleção nova. Ativação usa manifesto após conclusão; não apaga
índices antigos automaticamente. Alteração de modelo/endpoint/chunking exige ingestão.

Busca top-k=4, distância de cosseno <=0,55 como ponto inicial. Quando o usuário pede
explicitamente regimento, FAQ ou tabela, aplica filtro de categoria. Limiar foi testado
no conjunto fixo; não é garantia de relevância universal. Trechos enviados cabem em
6000 caracteres; memória é limitada a 4 turnos e não é fonte factual.

## Grounding e segurança

Saída documental tem afirmações, referências a chunk_id e trecho literal. Servidor
confere fonte presente na consulta, trecho exato, números na evidência e status.
Título, origem, página/seção e natureza vêm do inventário, nunca do modelo. UI usa texto
escapado, sem executar HTML ou comandos. JSON truncado é rejeitado; uma cerca completa
de Markdown pode ser removida antes da validação estrita.

Moderação de entrada preservada; trechos suspeitos são excluídos e o prompt separa
dados/instruções. Heurísticas não provam segurança geral e podem bloquear conteúdo
legítimo. Citação exata não comprova entailment semântico; RAGAS/revisão continuam
necessários. Sem evidência, dados_insuficientes; pedidos reconhecidos fora de domínio
ou de violação das regras são recusados. Recusas não recebem fontes fabricadas.

## Interface e integração

Streamlit chama o mesmo ServicoRAG usado por CLI/evals. Documental e operacional são
trilhas explícitas; terminal, schema operacional, consumo e sessões simuladas foram
preservados. Não há integração real com IoT, reserva ou pagamentos. Estado de conversa
fica por navegador; não existe autenticação de morador. Interface verificada com
AppTest e consulta cloud no navegador, mostrando fonte/trecho/natureza.

## Avaliação e resultados

24 perguntas congeladas em `evals/rag_cases.json`: 13 respondíveis, negativas,
segurança e memória. Gabaritos têm fontes/seções e pontos essenciais. Duas fixtures
adversariais substituem apenas o contexto do caso de teste. Coleta real: GPT-OSS 120B
e Gemma4 31B, prompts RAG v1/v2, uma repetição por condição. Não confundir os primeiros
runs de diagnóstico com os finais; a comparação final mantém corpus/índice/pipeline.

RAGAS 0.4.3 em ambiente isolado, juiz GPT-OSS 120B, temperature 0, saída até 4096,
embeddings Nomic local. Métricas Faithfulness e ResponseRelevancy (answer_relevancy).
Abstenção/falha em pergunta respondível tem relevância fim a fim 0 por protocolo e
faithfulness N/A. Publicar cobertura e denominadores, sem transformar N/A em 1.

Os valores consolidados estão em `resultados_rag.md` e `resultados_rag.json`, com
scores por caso em `evals/scores/`, após conclusão da avaliação. O juiz é automático:
não há notas humanas atribuídas à equipe. Uma repetição e autoavaliação GPT-OSS podem
introduzir variação/viés; não alegar significância estatística. Revisão da equipe é
necessária para confirmar interpretações de respostas e segurança.

No GPT-OSS v1→v2, faithfulness passou de 0,9231 para 1,0000 e relevância de 0,7626
para 0,7893 (13 perguntas respondíveis); as duas métricas melhoraram. O conjunto
completo teve status esperado em 24/24 casos e todas as 14 respostas factuais citaram
fontes válidas. Fonte esperada no contexto: 13/13, proxy de cobertura documental,
não prova de precisão semântica de cada chunk. Gemma v1 teve F 0,9487/R 0,7960;
v2 teve F 0,9444 (12 avaliadas/13) e R 0,7062, com 1 timeout. Não houve ganho Gemma.

## Problemas e limites

Gemma retornou JSON cercado; corrigiu-se parsing sem aceitar JSON incompleto. A busca
de regimento misturava manual e não cobria uma pergunta composta: filtragem por
categoria explicitamente pedida recuperou as seções necessárias. Uma falha de conexão
de Gemma no run final permanece registrada. RAGAS conflitou com a stack atual e foi
isolado, sem substituir os componentes da aplicação.

Nomic cloud retornou HTTP 401 apesar de geração cloud funcional. Implementação usa
Nomic local. Bônus multi-provider não é declarado: há dois modelos/prompts, mas um serviço de geração. 
Scanner redigido não encontrou padrões/chave atual em árvore pública e 41
blobs históricos; isso não substitui revisão de todos os possíveis segredos.

## Reprodução

Siga `app/README.md`. Para avaliação isolada:

```powershell
python -m venv .venv-evals
.\.venv-evals\Scripts\python.exe -m pip install -r requirements-ragas-lock.txt
.\.venv\Scripts\python.exe -m evals.executar_rag --modelos gpt-oss:120b gemma4:31b --prompts v1 v2 --saida evals/rag_runs/final
.\.venv-evals\Scripts\python.exe -m evals.avaliar_rag --todos evals/rag_runs/final
.\.venv\Scripts\python.exe tools/consolidar_rag.py
```

Runs nunca sobrescrevem arquivos antigos; para um experimento novo, usar diretório
novo e atualizar o consolidador explicitamente. O manual local pode atualizar-se:
somente comparar runs com fingerprints idênticos. Publicar scores redigidos, não o PDF
ou trechos integrais protegidos. `.env` nunca deve entrar no histórico.
