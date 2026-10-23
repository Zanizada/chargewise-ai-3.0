# Resultados RAG Sprint 04

Revalidação de **21/10/2026**. A coleta anterior permanece em `resultados_rag.md`. Base, conjunto e configurações coincidem; o hash do pipeline difere entre datas. As comparações controladas abaixo são internas à nova coleta.

RAGAS 0.4.3; relevância zero por protocolo em falhas/abstenções respondíveis

Uma repetição por condição; juiz GPT-OSS também é modelo avaliado. Não comprova significância estatística.

| Modelo | Prompt | Faithfulness (avaliados/13) | Answer relevancy (avaliados/13) | Status esperado /24 | Falhas |
|---|---|---|---|---|---|
| gemma4:31b | v1 | 0.9615 (13/13) | 0.7815 (13/13) | 24/24 | 0 |
| gemma4:31b | v2 | 0.8974 (13/13) | 0.7233 (13/13) | 24/24 | 0 |
| gpt-oss:120b | v1 | 1.0000 (13/13) | 0.7928 (13/13) | 24/24 | 0 |
| gpt-oss:120b | v2 | 1.0000 (13/13) | 0.7970 (13/13) | 24/24 | 0 |

## Comparações controladas

- Gemma4 v1 → v2: fidelidade −0,0641; relevância −0,0582. Regressão nas duas métricas.
- GPT-OSS v1 → v2: fidelidade estável em 1,0000; relevância +0,0042. Melhoria pequena segundo o critério do protocolo; uma execução não comprova significância estatística.

As quatro condições tiveram 24/24 status esperados, fonte esperada recuperada em 13/13 casos respondíveis e citações nas 14 respostas factuais de cada condição. Esses indicadores não substituem avaliação semântica. Nesta revalidação o Gemma não repetiu o timeout anterior; a falha histórica permanece documentada.

Scores por caso: `evals/scores/20261021`. Runs brutos locais: `evals/rag_runs/revalidacao_20261021_rede`, ignorados pelo Git por conterem trechos de manual com restrição de reprodução pública. Reproduza com o downloader e protocolo. Não há notas humanas inventadas.
