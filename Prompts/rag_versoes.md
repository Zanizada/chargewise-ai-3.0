# Versões RAG

> Revalidação independente em 21/10/2026: [resultados novos](../docs/resultados_rag_20261021.md). A tabela abaixo preserva a primeira coleta; a nova execução não altera o conteúdo dos prompts nem substitui resultados anteriores. A interpretação de v1/v2 como as duas iterações exigidas foi confirmada por Miguel.

| Versão | Alteração | Hipótese | Ganho medido |
|---|---|---|---|
| v1 | Contexto documental, contrato e citação literal | Baseline RAG | GPT-OSS: F 0,9231 / R 0,7626; Gemma: F 0,9487 / R 0,7960 |
| v2 | Checagem de entidade/vigência, abstenção e natureza simulada | Menos extrapolação e melhor relevância | GPT-OSS: F 1,0000 / R 0,7893; deltas +0,0769 / +0,0266. Gemma: F 0,9444 (12/13) / R 0,7062; houve regressão e 1 timeout |

Arquivos imutáveis. SHA-256 registrado em cada run. Comparar mesmo corpus/conjunto,
modelo e parâmetros; registrar regressões e não apenas melhorias.

RAGAS 0.4.3; perguntas respondíveis n=13; conjunto completo n=24. Mesmo corpus,
índice e pipeline nos quatro experimentos finais. Uma repetição por condição;
juiz GPT-OSS 120B também é modelo avaliado. Não comprova significância estatística.
Faithfulness do Gemma v2 exclui 1 falha (N/A), portanto não se calcula delta F como
comparação completa. Relevância inclui zero por protocolo na falha. Nenhum run foi
selecionado novamente para ocultar timeout. Detalhes e hashes:
[resultados](../docs/resultados_rag.md) e [scores](../evals/scores/).
