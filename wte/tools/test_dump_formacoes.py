#!/usr/bin/env python3
"""Testes do `dump_formacoes.py`: as quatro guardas, com dado plantado.

O gerador le a arvore de verdade, entao o teste que vale nao e "os numeros de
hoje continuam os de hoje" -- e **as guardas disparam**. Guarda nunca
exercitada e guarda ausente, que foi o que a CORR-WTE-020 achou no
`dfm2lfm.py`.

A quarta guarda e a mais barata de perder e a mais cara de nao ter: ela cruza o
NOME do item (`4 - 5 - 1  A`, que vem do `.lfm`) com a contagem de papeis (que
vem de `.data`). Se a ordem dos 18 registros nao casasse com a ordem da lista,
ou se o decodificador lesse a coluna de X achando que era a de papel, nenhuma
das outras tres pegaria.
"""

from __future__ import annotations

import unittest

import dump_formacoes as F

REAL = F.EXE.exists()


def zerada() -> dict[str, list[int]]:
    return {k: [0] * F.JOGADORES for k in ("papel", "x", "y", "zona")}


@unittest.skipUnless(REAL, "we-team-editor/we-team-editor.exe nao esta no disco")
class TestArvoreReal(unittest.TestCase):
    def setUp(self):
        pe = F.PE(F.EXE.read_bytes(), F.REL_EXE)
        self.formacoes, self.passo = F.varre(pe)

    def test_a_arvore_real_passa(self):
        F.confere(self.formacoes, self.passo)

    def test_sao_dezoito_de_onze(self):
        self.assertEqual(len(self.formacoes), F.FORMACOES)
        for f in self.formacoes:
            for k in ("papel", "x", "y", "zona"):
                self.assertEqual(len(f[k]), F.JOGADORES)

    def test_o_registro_default_e_zero(self):
        """O buraco do outro ramo -- e a razao da isencao da conferencia 2."""
        f = self.formacoes[F.FORMACAO_DEFAULT]
        for k in ("papel", "x", "y", "zona"):
            self.assertEqual(f[k], [0] * F.JOGADORES, k)

    def test_o_passo_e_02(self):
        self.assertAlmostEqual(self.passo, 0.2, places=12)

    def test_a_tabela_fecha_no_primeiro_ponteiro(self):
        self.assertEqual(F.REGISTRO * F.FORMACOES,
                         F.FIM_DA_TABELA - F.TABELA)


@unittest.skipUnless(REAL, "we-team-editor/we-team-editor.exe nao esta no disco")
class TestGuardas(unittest.TestCase):
    def setUp(self):
        pe = F.PE(F.EXE.read_bytes(), F.REL_EXE)
        self.formacoes, self.passo = F.varre(pe)

    def test_papel_fora_das_abreviaturas_derruba(self):
        self.formacoes[0]["papel"][3] = 99
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("abreviaturas", str(e.exception))

    def test_zona_fora_das_zonas_derruba(self):
        self.formacoes[0]["zona"][3] = 11
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("wte_zonas", str(e.exception))

    def test_destino_fora_do_campo_derruba(self):
        self.formacoes[0]["x"][3] = 200      # 200*8-2 = 1598, campo tem 395
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("fora do campo", str(e.exception))

    def test_a_guarda_da_grade_e_sobre_a_FORMULA_e_nao_sobre_o_dado(self):
        """Nenhum `x` ou `y` pode furar a grade, e isso e por construcao.

        `x*8 - 2` e sempre 6 modulo 8 e `((y-3) div 2)*5 - 7` e sempre 3 modulo
        5, para QUALQUER byte. Plantar dado nao derruba esta guarda, e dizer
        que ela confere a tabela seria mentira.

        O que ela confere e a coincidencia entre DUAS leituras independentes:
        o `8`/`-2` saiu do `0x004097d4` e o `8`/`5`/`7` do
        `rectanguloDragOver`. Trocar uma das duas derruba -- e e isso que este
        teste exercita.
        """
        for b in range(256):
            self.assertEqual(F.destino_x(b) % F.PASSO_X,
                             (F.FASE_X - F.RAIO) % F.PASSO_X, b)
            self.assertEqual(F.destino_y(b) % F.PASSO_Y,
                             (-F.RAIO) % F.PASSO_Y, b)

        fase = F.FASE_X
        F.FASE_X = fase + 1          # como se o arrasto tivesse outra fase
        self.addCleanup(setattr, F, "FASE_X", fase)
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("grade do arrasto", str(e.exception))

    def test_default_com_dado_derruba_a_isencao(self):
        """A isencao do registro 1 nao pode cobrir um registro de verdade."""
        self.formacoes[F.FORMACAO_DEFAULT]["x"][3] = 9
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("deixou de ser zero", str(e.exception))

    def test_ordem_trocada_derruba_pelo_nome(self):
        """Trocar dois registros mantem as quatro faixas e quebra a contagem.

        O par e escolhido pelo NOME, e nao por indice fixo: dois `4 - 5 - 1`
        trocados entre si nao mudariam a contagem, e o teste passaria sem
        exercitar nada.
        """
        nomes = F.nomes_da_lista()
        def conta(n):
            import re
            d = re.findall(r"\d", n)
            return tuple(d) if len(d) == 3 else None
        par = None
        for i in range(F.FORMACOES):
            for j in range(i + 1, F.FORMACOES):
                if conta(nomes[i]) and conta(nomes[j]) \
                        and conta(nomes[i]) != conta(nomes[j]):
                    par = (i, j)
                    break
            if par:
                break
        self.assertIsNotNone(par, "sem duas formacoes de contagem diferente")
        a, b = par
        self.formacoes[a], self.formacoes[b] = \
            self.formacoes[b], self.formacoes[a]
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("nao e a da lista", str(e.exception))

    def test_coluna_errada_derruba_pelo_nome(self):
        """Ler a coluna de zona achando que e a de papel."""
        for f in self.formacoes:
            f["papel"] = list(f["zona"])
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, self.passo)
        self.assertIn("papeis contam", str(e.exception))

    def test_passo_diferente_derruba(self):
        with self.assertRaises(F.DumpError) as e:
            F.confere(self.formacoes, 0.25)
        self.assertIn("esperava 0.2", str(e.exception))


class TestFormulas(unittest.TestCase):
    def test_destino_x(self):
        self.assertEqual(F.destino_x(0), -2)
        self.assertEqual(F.destino_x(43), 342)

    def test_destino_y_trunca_para_zero_como_o_idiv(self):
        """`y = 0` da -12, nao -17: `idiv` trunca para zero e o Python nao."""
        self.assertEqual(F.destino_y(0), -12)
        self.assertEqual(F.destino_y(3), -7)
        self.assertEqual(F.destino_y(87), 203)

    def test_o_destino_cai_na_grade_do_arrasto(self):
        for x in range(0, 44):
            self.assertEqual(F.destino_x(x) % F.PASSO_X,
                             (F.FASE_X - F.RAIO) % F.PASSO_X, x)

    def test_long_double(self):
        self.assertAlmostEqual(
            F.long_double(bytes.fromhex("00d0cccccccccccc" "fc3f")), 0.2, 12)
        self.assertAlmostEqual(
            F.long_double(bytes.fromhex("0000000000000080" "ff3f")), 1.0, 12)

    def test_long_double_recusa_tamanho_errado(self):
        with self.assertRaises(F.DumpError):
            F.long_double(b"\x00" * 8)


if __name__ == "__main__":
    unittest.main()
