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

    def test_os_dois_de_nome_saem_do_lote_provado_pelo_binario(self):
        """`edit_nombre1/2` tem limite POR TIME, e o lote e decodificado.

        Este teste ja afirmou duas coisas erradas, e passou nas duas. Primeiro
        que o destino era `raw_kanji_name` (40 bytes, `div 2` = 20), porque a
        conta fecha. Depois que o limite era o literal 5, lido da tela -- e a
        tela lia 5 porque o sexto caractere de `ABC.D ` e um espaco.

        O que ele segura agora nao e numero escrito a mao: e que o gerador
        DECODIFICA o operando ate a entrada de `0x004231a0` e emite o valor da
        tabela de comprimento daquele lote, com o `- 1` do lote kanji.
        """
        um = self.por_campo["edit_nombre1"]
        self.assertEqual(um.destino, "TEAM_NAME_KANJI_LEN")
        self.assertIn("OFS_TEAM_NAME_KANJI", um.nota)
        # O `- 1` e o `dec` de 0x00403d95, que so vale para a linha 0 coluna 0.
        self.assertEqual(um.maxlength,
                         T.tabela_de_comprimento("TEAM_NAME_KANJI_LEN")
                         [T.TIME_DE_REFERENCIA] - 1)
        self.assertIn("menos um", um.nota)

        dois = self.por_campo["edit_nombre2"]
        self.assertEqual(dois.destino, "TEAM_NAME_LEN_3")
        self.assertEqual(dois.maxlength,
                         T.tabela_de_comprimento("TEAM_NAME_LEN_3")
                         [T.TIME_DE_REFERENCIA] - 1)
        self.assertIn("OFS_TEAM_NAME_3", dois.nota)

    def test_so_o_lote_kanji_leva_o_decremento(self):
        """O `dec` de 0x00403d95 e da linha 0 coluna 0, e de mais nenhuma.

        Se ele valesse para todos, o `edit_nombre2` cairia de 7 para 6 -- e 7 e
        o que o oraculo mostra na tela.
        """
        self.assertEqual(T.LOTE_COM_DECREMENTO, ("OFS_TEAM_NAME_KANJI",))
        dois = self.por_campo["edit_nombre2"]
        self.assertNotIn("menos um", dois.nota)

    def test_decremento_num_lote_de_um_byte_derruba(self):
        """O `dec` so foi medido no caminho do `div 2`."""
        original = T.LOTE_COM_DECREMENTO
        T.LOTE_COM_DECREMENTO = ("OFS_TEAM_NAME_KANJI", "OFS_TEAM_NAME_3")
        self.addCleanup(setattr, T, "LOTE_COM_DECREMENTO", original)
        with self.assertRaises(T.DumpError) as e:
            T.monta()
        self.assertIn("so foi medido no caminho do `div 2`", str(e.exception))

    def test_lote_declarado_errado_derruba(self):
        """A guarda que faltava: trocar o `OFS_*` esperado tem de abortar."""
        original = dict(T.DESTINOS)
        T.DESTINOS["edit_nombre1"] = ("OFS_TEAM_NAME_1", "TEAM_NAME_LEN_1")
        self.addCleanup(T.DESTINOS.update, original)
        with self.assertRaises(T.DumpError) as e:
            T.monta()
        self.assertIn("DESTINOS declara OFS_TEAM_NAME_1", str(e.exception))

    def test_operando_fora_de_um_campo_mais_quatro_aborta(self):
        pe = T.PE(T.EXE.read_bytes(), T.REL_EXE)
        with self.assertRaises(T.DumpError):
            T.lote_do_operando(pe, T.BASE_DAS_MEDIDAS + T.CAMPO_LARGURA + 1)

    def test_operando_num_buraco_da_tabela_aborta(self):
        """A linha 0 so tem duas colunas; a terceira e zero."""
        pe = T.PE(T.EXE.read_bytes(), T.REL_EXE)
        with self.assertRaises(T.DumpError) as e:
            T.lote_do_operando(pe, T.BASE_DAS_MEDIDAS + T.CAMPO_LARGURA
                               + 2 * T.PASSO_COLUNA)
        self.assertIn("buraco", str(e.exception))

    def test_forma_incompativel_com_o_lote_aborta(self):
        """`div 2` so vale para lote de dois bytes por caractere."""
        original = dict(T.DESTINOS)
        T.DESTINOS["edit_nombre1"] = ("OFS_TEAM_NAME_KANJI", "TEAM_NAME_LEN_3")
        self.addCleanup(T.DESTINOS.update, original)
        with self.assertRaises(T.DumpError) as e:
            T.monta()
        self.assertIn("dois bytes por caractere", str(e.exception))

    def test_os_de_texto_cortam_um_byte_antes_do_destino(self):
        for campo in ("edit_nombre3", "casilla_nombre"):
            l = self.por_campo[campo]
            self.assertEqual(l.maxlength, l.largura - 1, campo)

    def test_o_numero_de_camisa_esta_marcado_como_sem_governo(self):
        self.assertIn("casilla_dorsalKeyPress",
                      self.por_campo["casilla_dorsal"].nota)


if __name__ == "__main__":
    unittest.main()
