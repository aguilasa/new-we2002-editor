#!/usr/bin/env python3
"""Testes do `dump_blococor.py`.

Os que nao precisam do `.exe` montam a aritmetica em memoria; os que precisam
pulam quando `we-team-editor/` nao esta la, como os outros testes de `tools/`.

O que se mede aqui e o que o gerador AFIRMA e o `--check` nao veria: que a
conta logico -> absoluto e a do original, e que as ancoras reprovam quando a
resposta muda. Um gerador cuja unica prova e "a saida bate com o commitado"
nao prova nada no dia em que os dois estao errados juntos.
"""

from __future__ import annotations

import unittest

import dump_blococor as B


class TestAritmetica(unittest.TestCase):
    """A conta do `0x00404E70`, sem `.exe`."""

    def test_dentro_do_primeiro_setor_nao_salta(self) -> None:
        self.assertEqual(B.absoluto(0, 1000), 1000)
        self.assertEqual(B.absoluto(2047, 0), 2047)

    def test_o_salto_entra_a_cada_2048(self) -> None:
        # O primeiro byte do setor seguinte pula os 280 de EDC/ECC mais os 24
        # de cabecalho -- e a mesma geometria dos `OFS_*` do we2002_core.
        self.assertEqual(B.absoluto(2048, 0), 2048 + 304)
        self.assertEqual(B.absoluto(4096, 0), 4096 + 608)

    def test_a_base_e_somada_depois_do_salto(self) -> None:
        self.assertEqual(B.absoluto(2048, 100), 2048 + 304 + 100)


class TestContraOExe(unittest.TestCase):
    def setUp(self) -> None:
        if not B.EXE.is_file():
            self.skipTest(f"sem {B.REL_EXE} -- o bloco de cor NAO foi conferido")
        self.pe = B.PE(B.EXE.read_bytes())
        self.paleta, self.forma = B.tabelas(self.pe)

    def test_a_tabela_de_paleta_tem_um_byte_por_time(self) -> None:
        self.assertEqual(len(self.paleta), B.TIMES_N)

    def test_a_tabela_de_paleta_nao_e_identidade(self) -> None:
        """O motivo de o gerador existir.

        Se ela fosse identidade, a tabela seria dispensavel e o offset sairia
        de formula -- e nao ha por que extrair 95 bytes do `.exe`.
        """
        self.assertNotEqual(self.paleta, list(range(B.TIMES_N)))
        self.assertLess(len(set(self.paleta)), B.TIMES_N)

    def test_o_time_36_tem_ramo_proprio(self) -> None:
        # O `cmp eax,0x24` do original: a tabela guarda um valor que nao e
        # indice de paleta, e o codigo nunca a consulta para ele.
        self.assertEqual(self.paleta[B.TIME_SENEGAL], 255)

    def test_as_cinco_bases_de_forma_sao_crescentes(self) -> None:
        self.assertEqual(len(self.forma), 5)
        self.assertEqual(self.forma, sorted(self.forma))

    def test_as_ancoras_fecham(self) -> None:
        provas = B.confere(self.paleta, self.forma)
        self.assertEqual(len(provas), 8)

    def test_ancora_plantada_reprova(self) -> None:
        """Trocar um byte da tabela tem de derrubar a conferencia.

        Sem isto, `confere` poderia estar somando as ancoras erradas e ninguem
        saberia -- o teste acima passaria do mesmo jeito.
        """
        paleta = list(self.paleta)
        paleta[0] = (paleta[0] + 1) % 256
        with self.assertRaises(B.BlocoCorError) as ctx:
            B.confere(paleta, self.forma)
        self.assertIn("OFS_FLAG_COLOURS", str(ctx.exception))

    def test_forma_plantada_reprova(self) -> None:
        forma = list(self.forma)
        forma[2] += 1
        with self.assertRaises(B.BlocoCorError) as ctx:
            B.confere(self.paleta, forma)
        self.assertIn("OFS_FLAG_SHAPE_COPY_3", str(ctx.exception))

    def test_a_saida_e_deterministica(self) -> None:
        a = B.pascal(self.paleta, self.forma)
        b = B.pascal(self.paleta, self.forma)
        self.assertEqual(a, b)
        self.assertIn("PALETA_DA_BANDEIRA", a)
        self.assertIn("FORMA_DA_BANDEIRA", a)


if __name__ == "__main__":
    unittest.main()
