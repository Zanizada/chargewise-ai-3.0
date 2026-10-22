"""Interface testada sem LLM real; citações e sessões independentes."""
import unittest
from streamlit.testing.v1 import AppTest
from src.config import RAIZ
from src.schemas.resposta_rag import RespostaRAG, Citacao


class BotInterface:
    def responder(self, pergunta, sessao):
        return RespostaRAG(status='respondido',resposta='Tarifa acadêmica confirmada [1].',
            modelo='teste',prompt='v2',prompt_sha256='teste',citacoes=[Citacao(
                chunk_id='x',document_id='tarifa',titulo='Tabela de teste',pagina=None,
                secao='Vigência',origem='Teste acadêmico',natureza='simulada',
                trecho='A tarifa de teste é um exemplo acadêmico.')])
    def limpar(self, sessao):
        pass


class TestesInterface(unittest.TestCase):
    def iniciar(self):
        return AppTest.from_file(str(RAIZ/'app/streamlit_app.py')).run(timeout=30)

    def test_renderizacao_fontes_e_limpeza(self):
        at=self.iniciar()
        self.assertFalse(at.exception)
        at.session_state['rag']=BotInterface()
        at.chat_input[0].set_value('Qual tarifa?').run(timeout=30)
        self.assertFalse(at.exception)
        self.assertTrue(any('Tabela de teste' in e.label for e in at.expander))
        self.assertEqual(len(at.session_state['conversas']['Documentos de recarga']),2)
        at.sidebar.button[0].click().run()
        self.assertEqual(at.session_state['conversas']['Documentos de recarga'],[])

    def test_isolamento_de_navegadores(self):
        a,b=self.iniciar(),self.iniciar()
        self.assertNotEqual(a.session_state['session_id'],b.session_state['session_id'])
        a.session_state['rag']=BotInterface()
        a.chat_input[0].set_value('Teste A').run()
        self.assertEqual(b.session_state['conversas']['Documentos de recarga'],[])

    def test_operacional_simulado(self):
        at=self.iniciar()
        at.sidebar.radio[0].set_value('Operação simulada').run()
        at.chat_input[0].set_value('Quanto consumi este mês?').run(timeout=30)
        self.assertFalse(at.exception)
        self.assertTrue(any('142' in e.value for e in at.text))


if __name__ == '__main__':
    unittest.main()
