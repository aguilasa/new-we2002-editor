#!/usr/bin/env python3
"""Testes do check_fase4.py -- WTE-TASK-31.

O que se mede aqui sao as duas leituras que o fechamento faz e que ninguem
conferiria sozinho:

1. **quem grava na imagem**, lido da primeira linha de `## Bytes tocados`. Essa
   linha e prosa escrita a mao em 94 arquivos, e a conta de gravacoes do
   fechamento inteiro sai dela -- uma frase nova de "nao grava" que o leitor nao
   reconhecesse faria a conta subir em silencio, que e o defeito que a
   CORR-WTE-012, a -014 e a -023 pegaram sempre em contagem de doc;
2. **quais cinco `trivial` sao reamostrados**. A regra tem de ser reproduzivel
   (senao o `--check` nunca casa) e tem de se deslocar quando a populacao muda
   (senao a reconferencia envelhece apontando para handler que saiu do grupo).

Os testes montam a entrada em memoria: nao abrem o `.exe`, nao precisam de
`DISPLAY` nem de Wine, e rodam num clone sem a pasta `we-team-editor/`.
"""

from __future__ import annotations

import re
import unittest

import check_fase4 as C


class TestPrimeiraLinha(unittest.TestCase):
    """A leitura pula o que nao e resposta."""

    def test_pula_vazio_e_cerca_de_bloco(self) -> None:
        """A `boton_tex2isoClick` abre a secao com um bloco de codigo.

        A cerca nao e a resposta -- a linha seguinte e. Antes desta regra o
        fechamento abortava dizendo que a secao estava vazia, e a secao tem
        onze linhas.
        """
        corpo = "\n```text\noffset = 19756824 + 47040 * i\n```\n"
        self.assertEqual(C.normaliza_primeira_linha(corpo),
                         "offset = 19756824 + 47040 * i")

    def test_tira_enfase_e_baixa_a_caixa(self) -> None:
        self.assertEqual(C.normaliza_primeira_linha("**Nenhum.**"), "nenhum.")
        self.assertEqual(C.normaliza_primeira_linha("`Nenhum`"), "nenhum")

    def test_secao_so_com_cerca_devolve_vazio(self) -> None:
        self.assertEqual(C.normaliza_primeira_linha("\n```\n```\n"), "")


class TestGravaNaImagem(unittest.TestCase):
    """A conta de gravacoes do fechamento inteiro sai daqui."""

    def test_nenhum_nao_grava(self) -> None:
        self.assertFalse(C.grava_na_imagem("x.y", "**Nenhum.**"))

    def test_nenhum_qualificado_tambem_nao(self) -> None:
        """`grabar_memoryClick` emite um `.mcr` e deixa a ROM intacta."""
        self.assertFalse(
            C.grava_na_imagem("x.y", "**Nenhum na imagem de CD.** Medido: ..."))
        self.assertFalse(
            C.grava_na_imagem("x.y", "**Na imagem de CD: nenhum.** Ela e ..."))

    def test_qualquer_outra_coisa_grava(self) -> None:
        self.assertTrue(
            C.grava_na_imagem("x.y", "Sete regioes por time, todas ..."))

    def test_secao_vazia_aborta(self) -> None:
        with self.assertRaises(C.Fase4Error) as ctx:
            C.grava_na_imagem("x.y", "\n\n")
        self.assertIn("vazia", str(ctx.exception))

    def test_forma_nova_de_nao_gravar_aborta_em_vez_de_contar(self) -> None:
        """O ponto do teste, e a razao de a guarda existir.

        Uma spec nova que escrevesse "Nenhum byte da imagem" seria classificada
        como GRAVACAO pela regra de prefixo -- e a tabela de gates ganharia um
        handler que nao grava, ou perderia um que grava. Abortar poe o erro na
        cara de quem escreveu a frase, no dia em que ele a escreveu.
        """
        with self.assertRaises(C.Fase4Error) as ctx:
            C.grava_na_imagem("x.y", "Byte nenhum, em lugar nenhum.")
        self.assertIn("NAO_GRAVA", str(ctx.exception))


class TestCincoTrivial(unittest.TestCase):
    """A amostra e reproduzivel, espacada, e se desloca com a populacao."""

    def amostra(self, n: int) -> list[str]:
        triviais = [{"endereco": f"0x{i:08x}", "handler": f"f.h{i}"}
                    for i in range(n)]
        return [x["handler"] for x in C.cinco_trivial(triviais)]

    def test_pega_as_duas_pontas_e_espaca_o_meio(self) -> None:
        """Com 19 -- a populacao real no fechamento -- sao estes cinco."""
        self.assertEqual(self.amostra(19),
                         ["f.h0", "f.h4", "f.h9", "f.h14", "f.h18"])

    def test_e_deterministica(self) -> None:
        self.assertEqual(self.amostra(19), self.amostra(19))

    def test_desloca_quando_a_populacao_muda(self) -> None:
        """Handler novo em `trivial` muda quais sao os cinco.

        E o que faz o gerador abortar se o registro da reconferencia nao
        acompanhar -- reconferencia velha nao vale para handler novo.
        """
        self.assertNotEqual(self.amostra(19), self.amostra(20))

    def test_nunca_repete_o_mesmo_handler(self) -> None:
        for n in range(5, 40):
            with self.subTest(n=n):
                self.assertEqual(len(set(self.amostra(n))), len(self.amostra(n)))

    def test_populacao_curta_demais_aborta(self) -> None:
        with self.assertRaises(C.Fase4Error):
            self.amostra(4)


class TestFormaAposentada(unittest.TestCase):
    """A guarda da CORR-WTE-085: `seis`/`nove gravacoes` em linha viva."""

    def test_a_forma_velha_e_pega(self) -> None:
        self.assertTrue(any(
            re.search(f, "duas das seis gravações do editor", re.I)
            for f in C.FORMAS_APOSENTADAS))
        self.assertTrue(any(
            re.search(f, "as nove gravações da fase 4", re.I)
            for f in C.FORMAS_APOSENTADAS))

    def test_o_digito_solto_nao_e_alvo(self) -> None:
        """`6` e `9` sozinhos dariam falso positivo em qualquer pagina."""
        self.assertFalse(any(
            re.search(f, "as 6 gravações medidas", re.I)
            for f in C.FORMAS_APOSENTADAS))

    def test_a_forma_velho_para_corrente_e_perdoada(self) -> None:
        """`seis -> dezessete` ensina; `seis` sozinho mente."""
        self.assertTrue(C._diz_o_corrente(
            "de seis gravações para dezessete", 17))
        self.assertTrue(C._diz_o_corrente("seis gravações viraram 17", 17))
        self.assertFalse(C._diz_o_corrente("duas das seis gravações", 17))


class TestMarcasDeDecompilado(unittest.TestCase):
    """A varredura daqui e mais estreita que a do `spec_index.py`."""

    def casa(self, texto: str) -> bool:
        return any(m.search(texto) for m, _ in C.MARCAS)

    def test_pega_o_que_o_ghidra_inventa(self) -> None:
        for trecho in ("undefined4 x;", "uVar1 = 3;", "local_1c",
                       "param_1", "DAT_00423abc", "__fastcall foo",
                       "(int)*(int *)(this + 8)"):
            with self.subTest(trecho=trecho):
                self.assertTrue(self.casa(trecho))

    def test_deixa_passar_undefined_sem_digito(self) -> None:
        """A diferenca contra o `spec_index.py`, e ela e deliberada.

        Esta varredura alcanca `.pas` e `.inc`, e o `we2002_types.pas` tem
        `undefined behaviour, not a behaviour` num comentario -- prosa inglesa,
        nao saida de decompilador. O custo esta escrito no cabecalho do
        gerador: um `undefined` de Ghidra sem digito passaria.
        """
        self.assertFalse(self.casa("undefined behaviour, not a behaviour"))


if __name__ == "__main__":
    unittest.main()
