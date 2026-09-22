# ChargeWise AI 3.0

Assistente conversacional em Python para consultas de recarga de veículos elétricos compartilhada em condomínios, desenvolvido no contexto do **EV Challenge — FIAP × GoodWe Brasil**, na disciplina Prompt and Artificial Intelligence.

O projeto atende principalmente moradores e também a administração do condomínio. A interação acontece pelo terminal, com respostas em português e saída estruturada validada por Pydantic v2.

## O que o programa faz

- Consulta a disponibilidade dos carregadores no cenário fornecido.
- Informa consumo mensal, valores registrados e dados da última recarga.
- Orienta o usuário sobre suporte e pedidos de agendamento.
- Mantém histórico separado por sessão enquanto o programa está aberto.
- Verifica padrões de prompt injection e encaminha certos pedidos de aconselhamento a profissionais habilitados.
- Valida o formato da resposta e confere fontes e determinados valores contra os dados operacionais.

**Os dados são fictícios.** O programa não está conectado a carregadores GoodWe, contas de moradores, pagamentos ou agendas reais. Não efetua reservas, cobranças, abertura de chamados ou comandos em equipamentos. O identificador da sessão organiza conversas; não autentica usuários.

## Modos de execução

| Modo | Como responde | Memória | Dependências |
|---|---|---|---|
| `demo` | Regras determinísticas, sem chamar IA | Limite de turnos | `requirements.txt` |
| `manual` | Requisição HTTP à API do Ollama | Limite de turnos | `requirements.txt` |
| `lcel` | LangChain: `ChatPromptTemplate \| ChatOllama \| PydanticOutputParser` | Histórico por sessão limitado por tokens | `requirements-langchain.txt` |

No modo LCEL, a cadeia é envolvida por `RunnableWithMessageHistory`. A memória utiliza `ConversationTokenBufferMemory` e descarta turnos antigos quando ultrapassa o orçamento. O histórico fica em memória RAM e termina ao encerrar o processo.

## 1. Preparar o ambiente

Use **Python 3.12** como referência para seguir estas instruções, com `pip` e `venv` disponíveis. Extraia o ZIP e abra um terminal na pasta que contém `main.py`.

### macOS / Linux

```bash
cd chargewise-ai-3.0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-langchain.txt
cp .env.example .env
```

### Windows — PowerShell

```powershell
cd chargewise-ai-3.0
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-langchain.txt
Copy-Item .env.example .env
```

Se a ativação não estiver disponível no seu terminal, utilize diretamente o executável do ambiente virtual no lugar de `python`: `.venv/bin/python` no macOS/Linux ou `.\.venv\Scripts\python.exe` no Windows.

O arquivo `requirements-langchain.txt` já inclui as dependências básicas. Para usar somente `demo` ou `manual`, sem contagem de tokens, basta instalar `requirements.txt`.

Mantenha o arquivo `.env` local. Não publique chaves de API.

## 2. Experimentar sem IA

A configuração inicial usa `demo`. Esse modo funciona sem Ollama e sem chave de API:

```bash
python -X utf8 main.py --modo demo
```

Digite, por exemplo:

```text
Qual carregador está disponível agora?
Quanto consumi este mês?
Qual foi minha última sessão de recarga?
```

Para uma única consulta, com a resposta completa em JSON:

```bash
python -X utf8 main.py --modo demo --pergunta "Quanto consumi este mês?" --json
```

No cenário padrão, o consumo fictício é de **142 kWh**, com valor registrado de **R$ 184,60**. A opção `--json` muda a apresentação da resposta; o terminal ainda imprime o cabeçalho do programa.

## 3. Configurar a IA com Ollama

Escolha uma das opções abaixo. Depois, execute o modo LCEL na etapa 4.

### Opção A — Ollama local

Instale o [Ollama](https://ollama.com/download) e mantenha o serviço aberto. Se ele não estiver iniciado, execute em outro terminal:

```bash
ollama serve
```

Baixe o modelo configurado no projeto:

```bash
ollama pull gpt-oss:120b
ollama list
```

O modelo de 120 bilhões de parâmetros exige recursos elevados de hardware e armazenamento. Verifique a capacidade da máquina antes de baixá-lo. Para experimentar um modelo menor, você pode baixar `qwen3:8b` e alterar `OLLAMA_MODEL` para esse nome; o modelo de referência da Sprint é `gpt-oss:120b`.

No `.env`, configure:

```dotenv
CHARGEWISE_MODO=lcel
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_API_KEY=
PROMPT_VERSAO=v2
CONTAR_TOKENS=true
```

### Opção B — API do Ollama Cloud

Crie uma chave na sua conta Ollama e confirme a disponibilidade do modelo no serviço. Configure o `.env`:

```dotenv
CHARGEWISE_MODO=lcel
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_API_KEY=SUBSTITUA_PELA_SUA_CHAVE
PROMPT_VERSAO=v2
CONTAR_TOKENS=true
```

A chamada direta à API cloud não exige baixar o modelo nem iniciar um servidor Ollama local. Use a URL base, sem acrescentar `/api/chat`; o cliente monta o caminho da requisição.

Referências oficiais: [execução local](https://docs.ollama.com/quickstart), [API cloud e autenticação](https://docs.ollama.com/cloud) e [modelo GPT-OSS](https://ollama.com/library/gpt-oss).

## 4. Rodar com LangChain

Com as dependências e o endpoint configurados:

```bash
python -X utf8 main.py --modo lcel --prompt v2
```

Para uma consulta isolada:

```bash
python -X utf8 main.py --modo lcel --prompt v2 --pergunta "Quanto consumi este mês?" --json
```

Para utilizar o cliente HTTP manual com o mesmo endpoint e modelo:

```bash
python -X utf8 main.py --modo manual --prompt v2
```

A primeira utilização do contador `tiktoken` pode precisar de conexão para baixar o encoding. No modo LCEL, o contador também é usado para limitar o histórico, independentemente da opção de registrar a estimativa de tokens por turno.

## 5. Conversar e alternar sessões

| Comando | Efeito |
|---|---|
| `/sessao NOME` | Seleciona um histórico separado, com identificador de 1 a 80 caracteres |
| `/historico` | Exibe as mensagens retidas na sessão atual |
| `/limpar` | Apaga o histórico da sessão atual |
| `/sair` | Encerra o programa |

A sessão inicial é `demo-1`, inclusive nos modos com IA. Para experimentar três turnos e isolamento, execute no mesmo processo:

```text
/sessao morador-a
Qual carregador está disponível agora?
Quanto consumi este mês?
Repita minha primeira pergunta.
/historico
/sessao morador-b
Repita minha primeira pergunta.
/sair
```

Cada nova execução do programa começa sem o histórico da execução anterior. Perguntas têm limite de 2.000 caracteres.

## 6. Cenários e opções do terminal

Os cenários ficam em `evals/contextos_simulados.json`:

| Cenário | Conteúdo |
|---|---|
| `padrao` | Três carregadores fictícios, consumo mensal e última sessão |
| `sem_dados` | Contexto sem registros operacionais |

Para consultar o cenário sem dados:

```bash
python -X utf8 main.py --modo demo --cenario sem_dados --pergunta "Quanto consumi este mês?" --json
```

Opções disponíveis:

| Opção | Valores / finalidade |
|---|---|
| `--modo` | `demo`, `manual` ou `lcel` |
| `--prompt` | `v1` ou `v2` |
| `--cenario` | `padrao` ou `sem_dados`; padrão: `padrao` |
| `--pergunta` | Faz uma consulta e encerra |
| `--json` | Mostra os campos estruturados da resposta |
| `--help` | Exibe a ajuda |

## Configuração completa

| Variável | Padrão | Finalidade |
|---|---|---|
| `CHARGEWISE_MODO` | `demo` | Modo usado quando `main.py` não recebe `--modo` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endereço base do serviço |
| `OLLAMA_MODEL` | `gpt-oss:120b` | Nome do modelo solicitado |
| `OLLAMA_API_KEY` | vazio | Credencial enviada como Bearer, quando configurada |
| `TEMPERATURE` | `0.2` | Parâmetro de geração entre 0 e 2 |
| `TOP_P` | `0.9` | Parâmetro de amostragem maior que 0 e até 1 |
| `MAX_TOKENS` | `512` | Limite de geração enviado como `num_predict` |
| `TIMEOUT_SEGUNDOS` | `90` | Tempo limite da requisição |
| `MAX_TURNOS` | `6` | Quantidade de turnos mantidos em `demo` e `manual` |
| `MAX_TOKENS_MEMORIA` | `2048` | Orçamento do histórico LCEL; não inclui system prompt nem pergunta atual |
| `PROMPT_VERSAO` | `v2` | Prompt selecionado quando `main.py` não recebe `--prompt` |
| `CONTAR_TOKENS` | `false` | Registra estimativa de tokens de entrada quando definido como `true` |

As opções `--modo` e `--prompt` prevalecem sobre o `.env`. Variáveis já definidas no ambiente do terminal também prevalecem sobre o `.env`.

A contagem com `tiktoken` usa `cl100k_base` sobre mensagens serializadas em JSON. É uma estimativa; os contadores retornados pelo serviço são registrados separadamente quando disponíveis.

## Contrato da resposta

O schema `ConsultaRecarga`, em `src/schemas/consulta_recarga.py`, define:

| Campo | Conteúdo |
|---|---|
| `intencao` | `disponibilidade`, `consumo`, `cobranca`, `sessao`, `agendamento`, `suporte`, `fora_escopo` ou `indefinida` |
| `status` | `respondido`, `dados_insuficientes`, `recusado` ou `encaminhar` |
| `resposta` | Texto apresentado ao usuário |
| `carregador_id` | Identificador do carregador ou `null` |
| `energia_kwh` | Energia não negativa ou `null` |
| `valor_brl` | Valor não negativo ou `null` |
| `fontes` | Identificadores das fontes utilizadas |
| `encaminhamento` | Destinatário da orientação; obrigatório para `status=encaminhar` |

O schema rejeita campos extras, respostas vazias e medidas inválidas. A validação de saída confere fontes e campos factuais selecionados contra o cenário. As fontes reconhecidas são `carregadores`, `consumo_mensal` e `ultima_sessao`.

## Testes e avaliações

Execute os testes de componentes a partir da raiz do projeto:

```bash
python -X utf8 -m unittest evals.verificar_componentes -v
```

Eles utilizam dados fixos e um servidor HTTP simulado; não exigem um modelo real. O teste LCEL requer as dependências correspondentes e o encoding do contador.

Para avaliar os 19 casos definidos em `evals/casos.json` no modo de demonstração:

```bash
python -X utf8 -m evals.executar --modo demo --prompt v2
```

Para avaliar uma execução real, configure o modelo no `.env` e informe explicitamente o modo:

```bash
python -X utf8 -m evals.executar --modo manual --prompt v1
python -X utf8 -m evals.executar --modo lcel --prompt v2
```

O avaliador usa `demo` e `v2` por padrão, mesmo que o `.env` selecione outros valores. Cada execução grava um JSON com nome e horário próprios dentro de `evals/`. Para escolher outro destino, acrescente `--arquivo CAMINHO.json`; o destino não pode existir, pois a escrita não sobrescreve resultados anteriores.

Os arquivos registram casos, respostas, erros, latência, contadores disponíveis, parâmetros e checagens básicas. As notas e justificativas humanas são preenchidas posteriormente. O processo retorna código `0` se todas as checagens passarem e `1` caso contrário. Resultados `demo` medem regras do programa, não qualidade de um modelo de IA.

## Organização do projeto

| Caminho | Responsabilidade |
|---|---|
| `main.py` | Interface de terminal e comandos de sessão |
| `src/app.py` | Coordenação de um turno e validações |
| `src/config.py` | Leitura e validação da configuração |
| `src/contexto.py` | Carregamento dos cenários |
| `src/modelos.py` | Respostas demo e cliente HTTP manual |
| `src/chain/builder.py` | Construção da cadeia LCEL |
| `src/chain/memoria.py` | Histórico manual limitado por turnos |
| `src/chain/memoria_lcel.py` | Histórico LCEL limitado por tokens |
| `src/chain/tokens.py` | Estimativa de tokens |
| `src/schemas/` | Contrato Pydantic da resposta |
| `src/guardrails/` | Moderação, heurísticas e validação de saída |
| `prompts/` | Arquivos de system prompt e tabela de versões |
| `evals/` | Casos, cenários, testes e execução das avaliações |
| `docs/` | Relatórios e registros de comparação |

## Equipe

| Integrante | RM |
|---|---|
| Arthur de Oliveira | 568986 |
| Miguel Piedade | 572445 |
| Rafael Zani Gizzi | 569033 |

Projeto acadêmico do grupo ARM — FIAP × GoodWe Brasil.
