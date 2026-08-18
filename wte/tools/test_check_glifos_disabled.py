#!/usr/bin/env python3
"""Testes do `check_glifos_disabled.py`, com BMP plantado em memoria.

O script mede a arvore de verdade, entao o teste que importa nao e "o numero
de hoje continua o de hoje" -- e **as guardas disparam**. Guarda nunca
exercitada e guarda ausente: foi o que a CORR-WTE-020 achou no `dfm2lfm.py`, e
o que a CORR-WTE-060 nao quer repetir no proprio conferidor.

Os BMPs sao montados aqui, 24 bpp `BI_RGB` bottom-up, porque e o unico formato
que os 18 formularios do C++Builder 6 trazem -- e o script **aborta** em vez de
adivinhar diante de qualquer outro, o que tambem e testado.
"""

from __future__ import annotations

import struct
import unittest
from pathlib import Path

import check_glifos_disabled as mod


def bmp(pixels: list[tuple[int, int, int]], larg: int) -> bytes:
    """Monta um BMP 24 bpp bottom-up. `pixels` vem da base para o topo."""
    alt = len(pixels) // larg
    passo = (larg * 3 + 3) // 4 * 4
    dados = b""
    for y in range(alt):
        linha = b"".join(bytes(p) for p in pixels[y * larg:(y + 1) * larg])
        dados += linha + b"\x00" * (passo - len(linha))
    inicio = 14 + 40
    cab = b"BM" + struct.pack("<IHHI", inicio + len(dados), 0, 0, inicio)
    info = struct.pack("<IiiHHIIiiII", 40, larg, alt, 1, 24, 0, len(dados),
                       0, 0, 0, 0)
    return cab + info + dados


PRETO, BRANCO, FUNDO, LARANJA = (0, 0, 0), (255, 255, 255), (255, 182, 118), \
    (1, 134, 255)


class TestDecodificador(unittest.TestCase):
    def test_transparente_e_o_inferior_esquerdo(self):
        # Primeiro pixel do arquivo = canto inferior esquerdo, num bottom-up.
        pix, transp = mod.pixels_bmp(bmp([FUNDO, PRETO, BRANCO, FUNDO], 2))
        self.assertEqual(transp, bytes(FUNDO))
        self.assertEqual(len(pix), 4)

    def test_so_preto_e_branco_sobre_transparente_da_zero(self):
        self.assertEqual(
            mod.nao_cinza_desenhados(bmp([FUNDO, PRETO, BRANCO, FUNDO], 2)), 0)

    def test_pixel_colorido_conta(self):
        self.assertEqual(
            mod.nao_cinza_desenhados(bmp([FUNDO, LARANJA, PRETO, FUNDO], 2)),
            1)

    def test_pixel_da_cor_transparente_nao_conta_mesmo_sendo_colorido(self):
        # FUNDO e colorido, mas e a cor transparente: nao e desenhado.
        self.assertEqual(
            mod.nao_cinza_desenhados(bmp([FUNDO, FUNDO, FUNDO, FUNDO], 2)), 0)

    def test_padding_de_linha_nao_entra_na_conta(self):
        # 1 px de largura => 3 bytes de dado e 1 de padding por linha.
        self.assertEqual(
            mod.nao_cinza_desenhados(bmp([FUNDO, LARANJA], 1)), 1)


class TestAbortos(unittest.TestCase):
    def test_recusa_bpp_diferente_de_24(self):
        b = bytearray(bmp([FUNDO, PRETO, BRANCO, FUNDO], 2))
        struct.pack_into("<H", b, 28, 8)
        with self.assertRaises(mod.CheckError) as c:
            mod.pixels_bmp(bytes(b))
        self.assertIn("24 bpp", str(c.exception))

    def test_recusa_comprimido(self):
        b = bytearray(bmp([FUNDO, PRETO, BRANCO, FUNDO], 2))
        struct.pack_into("<I", b, 30, 1)          # BI_RLE8
        with self.assertRaises(mod.CheckError):
            mod.pixels_bmp(bytes(b))

    def test_recusa_top_down(self):
        b = bytearray(bmp([FUNDO, PRETO, BRANCO, FUNDO], 2))
        struct.pack_into("<i", b, 22, -2)
        with self.assertRaises(mod.CheckError) as c:
            mod.pixels_bmp(bytes(b))
        self.assertIn("top-down", str(c.exception))

    def test_recusa_stream_que_nao_e_bmp(self):
        with self.assertRaises(mod.CheckError):
            mod.pixels_bmp(b"NAOEUMBMP" + b"\x00" * 60)

    def test_recusa_stream_truncado(self):
        b = bmp([FUNDO, PRETO, BRANCO, FUNDO], 2)
        with self.assertRaises(mod.CheckError):
            mod.pixels_bmp(b[:-4])


class TestGuardas(unittest.TestCase):
    """As tres guardas do `conferir()`, com a arvore real e INVARIANTES falso."""

    def setUp(self):
        self.original = set(mod.INVARIANTES)
        self.controle = mod.CONTROLE

    def tearDown(self):
        mod.INVARIANTES = self.original
        mod.CONTROLE = self.controle

    def test_arvore_real_passa(self):
        problemas, contagem = mod.conferir()
        self.assertEqual(problemas, [])
        self.assertEqual(contagem["invariantes sob gdeDisabled"],
                         len(self.original))

    def test_invariante_nao_declarada_derruba(self):
        mod.INVARIANTES = self.original - {("ep2002_mainform.lfm",
                                            "iguala_nombres")}
        problemas, _ = mod.conferir()
        self.assertTrue(any("iguala_nombres" in p and "nao esta em INVARIANTES"
                            in p for p in problemas), problemas)

    def test_declarada_que_deixou_de_ser_invariante_derruba(self):
        mod.INVARIANTES = self.original | {("ep2002_mainform.lfm",
                                            "boton_nombres2iso")}
        problemas, _ = mod.conferir()
        self.assertTrue(any("boton_nombres2iso" in p and "deixou de ser"
                            in p for p in problemas), problemas)

    def test_nome_inexistente_em_INVARIANTES_derruba(self):
        mod.INVARIANTES = self.original | {("ep2002_mainform.lfm", "nao_existe")}
        problemas, _ = mod.conferir()
        self.assertTrue(any("sumiu dos .lfm" in p for p in problemas),
                        problemas)

    def test_controle_derruba_quando_o_decodificador_quebra(self):
        mod.CONTROLE = ("ep2002_mainform.lfm", "boton_nombres2iso", 279)
        problemas, _ = mod.conferir()
        self.assertTrue(any("decodificador de BMP quebrou" in p
                            for p in problemas), problemas)


class TestContrato(unittest.TestCase):
    def test_check_sai_zero(self):
        self.assertEqual(mod.main(["check_glifos_disabled.py", "--check"]), 0)

    def test_nao_escreve_arquivo_nenhum(self):
        forms = Path(mod.FORMS)
        antes = {p: p.stat().st_mtime_ns for p in forms.glob("*.lfm")}
        mod.main(["check_glifos_disabled.py", "--check"])
        depois = {p: p.stat().st_mtime_ns for p in forms.glob("*.lfm")}
        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
