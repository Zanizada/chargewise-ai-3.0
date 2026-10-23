# Escopo atual e evidências das Sprints 1 a 4

## Problema e escolha do contexto

O projeto aborda a comunicação sobre recarga compartilhada em condomínios no
contexto EV ChargeOps: moradores precisam consultar disponibilidade, consumo e
cobranças registradas; administração precisa comunicar regras e suporte. Esse recorte
permite perguntas verificáveis contra registros e documentos, com persona principal
morador e secundária administração. A proposta evolui para integração operacional,
mas esta entrega usa dados simulados e não comanda equipamentos.

## Tecnologias e justificativas

| Tecnologia | Motivo da escolha e limite |
|---|---|
| Python | Compartilha serviços entre terminal, testes e interface; favorece evolução do projeto local. |
| Ollama / ChatOllama | Mesmo cliente para geração local ou cloud; o modelo de referência operacional é GPT-OSS 120B. Disponibilidade e latência dependem do endpoint. |
| LangChain LCEL | Explicita prompt, modelo e parser, permitindo histórico por sessão na cadeia. |
| Pydantic v2 | Rejeita formatos/campos inválidos; validação estrutural não garante veracidade. |
| RunnableWithMessageHistory e ConversationTokenBufferMemory | Limitam histórico por tokens; resumo determinístico preserva somente assuntos, sem valores antigos. |
| Tiktoken | Estima orçamento de tokens; não é o tokenizer oficial dos modelos Ollama. |
| PyMuPDFLoader e splitter recursivo | Preservam páginas e produzem trechos rastreáveis para recuperação. |
| Nomic local e Chroma persistente | Vetorização e busca sem reingerir a cada execução; uso local autorizado conforme relato do usuário. |
| Streamlit | Interface local em Python compartilhando o serviço usado na CLI e avaliações. |
| RAGAS | Mede faithfulness e answer relevancy; juiz automático sujeito a viés e variação. |

## Qual versão cada evidência descreve

- A aplicação operacional atual aceita prompts v1/v2/v4; v3 é artefato histórico,
  com instruções incompatíveis com o schema atual. Não habilitar sem adaptação e avaliação.
- Os dois runs históricos de 29 casos não são reproduzíveis pelo avaliador atual
  de 19 casos. Também usam conteúdos diferentes sob a etiqueta v3.
- A memória LCEL limita tokens por descarte e resumo determinístico de assuntos,
  com até 128 tokens reservados. Não resume fatos/valores nem as palavras exatas.
  O RAG continua com histórico limitado por turnos e não foi alterado.
- O schema operacional atual contém energia/valor e não estado/potência. Campos
  adicionais citados nos PDFs antigos não comprovam sua presença no checkout atual.
- O ganho RAG v1/v2 é independente do ganho operacional. Agora existe experimento
  atual manual v1 / LCEL v1,v2,v4; ver `comparativo_operacional.md` e `evals/sprint3_results.json`.
- PDFs históricos contêm narrativas divergentes sobre a Sprint 2 e recursos não
  presentes neste checkout. Foram preservados; precisam de revisão antes de uso
  como descrição atual. Não há base para afirmar aqui que a Sprint 2 foi entregue.

## Pendências que não se resolvem apenas escrevendo documentação

1. Revisar a avaliação qualitativa assistida por IA já registrada para os 19 casos
   e os cinco testes da Sprint 2. Não foi inventada avaliação humana.
2. Incorporar ao PDF o comparativo atual manual/LCEL, com nota IA, tokens, latência
   e acurácia. A referência manual foi executada agora, não recuperada da entrega antiga.
3. Revisar as evidências consolidadas em `evals/sprint3_results.json`; os experimentos
   históricos incompatíveis foram preservados e separados da coleta atual.
4. Resumo de assuntos implementado e testado; explicar seu alcance na apresentação.
5. Instalação independente validada, incluindo interface com geração real via AppTest
   e corpus com mesmo fingerprint dos scores. Publicar versão final revisada e
   ensaiar apresentação; ainda não é um clone de commit publicado.
6. Produzir vídeo e revisar PDFs, conforme planejamento do usuário.

Os requisitos de grupo continuam fora desta revisão. Não se presume que entregáveis
antigos devam ser reenviados na CP4; esta lista aponta evidências ausentes do conjunto atual.
