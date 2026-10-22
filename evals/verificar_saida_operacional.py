"""Regressões reais de suporte e ações inventadas, sem usar rede."""
import unittest
from src.schemas.consulta_recarga import ConsultaRecarga
from src.guardrails.output_validator import validar_saida, RespostaNaoConfiavel


class TestesSaidaOperacional(unittest.TestCase):
    def test_suporte_nao_pode_inventar_canal_ou_procedimento(self):
        for texto in ['Ligue para 0800-123-4567.', 'Procure suporte@example.com.',
                      'Reinicie o carregador.', 'Acesse o aplicativo para suporte.']:
            with self.subTest(texto=texto), self.assertRaises(RespostaNaoConfiavel):
                validar_saida(ConsultaRecarga(intencao='suporte',status='encaminhar',
                    resposta=texto,encaminhamento='suporte técnico'),{})

    def test_sem_agenda_nao_pode_confirmar_agendamento(self):
        with self.assertRaises(RespostaNaoConfiavel):
            validar_saida(ConsultaRecarga(intencao='agendamento',status='respondido',
                resposta='Você pode reservar pelo aplicativo.'),{})

    def test_encaminhamento_orientativo_e_aceito(self):
        r = ConsultaRecarga(intencao='suporte',status='encaminhar',
            resposta='Procure a administração ou suporte técnico.',
            encaminhamento='administração ou suporte técnico')
        self.assertIs(validar_saida(r,{}),r)

    def test_nao_afirma_chamado_aberto(self):
        with self.assertRaises(RespostaNaoConfiavel):
            validar_saida(ConsultaRecarga(intencao='suporte',status='encaminhar',
                resposta='Vou abrir um chamado.',encaminhamento='suporte técnico'),{})


if __name__ == '__main__':
    unittest.main()
