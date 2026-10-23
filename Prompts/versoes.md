# Versões de prompt

| Versão | Origem/mudança | Objetivo | Ganho medido |
|---|---|---|---|
| v1 | Cópia fiel do system prompt enviado na documentação da Sprint 1 | Preservar referência documental | LCEL atual: 7/19 checagens; qualidade IA 0,5263/2 |
| v2 | Tags XML, regras de dados ausentes, limites e JSON | Melhorar grounding operacional | LCEL atual: 14/19; qualidade IA 1,4737/2; ainda falha em suporte/agendamento |
| v3 histórico | Artefato de experimentos antigos com estado/potência e roteamento distintos | Preservar rastreabilidade; não suportado pela configuração atual | Não há comparação controlada de ganho; os dois runs históricos usam hashes v3 diferentes |
| v4 | Regras explícitas por intenção, suporte sem contatos inventados, ausência de agenda, memória e chaves exatas | Corrigir falhas reais mantendo schema estrito | LCEL atual: 19/19; qualidade IA 1,9474/2. Ganho v2→v4: +5 checagens; +0,4737 na nota IA |

O aplicativo acrescenta schema e contexto às duas versões. Portanto, executar v1 aqui é uma adaptação do prompt histórico ao app novo, não a reprodução de uma Sprint 2 implementada. O avaliador registra o hash do system prompt efetivo.

O demo não usa o prompt para gerar as respostas por regras. Compará-lo com v1/v2 não demonstra ganho de prompt. Execute os modelos reais e registre inclusive regressões.

Coleta atual de 16/10/2026: GPT-OSS 120B cloud, mesmo código/casos/parâmetros em
LCEL v1/v2/v4; uma repetição. Qualidade atribuída por revisão assistida por IA,
não por integrantes. Nota v4 inclui ressalva de formatação monetária em H06.
Prompt maior aumenta tokens estimados: aproximadamente 1023 por turno em v1/v2
contra 1466 em v4. Não comprova significância nem ganho exclusivamente da arquitetura.
Detalhes: [comparativo operacional](../docs/comparativo_operacional.md).
