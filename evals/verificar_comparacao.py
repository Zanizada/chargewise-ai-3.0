"""Impede concluir ganho com dados incompatíveis ou notas ausentes."""
from copy import deepcopy
import unittest
from evals.comparar_rag import comparar


def run():
    return {'hash_casos':'a','indice':{'fingerprint':'i'},'pipeline_sha256':'p',
        'config':{k:1 for k in ('k','chunk_size','chunk_overlap','temperature','top_p',
            'max_tokens','max_distance','max_context_chars','max_history_turns')},
        'avaliador':{'modelo':'juiz'},'registros':[{
            'caso':{'grupo':'respondivel','status':'respondido','fontes':['x']},
            'resultado':{'status':'respondido','citacoes':[{}],'latencia_segundos':1,
                'contextos':[{'metadata':{'document_id':'x'}}]},
            'revisao':{'faithfulness':None,'answer_relevancy':None}}]}


class TestesComparacao(unittest.TestCase):
    def test_nao_inventa_ganho_com_null(self):
        self.assertFalse(comparar(run(),run())['ganho_comprovado'])

    def test_rejeita_pipeline_e_conjunto_diferentes(self):
        for campo in ['hash_casos','pipeline_sha256']:
            a,b=run(),run()
            b[campo]='outro'
            with self.assertRaises(ValueError):
                comparar(a,b)

    def test_ganho_sem_ocultar_regressao(self):
        a,b=run(),run()
        a['registros'][0]['revisao'].update(faithfulness=0.8,answer_relevancy=0.8)
        b['registros'][0]['revisao'].update(faithfulness=0.9,answer_relevancy=0.8)
        self.assertTrue(comparar(a,b)['ganho_comprovado'])
        b['registros'][0]['revisao']['answer_relevancy']=0.7
        self.assertFalse(comparar(a,b)['ganho_comprovado'])


if __name__=='__main__':
    unittest.main()
