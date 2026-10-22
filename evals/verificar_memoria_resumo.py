"""Verifica poda, orçamento, isolamento e ausência de números no resumo."""
import unittest
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from src.chain.memoria_lcel import MemoriaLCEL


class Contador(FakeListChatModel):
    responses: list[str] = ['Não utilizado']
    def get_num_tokens_from_messages(self, messages, tools=None):
        return sum(len(m.content.split()) for m in messages)


class TestesResumo(unittest.TestCase):
    def test_resumo_sem_fatos_com_orcamento_e_isolamento(self):
        memoria = MemoriaLCEL(Contador(), 200)
        a = memoria.historico('A')
        a.add_messages([HumanMessage(content='Quanto consumi em 2099? ' + 'contexto ' * 90),
                        AIMessage(content='Valor antigo 9999. ' + 'resposta ' * 90)])
        a.add_messages([HumanMessage(content='Qual carregador disponível?'), AIMessage(content='Consultar fonte.')])
        self.assertIn('consumo', a.assuntos)
        resumo = a.mensagem_resumo().content
        self.assertNotIn('9999', resumo)
        self.assertNotIn('2099', resumo)
        self.assertLessEqual(Contador().get_num_tokens_from_messages(a.messages), 200)
        self.assertEqual(memoria.historico('B').messages, [])
        memoria.limpar('A')
        self.assertEqual(a.messages, [])

    def test_turno_invalido_preserva_estado(self):
        h = MemoriaLCEL(Contador(), 200).historico('A')
        h.add_messages([HumanMessage(content='Quanto consumi?'), AIMessage(content='Sem dado.')])
        antes = list(h.messages)
        with self.assertRaises(ValueError):
            h.add_messages([AIMessage(content='Inválido')])
        self.assertEqual(h.messages, antes)


if __name__ == '__main__':
    unittest.main()
