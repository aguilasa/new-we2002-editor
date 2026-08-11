#!/usr/bin/env python3
"""Testes do `compara_tela.py`: a deteccao de banda e a comparacao.

A deteccao erra em silencio de dois jeitos, e os dois ja aconteceram na
setima passagem da WTE-TASK-25: banda de sobra (o icone laranja do botao
"Sobre..." entrou na lista) e banda a menos. Nos dois casos o alinhamento entre
os cinco valores muda e a comparacao passa a confrontar barras diferentes --
divergencia falsa, ou pior, coincidencia que passa.

Tudo aqui roda contra imagens montadas em memoria: nao precisa do `.exe`, nem
do `:99`, nem de captura nenhuma.
"""

from __future__ import annotations

import unittest

import compara_tela as C

try:
    from PIL import Image
    TEM_PIL = True
except ImportError:                 # pragma: no cover
    TEM_PIL = False


def tela(bandas, altura_da_banda=12, x0=None, extras=()):
    """Imagem com as bandas pedidas, mais `extras` de `(y, largura, altura)`."""
    x0 = C.FAIXA_X[0] if x0 is None else x0
    alt = 10 + len(bandas) * 20 + 40
    img = Image.new("RGB", (C.FAIXA_X[1] + 20, alt), (0, 0, 128))
    for i, larg in enumerate(bandas):
        topo = 10 + i * 20
        for y in range(topo, topo + altura_da_banda):
            for x in range(x0, x0 + larg):
                img.putpixel((x, y), (255, 160, 0))
    for y0, larg, altura in extras:
        for y in range(y0, y0 + altura):
            for x in range(x0, x0 + larg):
                img.putpixel((x, y), (255, 160, 0))
    return img


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestBandas(unittest.TestCase):
    def test_mede_as_cinco(self):
        img = tela([9, 20, 64, 75, 141])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_banda_baixa_demais_e_ignorada(self):
        """Artefato de 1 px de altura nao e barra."""
        img = tela([9, 20, 64, 75, 141], extras=[(0, 60, 1)])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_banda_estreita_demais_e_ignorada(self):
        """O icone do botao `Sobre...`: alto o bastante, estreito demais.

        Foi o que fez a primeira medicao achar seis bandas onde ha cinco.
        """
        img = tela([9, 20, 64, 75, 141], extras=[(0, 3, 8)])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_barra_vazia_de_9px_conta(self):
        """9 px e `11*0 + 9` -- barra zerada, nao ruido. O limite e >=, e a
        diferenca entre medir o time sem forca e nao o medir."""
        img = tela([9, 9, 9, 9, 9])
        self.assertEqual(C.larguras(img, "x"), [9, 9, 9, 9, 9])

    def test_contagem_errada_aborta(self):
        img = tela([64, 75, 75])
        with self.assertRaises(C.TelaError) as e:
            C.larguras(img, "oraculo")
        self.assertIn("achei 3 banda(s)", str(e.exception))


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestCompara(unittest.TestCase):
    def test_iguais_passam(self):
        a = tela([64, 53, 75, 75, 75])
        m = C.compara(a, tela([64, 53, 75, 75, 75]), 2)
        self.assertEqual(m["diferencas"], [])

    def test_diferenca_e_nomeada_pela_barra(self):
        m = C.compara(tela([64, 53, 75, 75, 75]),
                      tela([64, 53, 75, 86, 75]), 2)
        self.assertEqual(len(m["diferencas"]), 1)
        self.assertEqual(m["diferencas"][0]["barra"], "velocidade")
        self.assertEqual(m["diferencas"][0]["oraculo"], 75)
        self.assertEqual(m["diferencas"][0]["port"], 86)

    def test_valor_do_jogo_e_a_inversa_da_largura(self):
        self.assertEqual(C.valor_da_barra(9), 0)
        self.assertEqual(C.valor_da_barra(64), 5)
        self.assertEqual(C.valor_da_barra(141), 12)

    def test_largura_que_nao_fecha_em_inteiro_nao_vira_valor(self):
        """104 px e o caso real do time 63. Barra do jogo e inteira, entao
        `8,64` seria afirmar o que nao se mediu -- devolve None."""
        self.assertIsNone(C.valor_da_barra(104))

    def test_autoteste_do_check_passa(self):
        self.assertEqual(C.autoteste(), 0)


if __name__ == "__main__":
    unittest.main()
