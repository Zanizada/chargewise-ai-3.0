# Avaliação manual equivalente (0–1)

Aplicar no mesmo conjunto/corpus a cada iteração. Esta via é aceita pelo enunciado,
mas justificar a impossibilidade de RAGAS no relatório; não presumir equivalência
numérica exata com o algoritmo. Checagens de palavras não são avaliação de qualidade.

Faithfulness: listar afirmações verificáveis da resposta exibida e, para cada uma,
indicar suporte ou ausência de suporte nos trechos realmente recuperados.
Score = sustentadas / total de afirmações verificáveis. Citação existente não basta.
Sem afirmações factuais (abstenção/falha): N/A, nunca 1 automático.

Answer relevancy: 1 = cobre todos os pontos essenciais sem conteúdo irrelevante;
0,75 = pequena omissão; 0,5 = atendimento parcial; 0,25 = tangencial; 0 = não atende.
Recusa indevida/falha em pergunta respondível recebe 0. Recusa correta em caso
negativo recebe 1 de relevância, separada do agregado de perguntas respondíveis.

Registrar avaliador, data, método, justificativa, afirmações e referências.
Se uma revisão for assistida por IA, declarar isso e exigir validação da equipe.
Não atribuir notas a integrantes que não revisaram. Dois revisores independentes são
recomendados. Dados ausentes ficam null e impedem comparação de ganho completo.

Médias por grupo (respondível/negativo/segurança/memória), com denominadores,
cobertura, falhas, taxa de abstenção e citações. Comparador exige mesmas condições.
