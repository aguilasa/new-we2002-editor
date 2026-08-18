#!/usr/bin/env python3
"""Testes do `dump_zonas.py`: a varredura e as quatro conferencias.

O script decodifica 44 imediatos escritos em ordem embaralhada -- o compilador
intercala `lea` de ponteiro com `mov` de deslocamento, e o primeiro campo de
cada registro sai por um registrador auxiliar. O modo de errar e mudo: um
ponteiro resolvido para o lugar errado troca um `x2` por um `y1` e produz um
retangulo plausivel.

Os testes montam um `FormCreate` sintetico num PE de mentira e rodam num clone
sem a pasta `we-team-editor/`. A medicao contra o binario de verdade fica sob
`skipUnless`, como nos irmaos.
"""

from __future__ import annotations

import struct
import unittest

import dump_zonas as Z

REAL = Z.EXE.is_file()

BASE_PE = 0x00400000
TEXT_VA = 0x00401000
DATA_VA = 0x00433000
DATA_TAM = 0x2000
TEXT_TAM = DATA_VA - TEXT_VA


class PEFalso:
    def __init__(self, text: bytes) -> None:
        self.base = BASE_PE
        self.text = text.ljust(TEXT_TAM, b"\x90")
        self.dados = bytes(DATA_TAM)
        self.data = self.text + self.dados
        self.sections = [
            (".text", TEXT_VA - BASE_PE, len(self.text), 0, len(self.text)),
            (".data", DATA_VA - BASE_PE, DATA_TAM, len(self.text), DATA_TAM),
        ]

    def off(self, va: int) -> int | None:
        if TEXT_VA <= va < TEXT_VA + len(self.text):
            return va - TEXT_VA
        if DATA_VA <= va < DATA_VA + DATA_TAM:
            return len(self.text) + (va - DATA_VA)
        return None


def _mov_ebx(valor: int) -> bytes:
    return b"\xbb" + struct.pack("<I", valor)


def _mov_disp32(disp: int, valor: int) -> bytes:
    return b"\xc7\x83" + struct.pack("<i", disp) + struct.pack("<I", valor)


def _lea_eax(disp: int) -> bytes:
    return b"\x8d\x83" + struct.pack("<i", disp)


def _mov_via_eax(valor: int) -> bytes:
    return b"\xc7\x00" + struct.pack("<I", valor)


def corpo(zonas, base=Z.BASE, via_ponteiro=True, pula=None) -> PEFalso:
    """Um `FormCreate` sintetico que escreve `zonas` como o original escreve.

    O primeiro campo de cada registro sai pelo ponteiro auxiliar e os outros
    tres pelo deslocamento -- que e a forma que o compilador emitiu e a que o
    decodificador tem de acertar.
    """
    bs = bytearray(b"\x90" * (Z.INI - TEXT_VA))
    bs += _mov_ebx(base)
    for i, quatro in enumerate(zonas):
        for c, valor in enumerate(quatro):
            disp = i * Z.PASSO + c * 4
            if pula is not None and disp == pula:
                continue
            if c == 0 and via_ponteiro:
                bs += _lea_eax(disp)
                bs += _mov_via_eax(valor)
            else:
                bs += _mov_disp32(disp, valor)
    return PEFalso(bytes(bs))


def onze(x1=10, y1=3, x2=129, y2=82):
    return [(x1, y1, x2, y2)] * Z.bolas()


class TestVarredura(unittest.TestCase):
    def test_le_os_quatro_campos_de_cada_registro(self):
        esperado = [(10 + i, 3, 129, 82) for i in range(Z.bolas())]
        self.assertEqual(Z.confere(Z.varre(corpo(esperado))), esperado)

    def test_o_ponteiro_auxiliar_nao_desloca_o_registro(self):
        """Com e sem ponteiro auxiliar o resultado tem de ser o mesmo.

        E a conferencia central: seguir `lea eax,[ebx+disp]` errado desloca o
        primeiro campo de todo registro sem deixar buraco.
        """
        z = [(10 + i, 3, 129, 82) for i in range(Z.bolas())]
        self.assertEqual(Z.varre(corpo(z, via_ponteiro=True)),
                         Z.varre(corpo(z, via_ponteiro=False)))


class TestConferencias(unittest.TestCase):
    def _erro(self, pe) -> str:
        with self.assertRaises(Z.DumpError) as ctx:
            Z.confere(Z.varre(pe))
        return str(ctx.exception)

    def test_base_errada_reprova(self):
        with self.assertRaises(Z.DumpError) as ctx:
            Z.varre(corpo(onze(), base=0x00433000))
        self.assertIn("ebx medido", str(ctx.exception))

    def test_campo_faltando_reprova(self):
        self.assertIn("perdeu uma", self._erro(corpo(onze(), pula=8)))

    def test_contagem_diferente_das_bolas_reprova(self):
        self.assertIn("`bolaN`", self._erro(corpo(onze()[:-1])))

    def test_retangulo_fora_do_campo_reprova(self):
        z = onze()
        z[3] = (10, 3, 9999, 82)
        self.assertIn("nao cabe no campo", self._erro(corpo(z)))

    def test_retangulo_invertido_reprova(self):
        z = onze()
        z[5] = (129, 3, 10, 82)
        self.assertIn("nao cabe no campo", self._erro(corpo(z)))


@unittest.skipUnless(REAL, "we-team-editor/we-team-editor.exe nao esta no disco")
class TestReal(unittest.TestCase):
    def setUp(self):
        pe = Z.PE(Z.EXE.read_bytes(), Z.REL_EXE)
        self.zonas = Z.confere(Z.varre(pe))

    def test_uma_zona_por_bola(self):
        self.assertEqual(len(self.zonas), Z.bolas())

    def test_as_zonas_se_alinham_em_quatro_colunas(self):
        """Os `x1` distintos sao QUATRO, e a distincao vale a medicao.

        Escrevi tres primeiro -- defesa, meio e ataque -- e o teste reprovou:
        alem de 10, 122 e 274 ha uma quarta coluna em 170, um meio-campo
        adiantado mais estreito. O numero certo e o medido; o palpite bonito
        era o errado.

        O que o teste segura nao e a estetica da tabela: e o alinhamento. Uma
        tabela deslocada por um campo traria `x1` vindo da coluna `y1`, e a
        contagem de colunas explodiria para o numero de linhas.
        """
        self.assertEqual(sorted({z[0] for z in self.zonas}),
                         [10, 122, 170, 274])

    def test_nenhuma_zona_e_degenerada(self):
        for i, (x1, y1, x2, y2) in enumerate(self.zonas):
            self.assertGreater(x2 - x1, 50, f"zona {i} estreita demais")
            self.assertGreater(y2 - y1, 50, f"zona {i} baixa demais")


if __name__ == "__main__":
    unittest.main()
