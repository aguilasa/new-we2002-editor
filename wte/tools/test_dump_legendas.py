#!/usr/bin/env python3
"""Testes do `dump_legendas.py`: a varredura e as conferencias.

O script tem uma parte que **decodifica** (percorre o inicializador e casa
cada construtor de `AnsiString` com o slot que ele enche) e uma parte que
**confere** (as duas tabelas fecham, e a forma de cada linha bate com o `Max`
do formulario). As duas erram calado, e de formas diferentes:

- decodificacao que perde um trio devolve tabela com buraco, e sem a
  conferencia de contiguidade o buraco viraria uma legenda deslocada -- a
  ficha mostraria "Za" onde devia mostrar "Lt", que e plausivel e errado;
- conferencia que nunca reprova e conferencia ausente. A atribuicao
  "linha `n` = `flechasapa n+1`" **nao esta escrita em lugar nenhum do
  binario**: sai da ordem em que o inicializador constroi. O `Max` do DFM e a
  segunda medida que a sustenta, e um teste tem de provar que ela reprova.

Os testes montam um inicializador sintetico num PE de mentira, entao rodam num
clone sem a pasta `we-team-editor/`. So a medicao contra o binario de verdade
fica sob `skipUnless`, como no `test_dump_auxiliares.py`.
"""

from __future__ import annotations

import struct
import unittest

import dump_legendas as L

REAL = L.EXE.is_file()

BASE = 0x00400000
TEXT_VA = 0x00401000
DATA_VA = 0x00423000
DATA_TAM = 0x4000          # cobre as tabelas (0x423798) e os literais (0x424754)
TEXT_TAM = DATA_VA - TEXT_VA


class PEFalso:
    """PE minimo: uma `.text` que alcanca o construtor e uma `.data` grande.

    A `.text` vai ate `0x00423000` de proposito: `CTOR` (`0x0042120c`) tem de
    cair dentro dela, senao `pe.off(CTOR)` sai `None` e a comparacao de alvo
    nunca casa -- que foi exatamente o primeiro erro desta ferramenta.
    """

    def __init__(self, text: bytes, data: bytes) -> None:
        self.base = BASE
        self.text = text.ljust(TEXT_TAM, b"\x90")
        self.dados = data.ljust(DATA_TAM, b"\x00")
        self.data = self.text + self.dados
        self.sections = [
            (".text", TEXT_VA - BASE, len(self.text), 0, len(self.text)),
            (".data", DATA_VA - BASE, len(self.dados), len(self.text),
             len(self.dados)),
        ]

    def off(self, va: int) -> int | None:
        if TEXT_VA <= va < TEXT_VA + len(self.text):
            return va - TEXT_VA
        if DATA_VA <= va < DATA_VA + len(self.dados):
            return len(self.text) + (va - DATA_VA)
        return None


# ------------------------------------------------------------- montagem ------

def _lea_edx_ebx(disp: int) -> bytes:
    return b"\x8d\x93" + struct.pack("<i", disp)


def _lea_eax_esi(disp: int) -> bytes:
    return b"\x8d\x86" + struct.pack("<i", disp)


def _call(origem: int, destino: int) -> bytes:
    return b"\xe8" + struct.pack("<i", destino - (origem + 5))


class Montador:
    """Constroi um inicializador sintetico e o blob de literais dele."""

    def __init__(self) -> None:
        self.corpo = bytearray()
        self.va = L.INI
        self.literais = bytearray()
        self.textos: dict[int, str] = {}   # deslocamento em ebx -> texto

    def _emite(self, bs: bytes) -> None:
        self.corpo += bs
        self.va += len(bs)

    def bases(self, tabelas: int = L.BASE_TABELAS,
              literais: int = L.BASE_LITERAIS) -> "Montador":
        self._emite(b"\xbb" + struct.pack("<I", literais))
        self._emite(b"\xbe" + struct.pack("<I", tabelas))
        return self

    def slot(self, destino_disp: int, texto: str) -> "Montador":
        disp = len(self.literais)
        self.literais += texto.encode("ascii") + b"\0"
        self.textos[disp] = texto
        self._emite(_lea_edx_ebx(disp))
        self._emite(_lea_eax_esi(destino_disp))
        self._emite(_call(self.va, L.CTOR))
        return self

    def pe(self) -> PEFalso:
        text = bytearray(b"\x90" * (L.INI - TEXT_VA)) + self.corpo
        text = text.ljust(L.FIM - TEXT_VA, b"\x90")
        text += b"\xc3"                                    # o `ret` do fim
        dados = bytearray(DATA_TAM)
        inicio = L.BASE_LITERAIS - DATA_VA
        dados[inicio:inicio + len(self.literais)] = self.literais
        return PEFalso(bytes(text), bytes(dados))


def completo(**troca: str) -> Montador:
    """Um inicializador que enche as duas tabelas com texto reconhecivel.

    A forma de cada linha copia a do binario de verdade -- `Max + 1` celulas
    com texto e o resto com um espaco --, porque e isso que a conferencia do
    `Max` julga.
    """
    maxs = L.maximos()
    m = Montador().bases()
    for linha in range(L.LINHAS):
        mx = maxs[f"flechasapa{linha + 1}"]
        cheias = 0 if mx >= L.COLUNAS else mx + 1
        for coluna in range(L.COLUNAS):
            disp = linha * L.PASSO + coluna * 4
            chave = f"{linha},{coluna}"
            if chave in troca:
                texto = troca[chave]
            else:
                texto = f"L{linha}C{coluna}" if coluna < cheias else " "
            m.slot(disp, texto)
    for i in range(maxs[L.CABELO] + 1):
        m.slot(L.LINHAS * L.PASSO + i * 4, f"H{i}")
    return m


# ------------------------------------------------------------ decodificacao --

class TestVarredura(unittest.TestCase):
    def test_monta_as_duas_tabelas(self):
        ficha, cabelo = L.confere(L.varre(completo().pe()))
        self.assertEqual(len(ficha), L.LINHAS * L.COLUNAS)
        self.assertEqual(ficha[0].texto, "L0C0")
        self.assertEqual(ficha[0].destino, L.BASE_TABELAS)
        self.assertEqual(len(cabelo), L.maximos()[L.CABELO] + 1)
        self.assertEqual(cabelo[0].destino, L.BASE_CABELO)

    def test_mov_eax_esi_e_o_deslocamento_zero(self):
        """O Borland emite `mov eax,esi` no lugar de `lea eax,[esi+0]`.

        Sem esta forma o primeiro slot da tabela some, e o buraco aparece
        justo na linha 0 coluna 0 -- que foi o sintoma real.
        """
        self.assertEqual(L._carrega(b"\x8b\xc6", 0, 2), ("eax", True, 0))

    def test_mov_reg_imm32_e_absoluto(self):
        """O inicializador tambem monta cadeias em globais soltas.

        Elas nao sao relativas a base nenhuma, e some-las a `esi` produziria
        destino no meio da tabela -- uma legenda por cima de outra.
        """
        self.assertEqual(L._carrega(b"\xb8\x6c\x2e\x43\x00", 0, 5),
                         ("eax", False, 0x00432E6C))

    def test_0xe8_dentro_de_imediato_nao_e_construtor(self):
        self.assertIsNone(L._chamada(b"\xb8\xe8\xb2\x40\x00", 0, 5))


# ------------------------------------------------------------ conferencias --

class TestConferencias(unittest.TestCase):
    def _erro(self, m: Montador) -> str:
        with self.assertRaises(L.DumpError) as ctx:
            L.confere(L.varre(m.pe()))
        return str(ctx.exception)

    def test_buraco_na_ficha_reprova(self):
        m = Montador().bases()
        for i in range(L.LINHAS * L.COLUNAS):
            if i == 5:
                continue
            m.slot(i * 4, "x")
        self.assertIn("buraco", self._erro(m))

    def test_slot_montado_duas_vezes_reprova(self):
        m = completo()
        m.slot(0, "outro")
        self.assertIn("duas vezes", self._erro(m))

    def test_base_recarregada_reprova(self):
        m = completo()
        m._emite(b"\xbe" + struct.pack("<I", 0x00424000))
        self.assertIn("recarregado", self._erro(m))

    def test_linha_com_celulas_demais_reprova(self):
        """`flechasapa12` tem `Max` 1 -- duas posicoes. Uma terceira e erro.

        Este e o teste que faz a atribuicao linha-para-controle valer alguma
        coisa: sem ele o gerador aceitaria qualquer forma de linha, e a coluna
        `Max` do markdown seria enfeite.
        """
        self.assertIn("`Max` 1", self._erro(completo(**{"11,2": "TALVEZ"})))

    def test_linha_de_faixa_grande_tem_de_ficar_vazia(self):
        """`flechasapa7` e a altura: `Max` 63, e a linha dele nao se usa."""
        self.assertIn("maior que", self._erro(completo(**{"6,0": "180"})))

    def test_literal_nao_imprimivel_reprova(self):
        m = Montador().bases()
        m.slot(0, "ok")
        m.literais[-1:] = b"\x01\0"        # estraga o NUL do primeiro literal
        with self.assertRaises(L.DumpError) as ctx:
            L.varre(m.pe())
        self.assertIn("ASCII imprimivel", str(ctx.exception))


# ----------------------------------------------------- contra o exe de verdade --

@unittest.skipUnless(REAL, "we-team-editor/we-team-editor.exe nao esta no disco")
class TestReal(unittest.TestCase):
    def setUp(self):
        pe = L.PE(L.EXE.read_bytes(), L.REL_EXE)
        self.ficha, self.cabelo = L.confere(L.varre(pe))
        self.maxs = L.maximos()

    def test_a_primeira_linha_e_a_posicao_do_jogador(self):
        """Se esta linha mudar, a ficha inteira esta lendo a tabela errada."""
        self.assertEqual([s.texto for s in self.ficha[:L.COLUNAS]],
                         ["Gl", "Za", "Lt", "Vl", "Al", "Me", "At", "Po"])

    def test_o_cabelo_tem_um_nome_por_bitmap(self):
        """32 nomes contra os 32 `image/pelo/pelo_<n>.bmp` da assets.md §5."""
        self.assertEqual(len(self.cabelo), 32)
        self.assertEqual(self.maxs[L.CABELO] + 1, 32)

    def test_as_tres_linhas_vazias_sao_as_de_faixa_grande(self):
        vazias = {linha for linha in range(L.LINHAS)
                  if not any(self.ficha[linha * L.COLUNAS + c].texto.strip()
                             for c in range(L.COLUNAS))}
        grandes = {linha for linha in range(L.LINHAS)
                   if self.maxs[f"flechasapa{linha + 1}"] >= L.COLUNAS}
        self.assertEqual(vazias, grandes)


if __name__ == "__main__":
    unittest.main()
