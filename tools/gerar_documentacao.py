"""PDFs de autoria acadêmica e inventário; não reproduz manual protegido."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://en.goodwe.com/Ftp/EN/Downloads/User%20Manual/GW_HCA%20Series_User%20Manual-EN.pdf'


def pdf(path, titulo, secoes, data='14/10/2026'):
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['Heading2'].keepWithNext = True
    story = [Paragraph(escape(titulo), styles['Title']), Spacer(1, 12)]
    for heading, content in secoes:
        if heading in ('Avaliação e limitações', '4. Problemas encontrados e soluções'):
            story.append(PageBreak())
        story += [Paragraph(escape(heading), styles['Heading2'])]
        if isinstance(content, list):
            linhas = [[Paragraph(escape(str(c)), styles['BodyText']) for c in row] for row in content]
            table = Table(linhas, colWidths=[165, 160, 160], repeatRows=1)
            table.setStyle(TableStyle([('BACKGROUND', (0,0),(-1,0),colors.HexColor('#e8eef5')),
                ('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8)]))
            story.append(table)
        else:
            for paragraph in content.split('\n\n'):
                story.append(Paragraph(escape(paragraph).replace('\n','<br/>'), styles['BodyText']))
                story.append(Spacer(1, 6))
    path.parent.mkdir(parents=True, exist_ok=True)
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica',8)
        canvas.drawString(40,25,'ChargeWise AI | Sprint 04 | Documento acadêmico | ' + data)
        canvas.drawRightString(A4[0]-40,25,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=40,leftMargin=40,
        topMargin=40,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer)


def base():
    root = ROOT / 'data/knowledge_base'
    pdf(root / 'guia_academico.pdf', 'Guia do projeto ChargeWise - SIMULAÇÃO ACADÊMICA', [
        ('Consulta documental', 'A consulta documental recupera trechos da base e apresenta documento, seção ou página. Não é telemetria e não realiza ações em equipamentos.'),
        ('Consulta operacional simulada', 'O cenário operacional contém três carregadores fictícios. A disponibilidade, o consumo mensal e a última sessão vêm de registros JSON simulados. O identificador de sessão separa conversas, mas não autentica moradores.'),
        ('Uso responsável', 'Regimento, FAQ e tabela tarifária ARM são exemplos acadêmicos. Não são normas de condomínio real ou tarifas oficiais. Para intervenção elétrica, procure profissional habilitado.'),
        ('Fontes e limites', 'Especificações de produtos só podem ser respondidas quando documentadas na base. O chatbot não efetua reserva, cobrança, pagamento, abertura de chamado ou comando de equipamento.')])
    entries = []
    for id_, path, title, nature, category, source in [
        ('goodwe-hca-referencia','goodwe_hca_referencia.md','Referência GoodWe HCA V1.3','síntese com fonte oficial','manual',URL),
        ('regimento-arm','regimento_simulado.md','Regimento ARM simulado','simulação acadêmica','regimento','Autoria acadêmica ARM'),
        ('faq-arm','faq_simulada.md','FAQ ARM simulada','simulação acadêmica','faq','Autoria acadêmica ARM'),
        ('tarifas-arm','tarifas_simuladas.md','Tarifas ARM simuladas','simulação acadêmica','tarifa','Autoria acadêmica ARM'),
        ('guia-academico','guia_academico.pdf','Guia acadêmico ChargeWise','simulação acadêmica','guia','Autoria acadêmica ARM')]:
        entries.append({'id':id_,'path':path,'title':title,'nature':nature,'category':category,
            'source':source,'revision':'2026-10-14','sha256':sha256((root/path).read_bytes()).hexdigest()})
    entries.append({'id':'goodwe-hca-original','path':'local/goodwe_hca_manual.pdf',
        'title':'GoodWe HCA User Manual V1.3','nature':'manual oficial; cópia local não distribuída',
        'category':'manual','source':URL,'revision':'2024-07-24','optional':True})
    (root/'manifest.json').write_text(json.dumps({'schema_version':1,'documents':entries},
        ensure_ascii=False,indent=2),encoding='utf-8')


def relatorio():
    status = 'Avaliações de modelos e ganho ainda pendentes; não há scores fabricados.'
    metricas = ROOT / 'docs/resultados_rag.json'
    if metricas.exists():
        dados = json.loads(metricas.read_text(encoding='utf-8'))
        partes = []
        for e in sorted(dados['experimentos'],key=lambda e:(e['modelo']!='gpt-oss:120b',e['prompt'])):
            f,r = e['faithfulness'],e['answer_relevancy']
            def nota(x):
                return f"{x['media']:.4f}" if x['media'] is not None else 'N/A'
            partes.append(f"{e['modelo']} / {e['prompt']}: faithfulness {nota(f)} ({f['avaliados']}/{f['total']}), relevância {nota(r)} ({r['avaliados']}/{r['total']}); status esperado {e['status_esperado']}/24; falhas {e['falhas']}; fonte esperada recuperada {e['fonte_esperada_no_contexto']['acertos']}/13.")
        for c in dados['comparacoes']:
            def delta(valor):
                return f'{valor:+.4f}' if valor is not None else 'N/A (cobertura diferente)'
            conclusao = 'ganho nas duas métricas' if c['ganho_comprovado'] else 'sem ganho comprovado; regressão registrada'
            partes.append(f"{c['modelo']}: variação de faithfulness {delta(c['deltas']['faithfulness'])}; variação de relevância {delta(c['deltas']['answer_relevancy'])}; {conclusao}.")
        partes.append('RAGAS 0.4.3, juiz GPT-OSS 120B; uma repetição por condição. Scores não equivalem a revisão humana nem comprovam significância. Relevância fim a fim é zero em pergunta respondível sem resposta. Faithfulness é N/A nesse caso. Geração usa cloud e embeddings Nomic locais, permitidos e recomendados pelo professor conforme relato de Miguel em 15/10/2026. O HTTP 401 cloud anterior é evidência histórica, sem pendência de migração.')
        status = '\n\n'.join(partes)
    revalidacao = ROOT/'docs/resultados_rag_20261021.json'
    if revalidacao.exists():
        novos = json.loads(revalidacao.read_text(encoding='utf-8'))
        status += '\n\nRevalidação independente de 21/10/2026 (resultados anteriores preservados):'
        for e in novos['experimentos']:
            f, r = e['faithfulness'], e['answer_relevancy']
            status += f"\n{e['modelo']} / {e['prompt']}: F {f['media']:.4f} ({f['avaliados']}/{f['total']}), R {r['media']:.4f} ({r['avaliados']}/{r['total']}); status {e['status_esperado']}/{e['total']}; falhas {e['falhas']}."
        status += '\nAs coletas são reportadas separadamente, sem selecionar apenas os melhores resultados. Corpus e casos coincidem, mas o hash do pipeline difere entre datas; não atribuir essas diferenças somente ao prompt. A comparação v1/v2 é controlada dentro de cada coleta. Ver docs/resultados_rag_20261021.md e scores datados.'
    status += '\n\nTestes locais em 21/10/2026: 44 testes aprovados, incluindo componentes, memória, validação, RAG, interface e comparador. Log: docs/testes_20261021_rede.txt. A tentativa inicial restrita por permissões de rede foi separada da execução válida.'
    pdf(ROOT/'docs/relatorio_evolucao_sprint04.pdf', 'ChargeWise AI - Evolução Sprint 04', [
        ('1. Resumo da evolução', 'O projeto evoluiu do chatbot de terminal com contexto simulado, Ollama/LangChain, schema Pydantic e memória para recuperação documental com embeddings Nomic, Chroma persistente, fontes visíveis e interface Streamlit. A comparação operacional atual está em docs/comparativo_operacional.md; a referência manual foi reexecutada, não recuperada como medição histórica. Na tabela abaixo, N/D identifica medições originais indisponíveis, sem estimativas inventadas.'),
        ('2. Pipeline e decisões', 'PyMuPDFLoader lê PDFs inventariados; Markdown é separado por seção. RecursiveCharacterTextSplitter usa 900 caracteres e overlap 150. Nomic-embed-text é utilizado tanto na ingestão quanto na consulta. Chroma tem coleção vinculada ao hash da base e ativação após ingestão completa. Busca top-k=4, com distância de cosseno máxima 0,55 como ponto inicial. Distância não é score de qualidade. A geração usa ChatOllama com prompt versionado e contrato independente do operacional. Cada afirmação exige trecho literal recuperado e fonte existente. Não há garantia semântica universal contra alucinação.'),
        ('3. Comparativo antes/depois', [
            ['Item','Sprints 1/2 (versão original)','Sprint 04 (RAG avaliado)'],
            ['Scores por iteração','N/D - sem medição original verificável','Coleta inicial GPT-OSS v1/v2: F 0,9231 / 1,0000; R 0,7626 / 0,7893. Coleta inicial e revalidação de 21/10 na próxima página.'],
            ['Qualidade do contexto recuperado','N/D - artefato RAG original não disponível','Fonte esperada recuperada em 13/13 casos respondíveis. Proxy de cobertura; não comprova precisão semântica de cada trecho.'],
            ['Citação de fonte','Prompt histórico; sem prova documental executável','Documento/página/seção e trecho validados, exibidos na interface.']]),
        ('Avaliação e limitações', status),
        ('4. Problemas encontrados e soluções', 'O validador operacional aceitava somente três fontes e comparava números com uma fixture. Solução: schema/validador documental separado, preservando regras antigas. O mock HTTP dos testes antigos informava consumo sem fonte e era rejeitado: a fixture foi corrigida para citar consumo_mensal. Documentos maliciosos podem tentar alterar regras: trechos suspeitos são excluídos, instruções ficam fora dos documentos e citações são conferidas. O manual GoodWe restringe reprodução pública: o PDF original fica local e ignorado pelo Git; base pública usa síntese curta e documentos acadêmicos claramente identificados.'),
        ('5. Equipe e atualizações', 'Turma 1CCPI. Miguel Piedade - RM 572445: implementação das melhorias desta etapa, integração RAG, interface, testes e documentação, com apoio de IA. As contribuições das etapas anteriores permanecem no histórico do projeto (Arthur de Oliveira - RM 568986; Rafael Zani Gizzi - RM 569033).'),
        ('Reprodução e entrega', 'Repositório: https://github.com/Zanizada/chargewise-ai-3.0. Instalar requirements-sprint04-lock.txt em Python 3.12, configurar .env local, preparar Nomic local e baixar o manual conforme app/README.md; executar python -m src.rag.ingest e iniciar Streamlit. Protocolo e testes estão em evals/. Entrega prevista para 23/10/2026. Duas versões RAG v1/v2 e a melhoria medida atendem à interpretação confirmada por Miguel em 21/10; não é necessária uma v3 apenas para cumprir contagem de iterações.')], data='21/10/2026')


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--base',action='store_true')
    p.add_argument('--relatorio',action='store_true')
    args=p.parse_args()
    if args.base:
        base()
    if args.relatorio:
        relatorio()
