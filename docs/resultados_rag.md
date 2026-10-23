# Resultados RAG Sprint 04

RAGAS 0.4.3; relevância zero por protocolo em falhas/abstenções respondíveis

Uma repetição por condição; juiz GPT-OSS também é modelo avaliado. Não comprova significância estatística.

| Modelo | Prompt | Faithfulness (avaliados/13) | Answer relevancy (avaliados/13) | Status esperado /24 | Falhas |
|---|---|---|---|---|---|
| gemma4:31b | v1 | 0.9487 (13/13) | 0.7960 (13/13) | 24/24 | 0 |
| gemma4:31b | v2 | 0.9444 (12/13) | 0.7062 (13/13) | 23/24 | 1 |
| gpt-oss:120b | v1 | 0.9231 (13/13) | 0.7626 (13/13) | 24/24 | 0 |
| gpt-oss:120b | v2 | 1.0000 (13/13) | 0.7893 (13/13) | 24/24 | 0 |

## Comparações controladas

- gemma4:31b: deltas {'faithfulness': None, 'answer_relevancy': -0.089742135423595}; ganho comprovado segundo o critério conservador: False.
- gpt-oss:120b: deltas {'faithfulness': 0.07692307692307687, 'answer_relevancy': 0.02662012811474257}; ganho comprovado segundo o critério conservador: True.

Scores por caso estão em `evals/scores/`. Runs brutos com contexto e citações estão no ambiente local em `evals/rag_runs/final/`, ignorados pelo Git por conterem trechos de manual com restrição de reprodução pública. Reproduza com o downloader e protocolo. 