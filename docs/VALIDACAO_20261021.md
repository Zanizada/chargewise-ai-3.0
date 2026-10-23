# Validação de entrega — 21/10/2026

## Testes locais

Comando: `python -X utf8 -B -m unittest evals.verificar_componentes evals.verificar_memoria_resumo evals.verificar_saida_operacional evals.verificar_rag evals.verificar_interface evals.verificar_comparacao`.

Resultado: **44 testes aprovados**, 6,083 segundos. Log válido: `testes_20261021_rede.txt`. Inclui interface Streamlit com modelo simulado, isolamento de sessões, memória, validação e comparação de avaliações. Não confundir esses testes com inferência real ou revisão humana.

A primeira tentativa, `testes_20261021.txt`, ocorreu em ambiente com conexões locais bloqueadas e foi interrompida após ficar sem progresso. Não é uma execução válida para medir o funcionamento com a infraestrutura disponível. Avisos de depreciação das bibliotecas permanecem; não foram tratados como falha nem se alterou a stack exigida apenas para removê-los.

## Consultas reais e RAGAS

Nova coleta com GPT-OSS 120B e Gemma4 31B, prompts v1/v2, 24 casos por condição. Todas as 96 consultas retornaram o status previsto, sem erros de geração. O fingerprint da base coincide com o dos scores anteriores. Parâmetros, hashes e scores por caso estão em `evals/scores/20261021/`; tabela em `resultados_rag_20261021.md`.

As métricas RAGAS medem dimensões de qualidade distintas do acerto de status. Resultados desta repetição devem ser lidos integralmente, incluindo regressões, sem substituir seletivamente scores anteriores. O juiz é automatizado (GPT-OSS), não um integrante. Não se atribui revisão humana inexistente.

Corpus, conjunto, prompt e configuração coincidem com a coleta anterior, mas o hash do pipeline mudou (a documentação histórica registra endurecimento dos códigos diagnósticos após aquela coleta). Por isso, não atribuir diferenças entre datas exclusivamente ao modelo ou à variabilidade. Comparações v1/v2 dentro desta nova coleta usam o mesmo pipeline e são verificadas pelo comparador.

Tentativa inicial de coleta com rede bloqueada: `evals/rag_runs/revalidacao_20261021/`. Coleta válida com rede: `evals/rag_runs/revalidacao_20261021_rede/`. Ambos ficam locais, ignorados pelo Git. O primeiro conjunto registra falhas de conexão e não integra a comparação de qualidade.

## Documentação e reprodução

Comandos da coleta e consolidação (usar outro diretório para uma nova execução):

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m evals.executar_rag --modelos gpt-oss:120b gemma4:31b --prompts v1 v2 --saida evals/rag_runs/revalidacao_20261021_rede
.\.venv-evals\Scripts\python.exe -X utf8 -B -m evals.avaliar_rag --todos evals/rag_runs/revalidacao_20261021_rede
.\.venv\Scripts\python.exe -X utf8 -B tools/consolidar_rag.py --runs evals/rag_runs/revalidacao_20261021_rede --scores evals/scores/20261021 --relatorio docs/resultados_rag_20261021
```

Nomic local permitido e duas versões RAG suficientes conforme confirmação de Miguel. Melhorias desta etapa atribuídas a Miguel, sem alterar autoria histórica. TXT contém repositório; vídeo será gravado pelo usuário. Os scripts do consolidador agora aceitam diretórios explícitos para preservar experimentos anteriores; o caminho antigo foi verificado e produziu o mesmo resumo JSON histórico.

Nenhum commit, push ou envio acadêmico foi executado nesta revisão. Acesso público e arquivos efetivamente publicados devem ser conferidos após o envio. Este registro não substitui a validação da versão clonada do repositório.
