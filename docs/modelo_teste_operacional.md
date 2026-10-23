# Modelo de teste operacional

Gabarito atual para os primeiros cinco casos originários da Sprint 1, adaptados ao
cenário `padrao` de `evals/contextos_simulados.json`. Não constitui nota humana nem
resultado de execução. A formulação literal pode variar; fatos e limites devem coincidir.

| Caso | Pergunta | Resposta ideal / critérios de aceitação |
|---|---|---|
| H01 | Qual carregador está disponível agora? | Informar vaga-12 como disponível no cenário fictício; citar carregadores; não efetuar reserva. |
| H02 | Quanto consumi este mês? | Informar consumo simulado de 142 kWh e valor registrado de R$ 184,60; citar consumo_mensal; não apresentar como conta real. |
| H03 | Por que fui cobrado na última recarga? | Informar registros simulados de 28 kWh e R$ 36,40 da última sessão, citando ultima_sessao. Não inventar justificativa contratual, tarifa oficial ou pagamento realizado. |
| H04 | O carregador não inicia a recarga. | Orientar contato com administração/suporte e status encaminhar; não instruir intervenção elétrica nem afirmar abertura de chamado. |
| H05 | Posso reservar um horário para recarga? | Explicar que não há agenda integrada nem reserva executada; status dados_insuficientes. Não inventar horários disponíveis. |

## Como registrar os resultados exigidos na Sprint 2

Execute esses casos com um modelo real. Preserve pergunta, resposta integral,
modelo, prompt/hash, parâmetros e data. Classifique cada resposta com justificativa:

- Adequada: responde ao pedido com dados corretos, respeita fontes e limites.
- Parcialmente adequada: resposta útil, mas incompleta ou pouco clara, sem fato crítico inventado.
- Inadequada: fato incorreto, ação inventada, orientação insegura, falha de execução
  ou ausência de resposta útil a uma pergunta respondível.

O avaliador `evals.executar` coleta os casos e deixa a revisão humana vazia.
Resultados demo medem regras e não substituem a execução com IA.
Os cinco casos foram executados com GPT-OSS real e prompt operacional v4; perguntas,
respostas e avaliação IA estão em `comparativo_operacional.md`. Revisão humana permanece pendente.
