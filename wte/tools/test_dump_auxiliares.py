#!/usr/bin/env python3
"""Testes do `dump_auxiliares.py`: a descoberta e as tres conferencias.

O script tem uma parte que **descobre** (percorre corpo e separa chamada
interna de importada) e uma parte que **confere** (as tres afirmacoes que
foram para spec). As duas erram de formas diferentes, e as duas erram calado:
descoberta que perde uma chamada devolve tabela curta com cara de completa, e
conferencia que nunca reprova e conferencia ausente -- que foi o que a
CORR-WTE-020 achou no `dfm2lfm.py`.

Os testes montam **corpos sinteticos** num PE de mentira, entao rodam num
clone sem a pasta `we-team-editor/`. So a medicao contra o binario de verdade
fica sob `skipUnless`, como no `test_dump_offsets.py`.
"""

from __future__ import annotations

import struct
import unittest

import dump_auxiliares as A

REAL = A.EXE.is_file() and (A.OUT / "offsets.tsv").exists()

TEXT_VA = 0x00401000
DATA_VA = 0x00423000

# A `.text` de mentira cobre 0x401000..0x411000 porque os dois enderecos que as
# conferencias visitam -- `PULA_SETOR` e `VARRE_TABELA` -- moram la dentro. Com
# a pagina unica que a primeira versao usava, os testes de guarda passavam pelo
# motivo errado: o erro era "fora das secoes", nao a divergencia plantada.
TEXT_TAM = 0x10000


class PEFalso:
    """PE minimo: uma `.text` e uma `.data`, ambas em offset conhecido.

    Implementa so o que `corpo`, `chamadas`, `internas` e as tres conferencias
    usam -- `data`, `base`, `sections`, `off` e `cstring`.
    """

    def __init__(self, text: bytes = b"", data: bytes = b"") -> None:
        self.base = 0x00400000
        self.text = text.ljust(TEXT_TAM, b"\x90")
        self.dados = data.ljust(0x1000, b"\x00")
        self.data = self.text + self.dados
        self.sections = [
            (".text", TEXT_VA - self.base, len(self.text), 0, len(self.text)),
            (".data", DATA_VA - self.base, len(self.dados), len(self.text),
             len(self.dados)),
        ]

    def off(self, va: int) -> int | None:
        if TEXT_VA <= va < TEXT_VA + len(self.text):
            return va - TEXT_VA
        if DATA_VA <= va < DATA_VA + len(self.dados):
            return len(self.text) + (va - DATA_VA)
        return None

    def cstring(self, va: int, limite: int = 64) -> str | None:
        o = self.off(va)
        if o is None:
            return None
        bruto = self.data[o:o + limite].split(b"\0")[0]
        if not bruto or not all(32 <= b < 127 for b in bruto):
            return None
        return bruto.decode("latin1")


def call(origem: int, destino: int) -> bytes:
    """`call rel32` de `origem` para `destino`."""
    return b"\xe8" + struct.pack("<i", destino - (origem + 5))


# ------------------------------------------------------------- descoberta ---
class TestChamadas(unittest.TestCase):
    def test_acha_call_rel32(self):
        corpo = call(TEXT_VA, 0x00401800) + call(TEXT_VA + 5, 0x00401900) + b"\xc3"
        pe = PEFalso(corpo)
        self.assertEqual(A.chamadas(pe, TEXT_VA, 0, len(corpo)),
                         [0x00401800, 0x00401900])

    def test_nao_repete_o_mesmo_alvo(self):
        corpo = call(TEXT_VA, 0x00401800) + call(TEXT_VA + 5, 0x00401800) + b"\xc3"
        pe = PEFalso(corpo)
        self.assertEqual(A.chamadas(pe, TEXT_VA, 0, len(corpo)), [0x00401800])

    def test_0xe8_dentro_de_imediato_nao_e_chamada(self):
        """`mov eax,0x40b2e8` tem um 0xe8 no operando, e nao chama nada.

        Este e o teste que separa percorrer instrucao a instrucao de varrer o
        byte 0xe8: a varredura de byte inventaria uma chamada aqui, e o alvo
        sairia de quatro bytes lidos do lugar errado.
        """
        corpo = b"\xb8\xe8\xb2\x40\x00" + b"\xc3"
        pe = PEFalso(corpo)
        self.assertEqual(A.chamadas(pe, TEXT_VA, 0, len(corpo)), [])


class TestInternas(unittest.TestCase):
    """Importada e handler publicado saem; o resto fica."""

    def monta(self):
        # 0x00401800 e um thunk `jmp DWORD PTR ds:0x0043e648`
        thunk = 0x00401800
        text = bytearray(b"\x90" * TEXT_TAM)
        text[thunk - TEXT_VA:thunk - TEXT_VA + 6] = (
            b"\xff\x25" + struct.pack("<I", 0x0043E648))
        return PEFalso(bytes(text)), {0x0043E648: "@Forms@TForm@Show$qqrv"}

    def test_thunk_sai(self):
        pe, iat = self.monta()
        self.assertEqual(
            A.internas(pe, [0x00401800], iat, set(), (TEXT_VA, TEXT_TAM)), [])

    def test_handler_publicado_sai(self):
        pe, iat = self.monta()
        self.assertEqual(
            A.internas(pe, [0x00401900], iat, {0x00401900}, (TEXT_VA, TEXT_TAM)),
            [])

    def test_fora_da_text_sai(self):
        pe, iat = self.monta()
        self.assertEqual(
            A.internas(pe, [0x00500000], iat, set(), (TEXT_VA, TEXT_TAM)), [])

    def test_interna_fica(self):
        pe, iat = self.monta()
        self.assertEqual(
            A.internas(pe, [0x00401900], iat, set(), (TEXT_VA, TEXT_TAM)),
            [0x00401900])


# ------------------------------------------------------- fronteira de setor ---
def corpo_pula_setor(setor: int, fim: int, salto: int) -> bytes:
    """Um corpo com a forma que `confere_pula_setor` procura."""
    return (b"\x53"                                  # push ebx
            + b"\xb9" + struct.pack("<I", setor)     # mov ecx,imm32
            + b"\x81\xfa" + struct.pack("<I", fim)   # cmp edx,imm32
            + b"\x68" + struct.pack("<I", salto)     # push imm32
            + b"\x5b\xc3")                           # pop ebx / ret


class TestPulaSetor(unittest.TestCase):
    def monta(self, corpo: bytes) -> PEFalso:
        text = bytearray(b"\x90" * TEXT_TAM)
        base = A.PULA_SETOR - TEXT_VA
        text[base:base + len(corpo)] = corpo
        return PEFalso(bytes(text))

    def test_geometria_certa_passa(self):
        pe = self.monta(corpo_pula_setor(A.SETOR, A.FIM_DOS_DADOS, A.SALTO))
        self.assertEqual(A.confere_pula_setor(pe, []),
                         {"setor": A.SETOR, "fim_dos_dados": A.FIM_DOS_DADOS,
                          "salto": A.SALTO})

    def test_setor_diferente_reprova(self):
        pe = self.monta(corpo_pula_setor(2048, A.FIM_DOS_DADOS, A.SALTO))
        with self.assertRaises(A.DumpError) as ctx:
            A.confere_pula_setor(pe, [])
        self.assertIn("geometria de setor", str(ctx.exception))

    def test_padrao_ambiguo_reprova_em_vez_de_ler_o_errado(self):
        """Dois `mov ecx,imm32` no corpo: a guarda para, nao escolhe.

        E a armadilha que o `check_barras.py` ja pagou -- la o padrao casava
        duas vezes e a leitura silenciosa teria pego a constante do
        arredondamento em vez da ancora.
        """
        corpo = (corpo_pula_setor(A.SETOR, A.FIM_DOS_DADOS, A.SALTO)[:-2]
                 + b"\xb9" + struct.pack("<I", 999) + b"\xc3")
        pe = self.monta(corpo)
        with self.assertRaises(A.DumpError) as ctx:
            A.confere_pula_setor(pe, [])
        self.assertIn("casou 2 vezes", str(ctx.exception))


# -------------------------------------------------------- tabelas de letra ---
class TestTabelasDeLetra(unittest.TestCase):
    def monta(self, maiusculas: bytes, minusculas: bytes) -> PEFalso:
        dados = bytearray(b"\x00" * 0x1000)
        for base, primeiro, _ultimo, rotulo in A.TABELAS_DE_LETRA:
            conteudo = maiusculas if rotulo == "maiusculas" else minusculas
            inicio = (base + primeiro) - DATA_VA
            dados[inicio:inicio + len(conteudo)] = conteudo
        return PEFalso(b"", bytes(dados))

    def test_identidade_passa(self):
        pe = self.monta(bytes(range(0x41, 0x5B)), bytes(range(0x61, 0x7B)))
        lidas = A.confere_tabelas_de_letra(pe)
        self.assertEqual([t["conteudo"] for t in lidas],
                         ["ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                          "abcdefghijklmnopqrstuvwxyz"])

    def test_mapa_que_nao_e_identidade_reprova(self):
        """Um ROT-13 nas maiusculas: a rotina viraria tradutor, nao filtro."""
        rot13 = bytes((b - 0x41 + 13) % 26 + 0x41 for b in range(0x41, 0x5B))
        pe = self.monta(rot13, bytes(range(0x61, 0x7B)))
        with self.assertRaises(A.DumpError) as ctx:
            A.confere_tabelas_de_letra(pe)
        self.assertIn("nao e identidade", str(ctx.exception))


# ----------------------------------------------------- varredura da tabela ---
def corpo_varre_tabela(base: int, colunas: int, passo: int) -> bytes:
    return (b"\x55\x8b\xec"                              # push ebp / mov ebp,esp
            + b"\xc7\x45\xcc" + struct.pack("<I", base)  # mov [ebp-0x34],imm32
            + b"\x83\xfe" + bytes([colunas])             # cmp esi,imm8
            + b"\x83\x45\xcc" + bytes([passo])           # add [ebp-0x34],imm8
            + b"\xc9\xc3")                               # leave / ret


class TestVarreduraDaTabela(unittest.TestCase):
    def monta(self, corpo: bytes) -> PEFalso:
        text = bytearray(b"\x90" * TEXT_TAM)
        base = A.VARRE_TABELA - TEXT_VA
        text[base:base + len(corpo)] = corpo
        return PEFalso(bytes(text))

    def test_base_igual_a_do_offsets_tsv_passa(self):
        esperada = 0x00423120
        pe = self.monta(corpo_varre_tabela(esperada, A.COLUNAS,
                                           A.PASSO_DA_LINHA))
        original = A.base_da_tabela_de_offsets
        A.base_da_tabela_de_offsets = lambda: esperada
        try:
            lido = A.confere_varredura_da_tabela(pe, [])
        finally:
            A.base_da_tabela_de_offsets = original
        self.assertEqual(lido["base"], esperada)
        self.assertEqual(lido["colunas"], A.COLUNAS)

    def test_base_divergente_reprova(self):
        pe = self.monta(corpo_varre_tabela(0x00423120, A.COLUNAS,
                                           A.PASSO_DA_LINHA))
        original = A.base_da_tabela_de_offsets
        A.base_da_tabela_de_offsets = lambda: 0x00424444
        try:
            with self.assertRaises(A.DumpError) as ctx:
                A.confere_varredura_da_tabela(pe, [])
        finally:
            A.base_da_tabela_de_offsets = original
        self.assertIn("offsets.tsv diz que a tabela comeca", str(ctx.exception))

    def test_linha_que_nao_fecha_reprova(self):
        """5 colunas de quatro bytes nao dao uma linha de 0x18."""
        esperada = 0x00423120
        pe = self.monta(corpo_varre_tabela(esperada, 5, A.PASSO_DA_LINHA))
        original = A.base_da_tabela_de_offsets
        A.base_da_tabela_de_offsets = lambda: esperada
        try:
            with self.assertRaises(A.DumpError) as ctx:
                A.confere_varredura_da_tabela(pe, [])
        finally:
            A.base_da_tabela_de_offsets = original
        self.assertIn("esperava 6", str(ctx.exception))


# ------------------------------------------------------- contra o binario ---
@unittest.skipUnless(REAL, "precisa do we-team-editor.exe e do offsets.tsv")
class TestReal(unittest.TestCase):
    def test_regeneracao_e_estavel(self):
        self.assertEqual(A.generate(), A.generate())

    def test_papel_para_endereco_inexistente_aborta(self):
        original = dict(A.PAPEIS)
        A.PAPEIS[0x00401234] = "rotina que nao existe"
        try:
            with self.assertRaises(A.DumpError) as ctx:
                A.medir()
        finally:
            A.PAPEIS.clear()
            A.PAPEIS.update(original)
        self.assertIn("nao chama", str(ctx.exception))

    def test_as_tres_rotinas_que_travavam_as_specs_tem_papel(self):
        m = A.medir()
        por_endereco = {r["endereco"]: r for r in m["rotinas"]}
        for endereco in (0x0040B0B4, 0x0040B188, 0x0040B2D8):
            self.assertTrue(por_endereco[endereco]["papel"],
                            f"{endereco:#010x} sem papel")

    def test_tamanho_desconhecido_nunca_tem_papel(self):
        """A tabela pode dizer `?`; o que ela nao pode e afirmar sem medir."""
        for r in A.medir()["rotinas"]:
            if r["bytes"] is None:
                self.assertEqual(r["papel"], "", f"{r['endereco']:#010x}")


if __name__ == "__main__":
    unittest.main()
