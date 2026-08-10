#!/usr/bin/env python3
"""Testes do check_fase3.py -- WTE-TASK-21.

O que se mede aqui e a **conta da fracao gerada**, porque ela e a afirmacao da
task: se o denominador ou o numerador escorregar, o fechamento publica um numero
que ninguem consegue refazer -- que e o defeito que a CORR-WTE-012, a -014 e a
-023 pegaram, sempre em contagem de doc.

Dois grupos:

1. as guardas, com entrada plantada -- bloco manual que sumiu da saida, e o
   dedupe da constante alcancada por dois caminhos;
2. a arvore de verdade -- os oito `.pas` da camada, os consumidores e o Ghidra.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_fase3 as C


class TestConfereBloco(unittest.TestCase):
    """A guarda que impede a fracao de contar codigo que nao existe."""

    def arquivo(self, tmp: Path, texto: str) -> Path:
        p = tmp / "saida.pas"
        p.write_text(texto, encoding="utf-8")
        return p

    def test_bloco_presente_conta_as_linhas_uteis(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            alvo = self.arquivo(Path(d), "unit x;\n  begin\n  Foo;\n  end;\n")
            # A linha em branco do bloco nao conta -- ela nao e codigo.
            self.assertEqual(C.confere_bloco(alvo, "begin\n\nFoo;\n", "b"), 2)

    def test_indentacao_diferente_ainda_casa(self) -> None:
        """O gerador reindenta o que poe dentro de `implementation`."""
        with tempfile.TemporaryDirectory() as d:
            alvo = self.arquivo(Path(d), "        Foo;\n")
            self.assertEqual(C.confere_bloco(alvo, "Foo;\n", "b"), 1)

    def test_bloco_que_sumiu_da_saida_aborta(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            alvo = self.arquivo(Path(d), "unit x;\nend.\n")
            with self.assertRaises(C.CheckError) as e:
                C.confere_bloco(alvo, "procedure Sumida;\n", "rota 3")
            self.assertIn("rota 3", str(e.exception))


class TestBlocosManuais(unittest.TestCase):

    def test_nenhum_texto_repetido_na_mesma_unidade(self) -> None:
        """O dedupe que corrigiu 320 linhas a mao para 277.

        `MANUAL_TIPOS["we2002_types"]` **e** `MANUAL_TYPES.interface` -- o
        gerador reusa a constante em vez de copiar o texto, e somar os dois
        caminhos contava o mesmo Pascal duas vezes.
        """
        for unidade, itens in C.blocos_manuais().items():
            textos = [t for _, t in itens]
            self.assertEqual(len(textos), len(set(textos)),
                             f"{unidade}: bloco manual contado duas vezes")

    def test_ha_bloco_manual_em_types_e_cdimage(self) -> None:
        """As duas pecas da rota 3 que o `tipos.md` decidiu: bitfield e fstream.

        Se isto ficar vazio, ou o gerador parou de emitir porte a mao -- e a
        fracao viraria 100% por engano -- ou as constantes mudaram de nome.
        """
        manuais = C.blocos_manuais()
        self.assertTrue(manuais.get("we2002_types"))
        self.assertTrue(manuais.get("we2002_cdimage"))


class TestArvoreReal(unittest.TestCase):
    """Contra a camada de dados commitada."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.frac = C.fracao_gerada()

    def test_os_oito_arquivos_da_camada_existem_e_sao_gerados(self) -> None:
        self.assertEqual(len(self.frac["por_arquivo"]), len(C.DA_CAMADA))

    def test_a_mao_nunca_passa_do_total_de_nenhum_arquivo(self) -> None:
        for nome, _, total, mao in self.frac["por_arquivo"]:
            self.assertLessEqual(mao, total, nome)

    def test_a_maior_parte_e_transpilacao(self) -> None:
        """A tese da §4.5, presa em teste.

        Nao e o numero exato -- ele muda quando o core muda --, e sim o sentido:
        se a fracao por regra cair abaixo da metade, a fase 3 virou porte
        manual e o plano precisa dizer isso em vez de fingir que nao.
        """
        self.assertGreater(self.frac["regra"], self.frac["total"] / 2)
        self.assertGreater(self.frac["mao"], 0,
                           "zero linha a mao significa que a rota 3 sumiu")

    def test_a_entrada_do_transpilador_e_a_do_plano(self) -> None:
        entrada, total = C.entrada_do_transpilador()
        self.assertEqual(len(entrada), 11)
        self.assertGreater(total, 2000)

    def test_so_teste_consome_a_camada(self) -> None:
        """A resposta a "o app ja le o jogo?", e ela e medida, nao opinada.

        Quando a integracao minima entrar (WTE-TASK-25), este teste passa a
        falhar -- e e o comportamento certo: o `fase-3-fechamento.md` afirma o
        contrario, e teria de ser regerado junto.
        """
        casca, teste = C.consumidores()
        self.assertEqual(casca, [])
        self.assertTrue(teste)

    def test_os_artefatos_de_medida_da_fase_3_nao_citam_ghidra(self) -> None:
        citando = {nome for nome, _, _ in C.ghidra_na_fase_3()}
        for artefato in ("tipos.md", "transpilador.md", "recusas.md",
                         "fase-3.md", "offsets-novos.md"):
            self.assertNotIn(artefato, citando)


if __name__ == "__main__":
    unittest.main()
