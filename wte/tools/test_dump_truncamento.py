#!/usr/bin/env python3
"""Testes do `dump_truncamento.py`.

O script junta tres fontes que nao se falam -- os `.dfm`, o `.text` do `.exe` e
a camada de dados -- e o valor dele esta justamente em elas se conferirem. Os
modos de errar sao dois, e os dois sao mudos:

- ler a expressao errada (`sar edx,1` confundido com carga de ponteiro) produz
  um `MaxLength` plausivel;
- deixar de conferir contra a largura do destino faz o documento afirmar um
  numero que ninguem mediu duas vezes.

Os testes de decodificacao rodam sobre um `.text` sintetico. A conferencia
contra o `.exe` fica sob `skipUnless`.
"""

from __future__ import annotations

import struct
import unittest

import dump_truncamento as T

REAL = T.EXE.is_file()


class TestLarguraDoDestino(unittest.TestCase):
    """A leitura do Pascal gerado -- a terceira fonte, e a que confere."""

    def test_vetor_simples(self):
        self.assertEqual(
            T.largura_do_destino("wte/src/we2002_player.pas", "name"), 11)

    def test_vetor_de_vetor_devolve_a_dimensao_INTERNA(self):
        """`abbreviations` e `array[0..2] of array[0..3]`: a largura e 4, nao 3.

        Pegar a externa daria 3, que por acaso e o `MaxLength` certo -- e a
        conferencia passaria pelo motivo errado, para sempre.
        """
        self.assertEqual(
            T.largura_do_destino("wte/src/we2002_team.pas", "abbreviations"), 4)

    def test_campo_inexistente_reprova(self):
        with self.assertRaises(T.DumpError):
            T.largura_do_destino("wte/src/we2002_team.pas", "nao_existe")


class TestDfm(unittest.TestCase):
    def test_acha_os_maxlength_declarados(self):
        m = T.maxlength_dos_dfm()
        self.assertEqual(m[("jugador", "casilla_nombre")], 10)
        self.assertEqual(m[("MainForm", "edit_nombre3")], 3)

    def test_nao_atribui_maxlength_ao_objeto_errado(self):
        """`MaxLength` pertence ao ultimo `object` aberto, e so a ele."""
        m = T.maxlength_dos_dfm()
        self.assertNotIn(("jugador", "casilla_precio"), [k for k in m
                                                         if m[k] == 10])


class TestExpressao(unittest.TestCase):
    """As tres formas de `edx`, sobre um `.text` sintetico."""

    def _pe(self, antes: bytes):
        class Falso:
            def __init__(self, d):
                self.data = d
        # a chamada fica logo depois do prefixo montado
        return Falso(antes + b"\xe8\x00\x00\x00\x00"), len(antes)

    def test_literal(self):
        pe, o = self._pe(b"\xba\x03\x00\x00\x00")
        self.assertEqual(T.expressao(pe, o), ("literal", 3))

    def test_menos_um(self):
        pe, o = self._pe(b"\x8b\x15\x48\x3b\x43\x00\x4a")
        self.assertEqual(T.expressao(pe, o), ("menos_um", 0x00433B48))

    def test_metade(self):
        pe, o = self._pe(b"\x8b\x15\x10\x3a\x43\x00\xd1\xfa")
        self.assertEqual(T.expressao(pe, o), ("metade", 0x00433A10))

    def test_carga_de_ponteiro_nao_e_expressao(self):
        """`mov edx,ds:FORM` seguido de `mov eax,[edx+disp]` e ponteiro.

        Tratar isto como comprimento daria `MaxLength := endereco do
        formulario` -- um numero enorme, e nenhum erro. E o terceiro sitio do
        binario de verdade, e foi ele que derrubou a primeira versao.
        """
        pe, o = self._pe(b"\x8b\x15\x60\x43\x43\x00"
                         b"\x8b\x82\x64\x03\x00\x00"
                         b"\xba\x03\x00\x00\x00")
        self.assertEqual(T.expressao(pe, o), ("literal", 3))

    def test_forma_desconhecida_reprova(self):
        pe, o = self._pe(b"\x8b\x15\x10\x3a\x43\x00\x90\x90")
        with self.assertRaises(T.DumpError):
            T.expressao(pe, o)

    def test_sem_carga_de_edx_reprova(self):
        pe, o = self._pe(b"\x90" * 8)
        with self.assertRaises(T.DumpError):
            T.expressao(pe, o)


@unittest.skipUnless(REAL, "we-team-editor/we-team-editor.exe nao esta no disco")
class TestReal(unittest.TestCase):
    def setUp(self):
        self.linhas = T.monta()
        self.por_campo = {l.campo: l for l in self.linhas}

    def test_tres_campos_vem_do_codigo(self):
        do_codigo = [l for l in self.linhas if l.fonte.startswith("código")]
        self.assertEqual(sorted(l.campo for l in do_codigo),
                         ["edit_nombre1", "edit_nombre2", "edit_nombre3"])

    def test_o_primeiro_campo_nao_inventa_destino(self):
        """`edit_nombre1` sai com destino vazio e o valor medido na tela.

        Este teste comecou afirmando o contrario -- que o destino era
        `raw_kanji_name`, 40 bytes, e o limite 20 -- e passava, porque
        `40 div 2` fecha. O `compara_tela.sh --nomes` mediu o oraculo cortando
        em CINCO. O que o teste segura agora nao e o numero: e a RECUSA de
        emitir destino que ninguem mediu.
        """
        l = self.por_campo["edit_nombre1"]
        self.assertEqual(l.destino, "")
        self.assertEqual(l.largura, 0)
        self.assertEqual(l.maxlength, 5)
        self.assertIn("nao medido", l.nota)

    def test_os_de_texto_cortam_um_byte_antes_do_destino(self):
        for campo in ("edit_nombre2", "edit_nombre3", "casilla_nombre"):
            l = self.por_campo[campo]
            self.assertEqual(l.maxlength, l.largura - 1, campo)

    def test_o_numero_de_camisa_esta_marcado_como_sem_governo(self):
        self.assertIn("casilla_dorsalKeyPress",
                      self.por_campo["casilla_dorsal"].nota)


if __name__ == "__main__":
    unittest.main()
