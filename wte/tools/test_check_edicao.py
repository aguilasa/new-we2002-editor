#!/usr/bin/env python3
"""Testes do `check_edicao.py`: a cobertura reprova quando deve.

O script existe para trocar prosa por reprovacao. Se as guardas dele nao
morderem, ele e prosa outra vez -- so que com cara de ferramenta, que e pior.
"""

from __future__ import annotations

import unittest

import check_edicao as C


class TestConjunto(unittest.TestCase):
    def test_sao_28_handlers(self):
        """Os 44 do grupo menos os 16 com dono fora, que e a conta do enunciado."""
        self.assertEqual(len(C.do_grupo_edicao()), 28)

    def test_a_tabela_cobre_exatamente_o_conjunto(self):
        self.assertEqual(sorted(C.INSTRUMENTO), C.do_grupo_edicao())

    def test_os_seis_grupos_estao_todos_representados(self):
        grupos = {v[0] for v in C.INSTRUMENTO.values()}
        self.assertEqual(grupos, {"barras", "nomes", "numeros", "atributos",
                                  "mover", "tatica"})


class TestGuardas(unittest.TestCase):
    def setUp(self):
        self.guardado = dict(C.INSTRUMENTO)

    def tearDown(self):
        C.INSTRUMENTO.clear()
        C.INSTRUMENTO.update(self.guardado)

    def _problemas(self) -> list[str]:
        return C.gera()[1]

    def test_handler_sem_instrumento_reprova(self):
        C.INSTRUMENTO.pop("relojTimer")
        self.assertTrue(any("sem instrumento" in p for p in self._problemas()))

    def test_instrumento_estatico_inexistente_reprova(self):
        C.INSTRUMENTO["relojTimer"] = ("tatica", C.ESTATICO, "nao_existe.py", "")
        self.assertTrue(any("nao existe" in p for p in self._problemas()))

    def test_modo_de_tela_inventado_reprova(self):
        """A guarda que impede o instrumento mais tentador de todos: escrever
        `compara_tela.sh --qualquercoisa` e declarar cobertura."""
        C.INSTRUMENTO["relojTimer"] = ("tatica", C.TELA,
                                       "compara_tela.sh --xyz", "")
        self.assertTrue(any("modo de tela" in p for p in self._problemas()))

    def test_outra_task_inexistente_reprova(self):
        C.INSTRUMENTO["relojTimer"] = ("tatica", C.OUTRA, "WTE-TASK-99", "")
        self.assertTrue(any("docs/tasks" in p for p in self._problemas()))

    def test_instrumento_para_handler_de_fora_reprova(self):
        C.INSTRUMENTO["colorearClick"] = ("tatica", C.ESTATICO,
                                          "dump_zonas.py", "")
        self.assertTrue(any("nao esta no grupo" in p for p in self._problemas()))

    def test_cobertura_de_tela_sem_trace_reprova(self):
        """A guarda que a tabela sozinha nao tem, e que custou uma atribuicao
        errada: dizer que um modo cobre um handler nao faz o handler disparar.

        O `dorsalMouseDown` esteve atribuido ao `--edicao`, que nao clica
        camisa nenhuma, e a atribuicao atravessou a revisao. Agora a evidencia
        de trace da propria corrida e quem decide.
        """
        C.INSTRUMENTO["dorsalMouseDown"] = ("numeros", C.TELA,
                                            "compara_tela.sh --edicao", "")
        self.assertTrue(any("nao tem" in p for p in self._problemas()))

    def test_sem_problema_a_tabela_sai(self):
        texto, problemas = C.gera()
        self.assertEqual(problemas, [])
        self.assertIn("edicao-cobertura", texto)


if __name__ == "__main__":
    unittest.main()
