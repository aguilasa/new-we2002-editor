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

    def test_bloco_presente_casa_por_linha_util_e_conta_todas(self) -> None:
        """As duas reguas de `confere_bloco()`, separadas pela CORR-WTE-051.

        O bloco tem 3 linhas fisicas e 2 uteis. O casamento usa as 2 -- linha
        vazia casaria com qualquer coisa --, e a contagem devolve as 3, porque
        a linha em branco foi escrita a mao, sai emitida junto, e o total do
        arquivo tambem a conta. Devolver 2 aqui era o que creditava branco de
        bloco manual a coluna *por regra*.
        """
        with tempfile.TemporaryDirectory() as d:
            alvo = self.arquivo(Path(d), "unit x;\n  begin\n  Foo;\n  end;\n")
            self.assertEqual(C.confere_bloco(alvo, "begin\n\nFoo;\n", "b"), 3)

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

    def test_as_tres_colunas_usam_a_mesma_regua(self) -> None:
        """A subtracao so vale entre contagens comensuraveis.

        A versao publicada fazia `total com branco - manual sem branco`, e as
        26 linhas em branco dos blocos manuais viravam *por regra*
        (CORR-WTE-051). Aqui se reconta a coluna **a mao** por fora, com a
        regua do total, e se exige o mesmo numero.
        """
        manuais = C.blocos_manuais()
        mao = sum(len(texto.splitlines())
                  for lista in manuais.values() for _, texto in lista)
        self.assertEqual(self.frac["mao"], mao)
        self.assertEqual(self.frac["regra"],
                         self.frac["total"] - self.frac["mao"])

    def test_a_contagem_do_bloco_inclui_a_linha_em_branco(self) -> None:
        """A regua da contagem, presa em teste, com bloco plantado.

        Se `confere_bloco()` voltar a devolver o numero do casamento, este
        teste reprova: o bloco tem 3 linhas fisicas e 2 uteis.
        """
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "u.pas"
            alvo.write_text("begin\n\n  x := 1;\nend;\n", encoding="utf-8")
            n = C.confere_bloco(alvo, "begin\n\n  x := 1;", "plantado")
        self.assertEqual(n, 3)

    def test_a_entrada_do_transpilador_e_a_do_plano(self) -> None:
        entrada, total = C.entrada_do_transpilador()
        self.assertEqual(len(entrada), 11)
        self.assertGreater(total, 2000)

    def test_todo_gerador_da_saida_tem_entrada_no_denominador(self) -> None:
        """A razao so diz alguma coisa entre populacoes que se correspondem.

        A versao publicada dividia a saida dos DOIS geradores (3692) pela
        entrada de um so (2504, o `UNITS`), creditando ao transpilador as 708
        linhas do `gen_tables_pas.py` (CORR-WTE-050). Aqui se prende o
        pareamento: gerador que aparece em `DA_CAMADA` tem de ter entrada.
        """
        entrada = C.entrada_por_gerador()
        self.assertEqual(set(entrada), set(C.DA_CAMADA.values()))
        C.conferir_entradas(entrada)          # nao levanta

    def test_gerador_sem_entrada_aborta(self) -> None:
        """Plantado: um terceiro gerador na saida e nada no denominador."""
        entrada = C.entrada_por_gerador()
        original = dict(C.DA_CAMADA)
        try:
            C.DA_CAMADA["we2002_inventado.pas"] = "gerador_novo.py"
            with self.assertRaises(C.CheckError) as ctx:
                C.conferir_entradas(entrada)
        finally:
            C.DA_CAMADA.clear()
            C.DA_CAMADA.update(original)
        self.assertIn("gerador_novo.py", str(ctx.exception))

    def test_a_entrada_de_tabelas_e_lida_do_proprio_gerador(self) -> None:
        """Nao e lista copiada: sao as constantes do `gen_tables_pas.py`.

        Copiar os tres caminhos para ca criaria a segunda copia que envelhece
        sozinha -- o defeito que o `blocos_manuais()` ja evita lendo o
        `port_database_pas`.
        """
        import gen_tables_pas as G
        self.assertEqual(C.entrada_de_tabelas(),
                         [G.TABLES_CPP, G.TABLES_HPP, G.OFFSETS_HPP])

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
