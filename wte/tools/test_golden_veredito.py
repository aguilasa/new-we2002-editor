#!/usr/bin/env python3
"""Testes do golden_veredito.py -- WTE-TASK-22.

O veredito e o gate: se ele disser PASSOU no lugar errado, todo handler da fase
4 entra sem julgamento nenhum. Por isso os tres codigos de saida sao exercitados
com relatorio plantado, e nao so o caminho feliz.

Um teste em particular vale por si: `test_faixa_declarada_ausente_reprova`. Um
gate que so subtrai excecoes passa verde quando o roteiro para de exercitar o
que dizia -- e a evidencia disso e a faixa declarada sumir.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import golden_veredito as V


def relatorio(*faixas) -> dict:
    return {"runs": [{"start": a, "end": b, "bytes": b - a + 1,
                      "kind": "data", "region": "OFS_X", "region_delta": 0}
                     for a, b in faixas]}


class TestLerFaixa(unittest.TestCase):

    def test_forma_normal(self) -> None:
        self.assertEqual(V.ler_faixa("11796..26527"), (11796, 26527))

    def test_sem_pontos_reprova_dizendo_a_forma(self) -> None:
        with self.assertRaises(V.FaixaInvalida) as e:
            V.ler_faixa("11796-26527")
        self.assertIn("INICIO..FIM", str(e.exception))

    def test_invertida_reprova(self) -> None:
        with self.assertRaises(V.FaixaInvalida):
            V.ler_faixa("100..10")

    def test_limite_nao_numerico_reprova(self) -> None:
        with self.assertRaises(V.FaixaInvalida):
            V.ler_faixa("a..b")


class TestJulgar(unittest.TestCase):

    def test_sem_divergencia_passa(self) -> None:
        codigo, linhas = V.julgar(relatorio(), [])
        self.assertEqual(codigo, 0)
        self.assertIn("byte-identico", linhas[0])

    def test_divergencia_nao_declarada_reprova_com_o_offset(self) -> None:
        """O positivo do gate: byte plantado tem de sair com endereco."""
        codigo, linhas = V.julgar(relatorio((4000, 4000)), [])
        self.assertEqual(codigo, 1)
        self.assertTrue(any("4000..4000" in l for l in linhas))

    def test_faixa_declarada_e_subtraida(self) -> None:
        codigo, _ = V.julgar(relatorio((11796, 26527)), [(11796, 26527)])
        self.assertEqual(codigo, 0)

    def test_faixa_declarada_ausente_reprova(self) -> None:
        """Declaracao que nao aparece e afirmacao que virou mentira.

        Diferente do `newWe2002`, que tolera a ausencia da dele: la a excecao e
        comportamento indefinido do original, aqui e gravacao deliberada -- ou
        acontece, ou o roteiro parou de exercitar o que dizia exercitar.
        """
        codigo, linhas = V.julgar(relatorio(), [(11796, 26527)])
        self.assertEqual(codigo, 3)
        self.assertTrue(any("11796..26527" in l for l in linhas))

    def test_declarada_nao_perdoa_a_vizinha(self) -> None:
        """Um byte de diferenca no limite ja e outra faixa.

        Sem isto, declarar `11796..26527` engoliria uma gravacao que comeca em
        11795 -- e o gate deixaria passar exatamente o tipo de erro de fronteira
        que a CORR-WTE-025 pegou (0-based contra 1-based).
        """
        codigo, _ = V.julgar(relatorio((11795, 26527)), [(11796, 26527)])
        self.assertEqual(codigo, 1)

    def test_inesperada_vence_ausente(self) -> None:
        """Com as duas falhas juntas, a mensagem e a da divergencia nova.

        Ordem escolhida: divergencia que ninguem declarou e o achado; faixa
        ausente e manutencao. Reportar a manutencao primeiro esconderia o byte
        que mudou.
        """
        codigo, linhas = V.julgar(relatorio((9, 9)), [(11796, 26527)])
        self.assertEqual(codigo, 1)
        self.assertIn("ninguem declarou", linhas[0])


class TestRoteiro(unittest.TestCase):

    def test_le_a_declaracao_do_cabecalho(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = Path(d) / "r.txt"
            r.write_text("# comentario\nalvo: ambos\nconhecida: 11796..26527\n"
                         "conhecida: 1921862..1921862\n! clique 1 2\n",
                         encoding="utf-8")
            self.assertEqual(V.faixas_do_roteiro(r),
                             [(11796, 26527), (1921862, 1921862)])

    def test_roteiro_sem_declaracao_nao_inventa(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = Path(d) / "r.txt"
            r.write_text("alvo: ambos\n! clique 1 2\n", encoding="utf-8")
            self.assertEqual(V.faixas_do_roteiro(r), [])


class TestMain(unittest.TestCase):

    def roda(self, rel: dict, *args: str) -> int:
        with tempfile.TemporaryDirectory() as d:
            j = Path(d) / "diff.json"
            j.write_text(json.dumps(rel), encoding="utf-8")
            return V.main([str(j), *args])

    def test_codigo_de_saida_e_o_veredito(self) -> None:
        self.assertEqual(self.roda(relatorio(), "--nenhuma"), 0)
        self.assertEqual(self.roda(relatorio((7, 7))), 1)
        self.assertEqual(self.roda(relatorio(), "--conhecida", "1..2"), 3)

    def test_faixa_malformada_sai_2_e_nao_1(self) -> None:
        """Erro de uso nao pode se disfarcar de reprovacao do gate."""
        self.assertEqual(self.roda(relatorio(), "--conhecida", "1-2"), 2)

    def test_nenhuma_com_conhecida_e_contradicao(self) -> None:
        self.assertEqual(
            self.roda(relatorio(), "--nenhuma", "--conhecida", "1..2"), 2)


class TestCheck(unittest.TestCase):
    """O `--check` que a bateria do Makefile cobra de todo script de `tools/`.

    Este nao gera arquivo, entao nao ha saida commitada para comparar -- e o
    mesmo caso do `check_lcl_props.py`. O que ele confere e o que envelheceria
    calado: `conhecida:` malformada num roteiro do gate so apareceria no meio de
    uma corrida de dez minutos, com duas copias de ~300 MB ja feitas.
    """

    def test_os_roteiros_commitados_passam(self) -> None:
        self.assertEqual(V.main(["--check"]), 0)

    def test_declaracao_malformada_reprova(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "golden-x.txt").write_text(
                "alvo: original\nconhecida: 10-20\n", encoding="utf-8")
            original = V.ROTEIROS
            try:
                V.ROTEIROS = Path(d)
                self.assertEqual(V.main(["--check"]), 2)
            finally:
                V.ROTEIROS = original

    def test_sem_roteiro_nenhum_reprova(self) -> None:
        """Zero roteiro nao e "nada a conferir": e o gate sem entrada."""
        with tempfile.TemporaryDirectory() as d:
            original = V.ROTEIROS
            try:
                V.ROTEIROS = Path(d)
                self.assertEqual(V.main(["--check"]), 2)
            finally:
                V.ROTEIROS = original


if __name__ == "__main__":
    unittest.main()
