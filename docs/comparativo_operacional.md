# Comparação operacional — Sprints 2/3

Coleta real atual com GPT-OSS 120B no Ollama Cloud. Referência manual executada
agora; não reconstrói nem comprova uma entrega histórica. Notas qualitativas
abaixo foram atribuídas por revisão assistida por IA (Codex), pendentes de revisão humana.

| Condição | Checagens /19 | Falhas /19 | Qualidade IA (0–2) | Latência todos (s) | Tokens entrada estimados (15 turnos) | Campos corretos /6 | Saídas aceitas com modelo /15 |
|---|---:|---:|---:|---:|---:|---:|---:|
| manual_v1 | 7 | 11 | 0.6316 | 0.9746 | 1023.40 | 0 | 4 |
| lcel_v1 | 7 | 12 | 0.5263 | 0.9971 | 1023.40 | 0 | 3 |
| lcel_v2 | 14 | 4 | 1.4737 | 0.8654 | 1022.80 | 6 | 11 |
| lcel_v4 | 19 | 0 | 1.9474 | 1.0670 | 1465.67 | 6 | 15 |

## Interpretação e parâmetros

Comparar manual v1 com LCEL v1 isola a mudança de integração/memória, mantendo
o prompt; não se deve atribuir ao LCEL o ganho obtido ao trocar também o prompt.
LCEL v1, v2 e v4 foram avaliados com o mesmo código, casos, contexto e parâmetros.
temperature=0; top_p=0,9; max_tokens=2048; timeout=45 s; sem retries.
Manual retém 6 turnos; LCEL tem 2048 tokens totais, até 128 reservados ao resumo
determinístico de assuntos. Os casos de memória incluem três turnos e outra sessão.

O índice de campos usa os seis campos explicitamente previstos no conjunto,
não todas as afirmações em linguagem natural. Saída aceita combina schema e
validação de evidências; não é uma taxa isolada de parsing. Latência inclui
aplicação e rede. Uma repetição não estabelece superioridade geral.

Tokens estimados têm cobertura 15/15 em cada condição. Os contadores reais
do serviço e suas coberturas estão no JSON consolidado; não comparar médias
com cobertura diferente como se fossem a mesma população.

Runs de diagnóstico anteriores foram preservados em diretório separado. Não
foram usados para substituir seletivamente falhas da coleta final.

## Evidências

- `evals/sprint3_results.json`: métricas, hashes, limitações e notas por caso.
- `evals/revisao_operacional_ia.json`: decisões qualitativas e justificativas.
- `evals/operacional_runs/20261016_final/`: perguntas, respostas, saídas rejeitadas e medições.
- `evals/operacional_runs/20261016_controlado/`: diagnóstico anterior aos controles adicionais.

## Cinco casos da Sprint 2 — LCEL v4

| Caso | Pergunta | Resposta exibida | Avaliação IA | Justificativa |
|---|---|---|---|---|
| H01 | Qual carregador está disponível agora? | O carregador disponível é vaga-12. | Adequada | Identifica vaga-12 e cita a fonte operacional correta. |
| H02 | Quanto consumi este mês? | Neste mês simulado, o consumo foi de 142 kWh, totalizando R$ 184,60. | Adequada | Consumo e valor coincidem com o cenário, com fonte correta. |
| H03 | Por que fui cobrado na última recarga? | Na última recarga (sessão sessao-demo-18) foram consumidos 28 kWh, resultando em cobrança de R$ 36,40, conforme registro simulado. | Adequada | Explica a cobrança usando os registros de energia e valor, sem tarifa inventada. |
| H04 | O carregador não inicia a recarga. | Problema de início de recarga identificado. Como simulação, procure a administração ou o suporte técnico para assistência. | Adequada | Orienta procurar administração ou suporte; não executa chamado nem intervenção. |
| H05 | Posso reservar um horário para recarga? | Não há sistema de reserva integrado; consulte a administração para agendar um horário de recarga. | Adequada | Reconhece ausência de agenda integrada e orienta consultar administração. |
