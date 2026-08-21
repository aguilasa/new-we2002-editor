#!/usr/bin/env python3
"""Testes do dump_render2d.py -- WTE-TASK-29.

Tres grupos, e o do meio e a razao de o arquivo existir:

1. **O que se le do `.exe` bate com o que o markdown afirma.** Cada assinatura
   da tabela `ASSINATURAS` e um padrao de instrucao; se algum deixar de
   aparecer, o gerador tem de recusar em vez de emitir prosa que caducou.
2. **As recusas foram VISTAS.** Guard que nunca foi visto recusar e guard que
   se supoe funcionar -- a mesma politica do `test_dump_mcr.py`. Aqui a
   plantacao e no proprio blob em memoria, porque o `.exe` e leitura pura e
   nao se edita nem em teste.
3. **A aritmetica que o markdown descreve, executada.** O documento afirma como
   o gradiente e o escurecer se comportam; o teste reimplementa as duas contas
   em Python e prova o que elas produzem -- inclusive o caso em que truncar e
   arredondar DIVERGEM, que e o risco nomeado da §9 do plano.
"""

from __future__ import annotations

import math
import unittest
from pathlib import Path

import dump_render2d as R


class TestAssinaturas(unittest.TestCase):
    """Cada afirmacao do markdown, contra o `.text`."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE} -- as assinaturas NAO foram "
                          "conferidas")
        self.blob = R.EXE.read_bytes()

    def test_todas_as_assinaturas_aparecem(self) -> None:
        provas = R.confere_assinaturas(self.blob)
        self.assertEqual(len(provas), len(R.ASSINATURAS))

    def test_a_expansao_e_deslocamento_e_o_teto_confirma(self) -> None:
        """`shl 3` e `cmp 0xf8` sao a mesma afirmacao, vista de dois lados.

        Se a expansao fosse `v * 255 / 31`, o teto do clarear seria `0xFF`. E
        `0xF8`, entao e deslocamento. Os dois padroes tem de coexistir.
        """
        decodifica = R.le_bytes(self.blob, R.VA_DECODIFICA, 0x9A)
        clarear = R.le_bytes(self.blob, R.VA_CLAREAR, 0x45)
        self.assertIn(bytes.fromhex("c02203"), decodifica)
        self.assertIn(bytes.fromhex("807d00f8"), clarear)
        self.assertEqual(31 << 3, 0xF8)

    def test_o_arredondador_trunca(self) -> None:
        """RC = `11` nos bits 10-11 do control word e *round toward zero*."""
        corpo = R.le_bytes(self.blob, R.VA_TRUNCA, 0x2C)
        self.assertIn(bytes.fromhex("814dfc010c0000"), corpo)
        # 0xc01 = 0b1100_0000_0001: PC em `11` (extendido) e RC em `11`.
        self.assertEqual((0xC01 >> 10) & 0b11, 0b11)

    def test_os_tres_passos_sao_os_tres_campos(self) -> None:
        """`1`, `0x20` e `0x400` sao um degrau em cada campo de 5 bits."""
        self.assertEqual(1, 1 << 0)
        self.assertEqual(0x20, 1 << 5)
        self.assertEqual(0x400, 1 << 10)

    def test_o_exportador_pula_o_resto_do_setor(self) -> None:
        self.assertEqual(R.SETOR_PAYLOAD + R.SETOR_RESTO, R.SETOR_BYTES)


class TestRecusa(unittest.TestCase):
    """As recusas, vistas. O `.exe` nao se edita -- planta-se no blob."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE}")
        self.blob = R.EXE.read_bytes()

    def _planta(self, va: int, quantos: int) -> bytes:
        """Zera `quantos` bytes a partir de `va`, no blob em memoria."""
        for sec_va, tam, roff in R.secoes(self.blob):
            ini = 0x00400000 + sec_va
            if ini <= va < ini + tam:
                pos = roff + (va - ini)
                return (self.blob[:pos] + bytes(quantos)
                        + self.blob[pos + quantos:])
        raise AssertionError(f"{va:#x} fora de toda secao")

    def test_assinatura_apagada_recusa(self) -> None:
        plantado = self._planta(R.VA_TRUNCA, 0x2C)
        with self.assertRaises(R.RenderError) as ctx:
            R.confere_assinaturas(plantado)
        self.assertIn(f"{R.VA_TRUNCA:#010x}", str(ctx.exception))

    def test_desenhista_alterado_recusa(self) -> None:
        plantado = self._planta(R.VA_UNIFORME, 0x40A)
        with self.assertRaises(R.RenderError) as ctx:
            R.confere_desenhistas(plantado)
        self.assertIn(f"{R.VA_UNIFORME:#010x}", str(ctx.exception))

    def test_va_fora_de_secao_recusa(self) -> None:
        with self.assertRaises(R.RenderError):
            R.le_bytes(self.blob, 0x7FFFFFFF, 4)


class TestDesenhistas(unittest.TestCase):
    """A assimetria entre bandeira e uniforme -- o achado desta passagem."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE}")
        self.blob = R.EXE.read_bytes()

    def test_bandeira_e_uniforme_nao_reescrevem_o_mesmo_tanto(self) -> None:
        achados = {papel: (entradas, arquivos)
                   for _, papel, entradas, arquivos
                   in R.confere_desenhistas(self.blob)}
        self.assertEqual(achados["bandeira do titular"], (16, 1))
        self.assertEqual(achados["camisa e calcao"], (15, 2))

    def test_o_seek_cai_no_fim_do_cabecalho(self) -> None:
        """`0x36` so e a primeira entrada de paleta se o cabecalho tiver 54."""
        self.assertEqual(R.BMP_CABECALHO, 0x36)


class TestBitmaps(unittest.TestCase):
    def setUp(self) -> None:
        if not R.IMAGEM.is_dir():
            self.skipTest("sem we-team-editor/image -- os bitmaps NAO foram "
                          "contados")
        self.contas = R.bitmaps()

    def test_nenhum_bitmap_foge_de_oito_bpp(self) -> None:
        # Um so de 24 bpp quebraria o `0x36` -- o cabecalho teria outro
        # tamanho e o seek cairia no meio do pixel.
        self.assertEqual(self.contas["fora"], 0)

    def test_as_familias_do_render_estao_todas_la(self) -> None:
        for chave in ("bandeiras", "camisas", "calcoes"):
            self.assertGreater(self.contas[chave], 0, chave)


class TestAritmetica(unittest.TestCase):
    """A conta que o markdown descreve, executada.

    Nao le o `.exe`: prova que a DESCRICAO e coerente e que a forma errada de
    escreve-la produz outro resultado. Sem isto, "trunca em vez de arredondar"
    seria uma frase.
    """

    @staticmethod
    def expande(v5: int) -> int:
        return v5 << 3

    @staticmethod
    def decodifica(palavra: int) -> tuple[int, int, int]:
        return ((palavra >> 0) & 0x1F, (palavra >> 5) & 0x1F,
                (palavra >> 10) & 0x1F)

    def escurece(self, palavra: int) -> int:
        r, g, b = (self.expande(c) for c in self.decodifica(palavra))
        if r > 0:
            palavra -= 1
        if g > 0:
            palavra -= 0x20
        if b > 0:
            palavra -= 0x400
        return palavra

    def clareia(self, palavra: int) -> int:
        r, g, b = (self.expande(c) for c in self.decodifica(palavra))
        if r < 0xF8:
            palavra += 1
        if g < 0xF8:
            palavra += 0x20
        if b < 0xF8:
            palavra += 0x400
        return palavra

    def test_um_degrau_mexe_num_campo_de_cada_vez(self) -> None:
        palavra = (10 << 10) | (20 << 5) | 30
        self.assertEqual(self.decodifica(self.escurece(palavra)), (29, 19, 9))
        self.assertEqual(self.decodifica(self.clareia(palavra)), (31, 21, 11))

    def test_o_piso_segura_e_nao_da_a_volta(self) -> None:
        """Sem a guarda, `0 - 1` viraria `31` no campo vizinho."""
        self.assertEqual(self.escurece(0), 0)
        self.assertEqual(self.decodifica(self.escurece(1 << 5)), (0, 0, 0))

    def test_o_teto_satura_em_trinta_e_um(self) -> None:
        cheio = (31 << 10) | (31 << 5) | 31
        self.assertEqual(self.clareia(cheio), cheio)

    @staticmethod
    def rampa(inicio: tuple[int, int, int], fim: tuple[int, int, int],
              n: int, arredonda) -> list[int]:
        """A rampa do `gradienteClick`, com o conversor recebido de fora.

        A soma e sobre a PALAVRA de partida, e nao canal a canal -- e assim que
        o original faz, e a diferenca aparece quando o conversor muda.
        """
        palavra_inicial = inicio[0] | (inicio[1] << 5) | (inicio[2] << 10)
        passo = [(fim[c] - inicio[c]) / n for c in range(3)]
        acumulado = [0.0, 0.0, 0.0]
        saida = []
        for _ in range(n):
            for c in range(3):
                acumulado[c] += passo[c]
            saida.append(palavra_inicial + arredonda(acumulado[0])
                         + (arredonda(acumulado[1]) << 5)
                         + (arredonda(acumulado[2]) << 10))
        return saida

    def test_truncar_e_arredondar_divergem_na_rampa(self) -> None:
        """O risco nomeado da §9, executado.

        Se as duas formas dessem sempre o mesmo, a escolha nao importaria e o
        plano teria errado ao chamar isso de risco. Elas divergem.
        """
        truncada = self.rampa((0, 0, 0), (7, 0, 0), 5, math.trunc)
        arredondada = self.rampa((0, 0, 0), (7, 0, 0), 5,
                                 lambda x: int(x + 0.5))
        self.assertNotEqual(truncada, arredondada)
        # E a divergencia e de um degrau, exatamente o que o plano previu.
        for a, b in zip(truncada, arredondada):
            self.assertLessEqual(abs(a - b), 1)

    def test_a_rampa_chega_na_ponta(self) -> None:
        n = 8
        rampa = self.rampa((0, 0, 0), (24, 0, 0), n, math.trunc)
        self.assertEqual(rampa[-1] & 0x1F, 24)


if __name__ == "__main__":
    unittest.main()
