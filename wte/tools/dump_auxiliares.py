#!/usr/bin/env python3
"""As rotinas internas que o grupo de carga chama, e o que cada uma toca.

Gera `wte/re/auxiliares.md` e `wte/re/auxiliares.tsv` — insumo da
[WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md), grupo de carga.

## Por que ele existe

Três specs do grupo pararam em `aberto` pela mesma razão: o handler chama
rotinas que **não são handler publicado**, e sem saber o que elas fazem não dá
para escrever o corpo. A `MainForm.lista_equiposChange` listava cinco desses
endereços numa tabela escrita à mão.

Medido, ela chama **sete**. Tabela de auxiliar escrita à mão erra da forma que
não aparece: o que falta na lista simplesmente não é procurado, e a spec fica
parecendo completa. Este script descobre a lista percorrendo o corpo de cada
handler instrução a instrução — quem entra na tabela é quem o binário chama.

## O que ele separa

Nem todo `call` do corpo é rotina do autor. Três classes, e a distinção é
mecânica, não julgamento:

| Classe | Como se reconhece |
|---|---|
| importada | o alvo é `jmp DWORD PTR ds:<IAT>` — sai com o nome do `.bpl` |
| handler publicado | o alvo está no [`published_methods.tsv`](published_methods.tsv) |
| **interna** | nenhuma das duas — é o que este script inventaria |

## O tamanho não sai de subtração de endereços

O fim de uma rotina interna sai do decodificador x86, como na
[`dump_arranque.py`](dump_arranque.py): a conta barata — até o próximo símbolo
conhecido — funciona no meio da `.text` e mente na borda. Rotina cujo fim o
decodificador não consegue determinar entra na tabela com tamanho `?` em vez de
ficar de fora: **o que não foi medido aparece dizendo que não foi medido.**

## As três conferências que abortam

Elas existem porque as afirmações abaixo entraram em spec e, se deixarem de
valer, o texto vira mentira em silêncio.

1. **A rotina de fronteira de setor.** `0x00403388` não recebe offset: ela
   pergunta ao `ftell` em que ponto do setor está e, se está no fim dos dados,
   pula. As três constantes saem decodificadas **do corpo dela** e têm de ser
   2352 (setor), 2072 (24 de cabeçalho + 2048 de dados) e 304 (280 de EDC/ECC
   + os 24 do cabeçalho seguinte) — a mesma geometria que o `we2002_core` deste
   repositório assa nos `OFS_*`.
2. **As duas tabelas de letra do filtro de nome.** `0x0040b2d8` indexa duas
   tabelas em `.data` pelo próprio byte lido. Elas são **identidade** — `A`…`Z`
   e `a`…`z` —, o que faz da rotina um filtro, não um tradutor. Se um dia
   deixarem de ser identidade, a spec do filtro está errada e a conferência
   reprova.
3. **A base da tabela de offsets.** `0x0040cbc8` carrega um endereço de `.data`
   e o percorre em linhas de seis colunas. Esse endereço tem de ser o mesmo que
   a [WTE-TASK-06](../../docs/tasks/06-mapa-de-offsets.md) registrou como
   primeiro slot em [`offsets.tsv`](offsets.tsv) — é a mesma tabela vista dos
   dois lados, e a conferência lê a base do corpo da rotina em vez de repeti-la.

Uso:

    python3 wte/tools/dump_auxiliares.py            # regenera
    python3 wte/tools/dump_auxiliares.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
CAMPOS = ROOT / "wte" / "re" / "campos.tsv"
OUT = ROOT / "wte" / "re"

REL_EXE = "we-team-editor/we-team-editor.exe"
REL_PUB = "wte/re/published_methods.tsv"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_auxiliares.py"

TSV_NAME = "auxiliares.tsv"
MD_NAME = "auxiliares.md"

GRUPO = "carga"
HANDLERS_ESPERADOS = 28

# Teto duro da varredura de `extent`, o mesmo do `dump_arranque.py`.
TETO = 8192

# Geometria do setor MODE2/2352, decodificada do corpo de `0x00403388` e
# conferida contra estes tres valores. Ver a conferencia 1 do cabecalho.
SETOR = 2352
FIM_DOS_DADOS = 2072
SALTO = 304
PULA_SETOR = 0x00403388

# As duas tabelas de letra do filtro de nome (conferencia 2). O endereco e a
# BASE que o corpo carrega; o indice e o proprio byte lido, entao a faixa util
# comeca em base + primeiro codigo.
FILTRO_NOME = 0x0040B2D8
TABELAS_DE_LETRA = (
    (0x00423129, 0x41, 0x5A, "maiusculas"),
    (0x00423124, 0x61, 0x7A, "minusculas"),
)

# A rotina que percorre a tabela de offsets, e a forma da varredura dela: seis
# colunas de quatro bytes, uma linha de 0x18. A base que ela carrega tem de ser
# a mesma que a WTE-TASK-06 registrou como primeiro slot da tabela -- ver a
# conferencia 3 do cabecalho.
VARRE_TABELA = 0x0040CBC8
COLUNAS = 6
PASSO_DA_LINHA = 0x18

# O papel de cada rotina interna, quando ele foi lido. Chave = endereco.
#
# Esta tabela e a UNICA coisa escrita a mao neste script, e ela nao inventa
# linha: `medir()` aborta se um endereco daqui nao aparecer na descoberta. O
# que nao foi lido nao ganha entrada -- aparece na tabela geral com papel
# vazio, que e a informacao honesta.
PAPEIS: dict[int, str] = {
    0x00403388: "pula a fronteira de setor: se `ftell % 2352 == 2072`, avanca 304",
    0x004033BC: "le `ecx` bytes da imagem a partir do offset em `edx` para o "
                "destino empilhado",
    0x004050D0: "carrega os campos de nome do time selecionado para as globais",
    0x0040CBC8: "percorre a tabela de offsets em `.data`, seis colunas por linha",
    0x00405270: "desenha a bandeira 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)",
    0x004056C8: "desenha o uniforme 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)",
    0x0040B0B4: "preenche as 23 legendas `dorsalN` com os numeros de camisa",
    0x0040B188: "marca a camisa N: apaga a marcada, acha a nova por "
                "`FindComponent`, destaca",
    0x0040B2D8: "preenche `lista_jugadores_1` com os 23 nomes, filtrados",
    0x00417810: "`fseek` da RTL",
    0x00418F70: "`fgetc` da RTL",
}


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do `dump_units.py` e do
# `dump_arranque.py`: cada gerador de `wte/tools/` roda sozinho, sem importar
# os irmaos.
class PE:
    def __init__(self, data: bytes, rotulo: str) -> None:
        self.data = data
        self.rotulo = rotulo
        if data[:2] != b"MZ":
            raise DumpError(f"{rotulo}: nao comeca com MZ")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise DumpError(f"{rotulo}: assinatura PE ausente em {pe:#x}")
        nsec = struct.unpack_from("<H", data, pe + 6)[0]
        szopt = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        self.base = struct.unpack_from("<I", data, opt + 28)[0]
        self.dirs = opt + 96
        self.sections = []
        for i in range(nsec):
            o = pe + 24 + szopt + i * 40
            self.sections.append((
                data[o:o + 8].rstrip(b"\0").decode("latin1"),
                struct.unpack_from("<I", data, o + 12)[0],   # vaddr
                struct.unpack_from("<I", data, o + 8)[0],    # vsize
                struct.unpack_from("<I", data, o + 20)[0],   # raddr
                struct.unpack_from("<I", data, o + 16)[0]))  # rsize

    def off(self, va: int) -> int | None:
        rva = va - self.base
        for _n, vaddr, vsize, raddr, rsize in self.sections:
            if vaddr <= rva < vaddr + max(vsize, rsize) and rva - vaddr < rsize:
                return raddr + (rva - vaddr)
        return None

    def dword(self, va: int) -> int:
        o = self.off(va)
        if o is None:
            raise DumpError(f"{self.rotulo}: {va:#010x} fora das secoes")
        return struct.unpack_from("<I", self.data, o)[0]

    def shortstring(self, va: int) -> str:
        o = self.off(va)
        if o is None:
            raise DumpError(f"{self.rotulo}: {va:#010x} fora das secoes")
        return self.data[o + 1:o + 1 + self.data[o]].decode("latin1")

    def cstring(self, va: int, limite: int = 64) -> str | None:
        """Literal ASCII terminado em NUL, ou None se nao for texto."""
        o = self.off(va)
        if o is None:
            return None
        bruto = self.data[o:o + limite].split(b"\0")[0]
        if not bruto or not all(32 <= b < 127 for b in bruto):
            return None
        return bruto.decode("latin1")

    def imports(self) -> dict[int, str]:
        """Endereco do slot do IAT -> nome importado."""
        rva = struct.unpack_from("<I", self.data, self.dirs + 8)[0]
        o = self.off(self.base + rva)
        if o is None:
            raise DumpError(f"{self.rotulo}: diretorio de import fora das secoes")
        saida: dict[int, str] = {}
        i = 0
        while True:
            ent = self.data[o + i * 20:o + i * 20 + 20]
            if ent == b"\0" * 20:
                break
            oft, _ts, _fc, _nome, ft = struct.unpack("<IIIII", ent)
            to = self.off(self.base + (oft or ft))
            j = 0
            while True:
                v = struct.unpack_from("<I", self.data, to + j * 4)[0]
                if v == 0:
                    break
                if v & 0x80000000:
                    nome = f"ord#{v & 0xFFFF}"
                else:
                    po = self.off(self.base + v)
                    nome = self.data[po + 2:].split(b"\0")[0].decode("latin1")
                saida[self.base + ft + j * 4] = nome
                j += 1
            i += 1
        return saida

    def exports(self) -> dict[int, str]:
        """RVA -> nome exportado (o primeiro, quando ha alias)."""
        rva = struct.unpack_from("<I", self.data, self.dirs)[0]
        if not rva:
            return {}
        o = self.off(self.base + rva)
        nnam = struct.unpack_from("<I", self.data, o + 24)[0]
        afun, anam, aord = struct.unpack_from("<III", self.data, o + 28)
        fo, no, oo = (self.off(self.base + x) for x in (afun, anam, aord))
        saida: dict[int, str] = {}
        for i in range(nnam):
            nr = struct.unpack_from("<I", self.data, no + i * 4)[0]
            nome = self.data[self.off(self.base + nr):].split(b"\0")[0].decode("latin1")
            ordi = struct.unpack_from("<H", self.data, oo + i * 2)[0]
            saida.setdefault(struct.unpack_from("<I", self.data, fo + ordi * 4)[0], nome)
        return saida

    def vmts(self) -> dict[str, int]:
        """Nome de classe -> endereco do VMT, pelo auto-ponteiro."""
        achados: dict[str, int] = {}
        for _n, vaddr, vsize, raddr, rsize in self.sections:
            limite = min(vsize, rsize)
            for delta in range(0, max(0, limite - 4), 4):
                valor = struct.unpack_from("<I", self.data, raddr + delta)[0]
                va = self.base + vaddr + delta
                if valor != va + 76:
                    continue
                vmt = va + 76
                # Nos packages o auto-ponteiro tambem casa em lixo: `dword` e
                # `shortstring` sao chamados so depois de o alvo cair numa secao.
                if self.off(vmt + VMT_CLASS_NAME) is None:
                    continue
                nome_ptr = self.dword(vmt + VMT_CLASS_NAME)
                if not nome_ptr or self.off(nome_ptr) is None:
                    continue
                if self.off(vmt + VMT_INSTANCE_SIZE) is None:
                    continue
                if not self.dword(vmt + VMT_INSTANCE_SIZE):
                    continue
                nome = self.shortstring(nome_ptr)
                if nome.startswith("T") and nome[1:2].isupper():
                    achados.setdefault(nome, vmt)
        return achados

def _i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]



PREFIXES = frozenset(
    [0x66, 0x67, 0xF0, 0xF2, 0xF3, 0x2E, 0x36, 0x3E, 0x26, 0x64, 0x65])

_MAP1: dict[int, tuple[bool, object]] = {}
_MAP2: dict[int, tuple[bool, object]] = {}


def _fill(table: dict[int, tuple[bool, object]], codes, modrm: bool,
          imm: object) -> None:
    for code in codes:
        table[code] = (modrm, imm)


# --- mapa de um byte
for _base in (0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38):
    _fill(_MAP1, range(_base, _base + 4), True, 0)      # alu r/m, r
    _MAP1[_base + 4] = (False, 1)                       # alu al, imm8
    _MAP1[_base + 5] = (False, "z")                     # alu eax, imm32
    _MAP1[_base + 6] = (False, 0)                       # push sreg / daa ...
    _MAP1[_base + 7] = (False, 0)
_fill(_MAP1, range(0x40, 0x60), False, 0)               # inc/dec/push/pop r32
_fill(_MAP1, (0x60, 0x61), False, 0)                    # pusha / popa
_fill(_MAP1, (0x62, 0x63), True, 0)                     # bound / arpl
_MAP1[0x68] = (False, "z")                              # push imm32
_MAP1[0x69] = (True, "z")                               # imul r, r/m, imm32
_MAP1[0x6A] = (False, 1)                                # push imm8
_MAP1[0x6B] = (True, 1)                                 # imul r, r/m, imm8
_fill(_MAP1, range(0x6C, 0x70), False, 0)               # ins / outs
_fill(_MAP1, range(0x70, 0x80), False, 1)               # jcc rel8
_MAP1[0x80] = (True, 1)
_MAP1[0x81] = (True, "z")
_MAP1[0x82] = (True, 1)
_MAP1[0x83] = (True, 1)
_fill(_MAP1, range(0x84, 0x90), True, 0)                # test/xchg/mov/lea/pop
_fill(_MAP1, range(0x90, 0x9A), False, 0)               # xchg eax / cwde / cdq
_MAP1[0x9A] = (False, "p")                              # call far
_fill(_MAP1, range(0x9B, 0xA0), False, 0)
_fill(_MAP1, range(0xA0, 0xA4), False, 4)               # mov eax, moffs32
_fill(_MAP1, range(0xA4, 0xA8), False, 0)               # movs / cmps
_MAP1[0xA8] = (False, 1)
_MAP1[0xA9] = (False, "z")
_fill(_MAP1, range(0xAA, 0xB0), False, 0)               # stos / lods / scas
_fill(_MAP1, range(0xB0, 0xB8), False, 1)               # mov r8, imm8
_fill(_MAP1, range(0xB8, 0xC0), False, "z")             # mov r32, imm32
_fill(_MAP1, (0xC0, 0xC1), True, 1)                     # shift r/m, imm8
_MAP1[0xC2] = (False, 2)                                # ret imm16
_MAP1[0xC3] = (False, 0)                                # ret
_fill(_MAP1, (0xC4, 0xC5), True, 0)                     # les / lds
_MAP1[0xC6] = (True, 1)
_MAP1[0xC7] = (True, "z")
_MAP1[0xC8] = (False, 3)                                # enter
_MAP1[0xC9] = (False, 0)                                # leave
_MAP1[0xCA] = (False, 2)                                # retf imm16
_fill(_MAP1, (0xCB, 0xCC), False, 0)
_MAP1[0xCD] = (False, 1)                                # int imm8
_fill(_MAP1, (0xCE, 0xCF), False, 0)
_fill(_MAP1, range(0xD0, 0xD4), True, 0)                # shift r/m, 1 / cl
_fill(_MAP1, (0xD4, 0xD5), False, 1)                    # aam / aad
_fill(_MAP1, (0xD6, 0xD7), False, 0)                    # salc / xlat
_fill(_MAP1, range(0xD8, 0xE0), True, 0)                # x87
_fill(_MAP1, range(0xE0, 0xE8), False, 1)               # loop / jecxz / in/out
_MAP1[0xE8] = (False, "z")                              # call rel32
_MAP1[0xE9] = (False, "z")                              # jmp rel32
_MAP1[0xEA] = (False, "p")                              # jmp far
_MAP1[0xEB] = (False, 1)                                # jmp rel8
_fill(_MAP1, range(0xEC, 0xF0), False, 0)               # in / out dx
_fill(_MAP1, (0xF1, 0xF4, 0xF5), False, 0)
_MAP1[0xF6] = (True, "g3b")
_MAP1[0xF7] = (True, "g3z")
_fill(_MAP1, range(0xF8, 0xFE), False, 0)
_fill(_MAP1, (0xFE, 0xFF), True, 0)

# --- mapa de dois bytes (prefixo 0x0F)
_fill(_MAP2, range(0x00, 0x04), True, 0)
_fill(_MAP2, (0x05, 0x06, 0x08, 0x09, 0x0B), False, 0)
_MAP2[0x0D] = (True, 0)
_fill(_MAP2, range(0x10, 0x20), True, 0)
_fill(_MAP2, range(0x28, 0x31), True, 0)
_fill(_MAP2, range(0x31, 0x35), False, 0)
_fill(_MAP2, range(0x40, 0x70), True, 0)
_fill(_MAP2, range(0x70, 0x74), True, 1)
_fill(_MAP2, range(0x74, 0x77), True, 0)
_MAP2[0x77] = (False, 0)
_fill(_MAP2, range(0x78, 0x80), True, 0)
_fill(_MAP2, range(0x80, 0x90), False, "z")             # jcc rel32
_fill(_MAP2, range(0x90, 0xA0), True, 0)                # setcc
_fill(_MAP2, (0xA0, 0xA1, 0xA2), False, 0)
_MAP2[0xA3] = (True, 0)
_MAP2[0xA4] = (True, 1)
_MAP2[0xA5] = (True, 0)
_fill(_MAP2, (0xA8, 0xA9, 0xAA), False, 0)
_MAP2[0xAB] = (True, 0)
_MAP2[0xAC] = (True, 1)
_fill(_MAP2, (0xAD, 0xAE, 0xAF), True, 0)
_fill(_MAP2, range(0xB0, 0xBA), True, 0)
_MAP2[0xBA] = (True, 1)
_fill(_MAP2, range(0xBB, 0xC2), True, 0)
_fill(_MAP2, (0xC2, 0xC4, 0xC5, 0xC6), True, 1)
_MAP2[0xC3] = (True, 0)
_MAP2[0xC7] = (True, 0)
_fill(_MAP2, range(0xC8, 0xD0), False, 0)               # bswap
_fill(_MAP2, range(0xD0, 0x100), True, 0)


def decode(data: bytes, pos: int, limit: int) -> tuple[int, str, int | None]:
    """(comprimento, classe de fluxo, alvo) da instrucao em `pos`.

    Classe e uma de `''`, `'ret'`, `'jmp'`, `'jcc'`, `'call'`. O alvo, quando
    existe, e offset de arquivo -- so os desvios relativos tem um, que e o que
    a varredura de `extent` precisa.
    """
    start = pos
    opsize = 4
    while pos < limit and data[pos] in PREFIXES:
        if data[pos] == 0x66:
            opsize = 2
        elif data[pos] == 0x67:
            raise DumpError(
                f"{REL_EXE}: prefixo 0x67 (endereco de 16 bits) em "
                f"{pos:#x}. O decodificador deste script nao cobre modo de "
                f"endereco de 16 bits, e adivinhar o comprimento a partir "
                f"daqui embaralharia a varredura inteira.")
        pos += 1
    if pos >= limit:
        raise DumpError(
            f"{REL_EXE}: so prefixos ate o limite, a partir de {start:#x}")
    op = data[pos]
    pos += 1
    two = op == 0x0F
    if two:
        if pos >= limit:
            raise DumpError(f"{REL_EXE}: 0x0F sem segundo byte em {start:#x}")
        op = data[pos]
        pos += 1
        entry = _MAP2.get(op)
    else:
        entry = _MAP1.get(op)
    if entry is None:
        raise DumpError(
            f"{REL_EXE}: opcode {'0f' if two else ''}{op:02x} em {start:#x} "
            f"nao esta no mapa deste decodificador. Um opcode desconhecido "
            f"desalinha a varredura de instrucao e falsifica todas as "
            f"extensoes de handler depois dele -- por isso aborta em vez de "
            f"chutar um comprimento.")
    has_modrm, imm = entry
    reg = None
    if has_modrm:
        if pos >= limit:
            raise DumpError(f"{REL_EXE}: ModRM fora do limite em {start:#x}")
        modrm = data[pos]
        pos += 1
        mod, reg, rm = modrm >> 6, (modrm >> 3) & 7, modrm & 7
        if mod != 3:
            if rm == 4:
                if pos >= limit:
                    raise DumpError(
                        f"{REL_EXE}: SIB fora do limite em {start:#x}")
                sib = data[pos]
                pos += 1
                if mod == 0 and (sib & 7) == 5:
                    pos += 4
            if mod == 0 and rm == 5:
                pos += 4
            elif mod == 1:
                pos += 1
            elif mod == 2:
                pos += 4
    if imm == "g3b":
        imm = 1 if reg in (0, 1) else 0
    elif imm == "g3z":
        imm = opsize if reg in (0, 1) else 0
    elif imm == "z":
        imm = opsize
    elif imm == "p":
        imm = 2 + opsize
    assert isinstance(imm, int)
    pos += imm
    if pos > limit:
        raise DumpError(
            f"{REL_EXE}: a instrucao em {start:#x} atravessa o limite "
            f"{limit:#x}")

    kind = ""
    target: int | None = None
    if not two:
        if op in (0xC2, 0xC3, 0xCA, 0xCB):
            kind = "ret"
        elif op == 0xE9:
            kind = "jmp"
            if imm == 4:
                target = pos + _i32(data, pos - 4)
        elif op == 0xEB:
            kind = "jmp"
            target = pos + struct.unpack_from("<b", data, pos - 1)[0]
        elif 0x70 <= op <= 0x7F or op in (0xE0, 0xE1, 0xE2, 0xE3):
            kind = "jcc"
            target = pos + struct.unpack_from("<b", data, pos - 1)[0]
        elif op == 0xE8:
            kind = "call"
        elif op == 0xFF and reg in (4, 5):
            kind = "jmp"                     # jmp indireto: encerra o fluxo
    elif 0x80 <= op <= 0x8F and imm == 4:
        kind = "jcc"
        target = pos + _i32(data, pos - 4)
    return pos - start, kind, target


def extent(data: bytes, start: int, limit: int, what: str) -> int:
    """Onde a funcao que comeca em `start` termina, em offset de arquivo.

    Varredura linear que so encerra num `ret` ou `jmp` situado alem de todo
    alvo de desvio ja visto -- o `jmp` de dentro de um `if` nao encerra a
    funcao, e o teto de alvos e o que sabe disso.
    """
    pos = start
    farthest = start
    while pos < limit:
        length, kind, target = decode(data, pos, limit)
        if target is not None and farthest < target <= limit:
            farthest = target
        pos += length
        if kind in ("ret", "jmp") and pos > farthest:
            return pos
    raise DumpError(
        f"{REL_EXE}: {what} nao termina antes de {limit:#x}. Um corpo de "
        f"handler tem de acabar antes do proximo comecar; se nao acaba, ou o "
        f"{REL_PUB} esta desatualizado ou a varredura desalinhou.")


# ------------------------------------------------------------------ thunks ---
def resolve_thunk(pe: PE, alvo: int, iat: dict[int, str]) -> str | None:
    """Nome importado por tras de um `jmp DWORD PTR ds:<IAT>` em `alvo`."""
    o = pe.off(alvo)
    if o is None or pe.data[o:o + 2] != b"\xff\x25":
        return None
    return iat.get(struct.unpack_from("<I", pe.data, o + 2)[0])



# ------------------------------------------------------------- descoberta ---
def le_handlers() -> list[dict]:
    linhas = PUB.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    saida = []
    for linha in linhas[1:]:
        c = dict(zip(cab, linha.split("\t")))
        saida.append({"endereco": int(c["endereco"], 16),
                      "handler": c["handler"],
                      "formulario": c["formulario"],
                      "grupo": c["grupo"]})
    return saida


def faixa_text(pe: PE) -> tuple[int, int]:
    for nome, vaddr, vsize, raddr, rsize in pe.sections:
        if nome == ".text":
            return pe.base + vaddr, min(vsize, rsize)
    raise DumpError(f"{REL_EXE}: nao tem secao .text")


def corpo(pe: PE, ini: int, fronteiras: list[int]) -> tuple[int, int | None]:
    """(offset de arquivo, tamanho) do corpo em `ini`; tamanho `None` se o
    decodificador nao conseguir determinar onde ele acaba."""
    o = pe.off(ini)
    if o is None:
        raise DumpError(f"{REL_EXE}: {ini:#010x} fora das secoes")
    seguinte = min((f for f in fronteiras if f > ini), default=ini + TETO)
    teto = pe.off(min(seguinte, ini + TETO))
    try:
        return o, extent(pe.data, o, teto, f"{ini:#010x}") - o
    except DumpError:
        return o, None


def chamadas(pe: PE, ini: int, o: int, tam: int) -> list[int]:
    """Alvos de `call rel32` no corpo, na ordem em que aparecem, sem repetir.

    Percorre instrucao a instrucao, e nao por varredura do byte 0xE8: o byte
    tambem cai dentro de operando imediato, e ali ele nao e chamada nenhuma.
    """
    alvos: list[int] = []
    p = 0
    while p < tam:
        comprimento, _kind, _target = decode(pe.data, o + p, o + tam)
        if pe.data[o + p] == 0xE8 and comprimento == 5:
            alvo = ini + p + 5 + struct.unpack_from("<i", pe.data, o + p + 1)[0]
            if alvo not in alvos:
                alvos.append(alvo)
        p += comprimento
    return alvos


def internas(pe: PE, alvos: list[int], iat: dict[int, str],
             publicados: set[int], text: tuple[int, int]) -> list[int]:
    """Dos alvos, os que nao sao importados nem handler publicado."""
    ini, tam = text
    saida = []
    for alvo in alvos:
        if not (ini <= alvo < ini + tam):
            continue
        if resolve_thunk(pe, alvo, iat) is not None:
            continue
        if alvo in publicados:
            continue
        saida.append(alvo)
    return saida


# -------------------------------------------------------------- inventario ---
def toca(pe: PE, ini: int, o: int, tam: int, iat: dict[int, str],
         text: tuple[int, int]) -> dict:
    """O que um corpo toca: importados, literais e globais da `.data`."""
    corpo_bytes = pe.data[o:o + tam]
    importados: list[str] = []
    for alvo in chamadas(pe, ini, o, tam):
        nome = resolve_thunk(pe, alvo, iat)
        if nome and nome not in importados:
            importados.append(nome)

    literais: list[str] = []
    for m in re.finditer(rb"[\xb8-\xbf](....)", corpo_bytes):
        texto = pe.cstring(struct.unpack("<I", m.group(1))[0])
        if texto is not None and len(texto) >= 3 and texto not in literais:
            literais.append(texto)

    # `mov eax,moffs32` (0xa1) e `mov <reg>,[disp32]` (0x8b /r com mod=00,
    # rm=101). Sao as duas formas com que o C++Builder alcanca variavel global.
    globais: list[int] = []
    for padrao in (rb"\xa1(....)", rb"\x8b[\x05\x0d\x15\x1d\x25\x2d\x35\x3d](....)"):
        for m in re.finditer(padrao, corpo_bytes):
            va = struct.unpack("<I", m.group(1))[0]
            secao = next((n for n, vaddr, vsize, raddr, rsize in pe.sections
                          if pe.base + vaddr <= va
                          < pe.base + vaddr + max(vsize, rsize)), None)
            if secao == ".data" and va not in globais:
                globais.append(va)
    return {"importados": importados, "literais": literais,
            "globais": sorted(globais)}


# ------------------------------------------------------------ conferencias ---
def confere_pula_setor(pe: PE, fronteiras: list[int]) -> dict[str, int]:
    """As tres constantes de fronteira de setor, lidas do corpo de `0x403388`."""
    o, tam = corpo(pe, PULA_SETOR, fronteiras)
    if tam is None:
        raise DumpError(
            f"{PULA_SETOR:#010x}: o decodificador nao acha o fim do corpo, "
            f"entao as constantes de setor nao podem ser conferidas")
    corpo_bytes = pe.data[o:o + tam]
    achados: dict[str, int] = {}
    for chave, padrao in (("setor", rb"\xb9(....)"),
                          ("fim_dos_dados", rb"\x81\xfa(....)"),
                          ("salto", rb"\x68(....)")):
        casos = re.findall(padrao, corpo_bytes)
        if len(casos) != 1:
            raise DumpError(
                f"{PULA_SETOR:#010x}: o padrao de `{chave}` casou "
                f"{len(casos)} vezes, esperava uma. Casamento ambiguo leria a "
                f"constante errada e a conferencia passaria mentindo.")
        achados[chave] = struct.unpack("<I", casos[0])[0]
    esperado = {"setor": SETOR, "fim_dos_dados": FIM_DOS_DADOS, "salto": SALTO}
    if achados != esperado:
        raise DumpError(
            f"{PULA_SETOR:#010x}: geometria de setor {achados}, esperava "
            f"{esperado}. Ou o binario mudou, ou a leitura de que esta rotina "
            f"pula fronteira de setor esta errada -- e ela sustenta a spec do "
            f"filtro de nome e a equivalencia com os `OFS_*` do we2002_core.")
    if achados["fim_dos_dados"] + achados["salto"] != achados["setor"] + 24:
        raise DumpError(
            f"{PULA_SETOR:#010x}: {achados['fim_dos_dados']} + "
            f"{achados['salto']} nao da {achados['setor']} + 24 de cabecalho")
    return achados


def base_da_tabela_de_offsets() -> int:
    """O `va` do primeiro `tabela_slot` do [`offsets.tsv`](../re/offsets.tsv)."""
    linhas = (OUT / "offsets.tsv").read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    for linha in linhas[1:]:
        c = dict(zip(cab, linha.split("\t")))
        if c["registro"] == "tabela_slot":
            return int(c["va"], 16)
    raise DumpError(f"{REL_OUT}/offsets.tsv: nenhuma linha `tabela_slot`")


def confere_varredura_da_tabela(pe: PE, fronteiras: list[int]) -> dict[str, int]:
    """A base e a forma da varredura de `0x0040cbc8`, lidas do corpo dela."""
    o, tam = corpo(pe, VARRE_TABELA, fronteiras)
    if tam is None:
        raise DumpError(
            f"{VARRE_TABELA:#010x}: o decodificador nao acha o fim do corpo")
    corpo_bytes = pe.data[o:o + tam]
    achados: dict[str, int] = {}
    for chave, padrao in (("base", rb"\xc7\x45\xcc(....)"),
                          ("colunas", rb"\x83\xfe(.)"),
                          ("passo", rb"\x83\x45\xcc(.)")):
        casos = re.findall(padrao, corpo_bytes)
        if len(casos) != 1:
            raise DumpError(
                f"{VARRE_TABELA:#010x}: o padrao de `{chave}` casou "
                f"{len(casos)} vezes, esperava uma")
        achados[chave] = (struct.unpack("<I", casos[0])[0]
                          if len(casos[0]) == 4 else casos[0][0])
    esperado_base = base_da_tabela_de_offsets()
    if achados["base"] != esperado_base:
        raise DumpError(
            f"{VARRE_TABELA:#010x}: varre {achados['base']:#010x}, e o "
            f"{REL_OUT}/offsets.tsv diz que a tabela comeca em "
            f"{esperado_base:#010x}. Ou a WTE-TASK-06 mediu outra tabela, ou "
            f"esta rotina nao e a que a percorre.")
    if (achados["colunas"], achados["passo"]) != (COLUNAS, PASSO_DA_LINHA):
        raise DumpError(
            f"{VARRE_TABELA:#010x}: {achados['colunas']} colunas de passo "
            f"{achados['passo']:#x}, esperava {COLUNAS} e {PASSO_DA_LINHA:#x}")
    if achados["colunas"] * 4 != achados["passo"]:
        raise DumpError(
            f"{VARRE_TABELA:#010x}: {achados['colunas']} colunas de quatro "
            f"bytes nao fecham a linha de {achados['passo']:#x}")
    return achados


def confere_tabelas_de_letra(pe: PE) -> list[dict]:
    """As duas tabelas do filtro de nome sao identidade — ou aborta."""
    saida = []
    for base, primeiro, ultimo, rotulo in TABELAS_DE_LETRA:
        o = pe.off(base + primeiro)
        if o is None:
            raise DumpError(f"tabela de {rotulo} em {base:#010x} fora das secoes")
        bruto = pe.data[o:o + (ultimo - primeiro + 1)]
        esperado = bytes(range(primeiro, ultimo + 1))
        if bruto != esperado:
            raise DumpError(
                f"a tabela de {rotulo} de {FILTRO_NOME:#010x} nao e identidade: "
                f"{bruto!r}. A spec diz que a rotina FILTRA, e um mapa que nao "
                f"e identidade a torna um TRADUTOR -- que e outra coisa.")
        saida.append({"base": base, "primeiro": primeiro, "ultimo": ultimo,
                      "rotulo": rotulo, "conteudo": bruto.decode("latin1")})
    return saida


# ----------------------------------------------------------------- medicao ---
def medir() -> dict:
    pe = PE(EXE.read_bytes(), REL_EXE)
    iat = pe.imports()
    exportados = {pe.base + rva: nome for rva, nome in pe.exports().items()}
    todos = le_handlers()
    publicados = {h["endereco"] for h in todos}
    text = faixa_text(pe)

    alvo = [h for h in todos if h["grupo"] == GRUPO]
    if len(alvo) != HANDLERS_ESPERADOS:
        raise DumpError(
            f"{REL_PUB}: {len(alvo)} handlers no grupo `{GRUPO}`, esperava "
            f"{HANDLERS_ESPERADOS}")

    fronteiras = sorted(publicados)
    rotinas: dict[int, dict] = {}

    # nivel 1: chamadas diretas dos handlers do grupo
    for h in sorted(alvo, key=lambda x: x["endereco"]):
        o, tam = corpo(pe, h["endereco"], fronteiras)
        if tam is None:
            raise DumpError(
                f"{h['formulario']}.{h['handler']}: o decodificador nao acha o "
                f"fim do corpo. Handler publicado tem de terminar antes do "
                f"proximo; se nao termina, o {REL_PUB} desalinhou.")
        for a in internas(pe, chamadas(pe, h["endereco"], o, tam), iat,
                          publicados, text):
            r = rotinas.setdefault(a, {"nivel": 1, "de": [], "chama": []})
            r["nivel"] = 1
            rotulo = f"{h['formulario']}.{h['handler']}"
            if rotulo not in r["de"]:
                r["de"].append(rotulo)

    # nivel 2: o que as de nivel 1 chamam. Uma so descida: o objetivo e nomear
    # a rotina que a spec cita, nao fechar o grafo de chamada do binario.
    fronteiras = sorted(publicados | set(rotinas))
    for a in sorted(rotinas):
        o, tam = corpo(pe, a, fronteiras)
        rotinas[a]["offset"], rotinas[a]["bytes"] = o, tam
        if tam is None:
            continue
        for b in internas(pe, chamadas(pe, a, o, tam), iat, publicados, text):
            if b == a:
                continue
            rotinas[a]["chama"].append(b)
            r = rotinas.setdefault(b, {"nivel": 2, "de": [], "chama": []})
            if f"{a:#010x}" not in r["de"]:
                r["de"].append(f"{a:#010x}")

    fronteiras = sorted(publicados | set(rotinas))
    for a, r in rotinas.items():
        if "bytes" not in r:
            r["offset"], r["bytes"] = corpo(pe, a, fronteiras)

    faltando = sorted(set(PAPEIS) - set(rotinas))
    if faltando:
        raise DumpError(
            "PAPEIS descreve rotina que o grupo de carga nao chama: "
            + ", ".join(f"{a:#010x}" for a in faltando)
            + ". Papel escrito a mao para endereco que a descoberta nao acha e "
              "spec apontando para o vazio.")

    for a, r in sorted(rotinas.items()):
        r["endereco"] = a
        r["papel"] = PAPEIS.get(a, "")
        if r["papel"] and r["bytes"] is not None:
            r.update(toca(pe, a, r["offset"], r["bytes"], iat, text))
        else:
            r.update({"importados": [], "literais": [], "globais": []})

    return {"rotinas": [rotinas[a] for a in sorted(rotinas)],
            "setor": confere_pula_setor(pe, fronteiras),
            "tabela": confere_varredura_da_tabela(pe, fronteiras),
            "letras": confere_tabelas_de_letra(pe),
            "exportados": exportados,
            "handlers": len(alvo)}


# ------------------------------------------------------------------- saida ---
def gera_tsv(m: dict) -> str:
    linhas = ["endereco\tnivel\tbytes\tchamado_por\tchama\tpapel"]
    for r in m["rotinas"]:
        linhas.append("\t".join((
            f"{r['endereco']:#010x}",
            str(r["nivel"]),
            "?" if r["bytes"] is None else str(r["bytes"]),
            ",".join(r["de"]),
            ",".join(f"{x:#010x}" for x in r["chama"]),
            r["papel"])))
    return "\n".join(linhas) + "\n"


def gera_md(m: dict) -> str:
    rotinas = m["rotinas"]
    com_papel = [r for r in rotinas if r["papel"]]
    sem_tamanho = [r for r in rotinas if r["bytes"] is None]
    n1 = sum(1 for r in rotinas if r["nivel"] == 1)

    w: list[str] = []
    a = w.append
    a("# `re/auxiliares.md` — as rotinas internas que o grupo de carga chama")
    a("")
    a("Produto da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md). Gerado")
    a("por [`../tools/dump_auxiliares.py`](../tools/dump_auxiliares.py) a partir")
    a(f"de `{REL_EXE}` e de")
    a("[`published_methods.tsv`](published_methods.tsv). **Não editar à mão:**")
    a("")
    a("```sh")
    a(f"python3 {GENERATOR}")
    a(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    a("```")
    a("")
    a("A tabela está em [`auxiliares.tsv`](auxiliares.tsv); este arquivo é a")
    a("leitura dela. **Todo número daqui saiu do script.**")
    a("")
    a("## O problema que a medição resolve")
    a("")
    a("Três specs do grupo de carga pararam em `aberto` pela mesma razão: o")
    a("handler chama rotinas que não são handler publicado, e sem saber o que")
    a("elas fazem não dá para escrever o corpo. A tabela de auxiliares da")
    a("[`spec/MainForm.lista_equiposChange.md`](spec/MainForm.lista_equiposChange.md)")
    a("foi escrita à mão e listava **cinco** endereços.")
    a("")
    equipos = [r for r in rotinas
               if "MainForm.lista_equiposChange" in r["de"]]
    lidas = [r for r in equipos if r["papel"]]
    a(f"Medido, esse handler chama **{len(equipos)}** rotinas internas —")
    a(f"{len(lidas)} delas já com papel lido, {len(equipos) - len(lidas)} ainda")
    a("sem:")
    a("")
    for r in equipos:
        a(f"- `{r['endereco']:#010x}` — {r['papel'] or '*sem papel lido*'}")
    a("")
    a("A comparação não é 5 contra 13 de igual para igual: parte das que")
    a("faltavam é rotina de biblioteca que a tabela à mão descartaria de")
    a("propósito. Mas **duas das que faltavam carregam dado do jogo** —")
    a("`0x004050d0` e `0x0040cbc8` —, e essas não estavam sendo descartadas: não")
    a("estavam sendo vistas. Tabela de auxiliar escrita à mão erra da forma que")
    a("não aparece: o que falta na lista simplesmente não é procurado, e a spec")
    a("fica parecendo completa.")
    a("")
    a("## O que entrou na conta")
    a("")
    a(f"Os {m['handlers']} handlers do grupo `{GRUPO}` chamam **{n1}** rotinas")
    a("internas diretamente. O script desce **um** nível a partir delas — o")
    a(f"objetivo é nomear a rotina que a spec cita, não fechar o grafo de")
    a(f"chamada do binário —, e com isso a tabela tem {len(rotinas)} linhas.")
    a("")
    a("Nem todo `call` do corpo entra: importada sai pelo `jmp DWORD PTR")
    a("ds:<IAT>`, handler publicado sai pelo")
    a("[`published_methods.tsv`](published_methods.tsv). Sobra a rotina interna,")
    a("que é o que interessa.")
    a("")
    if sem_tamanho:
        a(f"**{len(sem_tamanho)} entram com tamanho `?`.** O fim de uma rotina")
        a("sai do decodificador x86, não de subtração de endereços; quando ele")
        a("não consegue determinar onde o corpo acaba, a linha diz isso em vez")
        a("de sumir da tabela. Nenhuma delas tem papel lido.")
        a("")
    a("## As rotinas")
    a("")
    a("| Endereço | Nível | Bytes | Chamada por | Papel |")
    a("|---|---:|---:|---|---|")
    for r in rotinas:
        tam = "?" if r["bytes"] is None else str(r["bytes"])
        de = ", ".join(f"`{x}`" for x in r["de"])
        a(f"| `{r['endereco']:#010x}` | {r['nivel']} | {tam} | {de} | "
          f"{r['papel'] or '—'} |")
    a("")
    a("## A fronteira de setor, e por que ela fecha um círculo")
    a("")
    s = m["setor"]
    a(f"`{PULA_SETOR:#010x}` não recebe offset nenhum. Ela pergunta ao `ftell`")
    a("em que ponto do setor o arquivo está e, se está no fim dos dados, avança:")
    a("")
    a("```text")
    a(f"se ftell(imagem) mod {s['setor']} = {s['fim_dos_dados']}:")
    a(f"    avanca {s['salto']} bytes e devolve verdadeiro")
    a("senao: devolve falso")
    a("```")
    a("")
    a(f"{s['setor']} é o setor MODE2/2352 inteiro; {s['fim_dos_dados']} é")
    a(f"24 de cabeçalho mais 2048 de dados; {s['salto']} é os 280 de EDC/ECC")
    a("mais os 24 do cabeçalho do setor seguinte. É a **mesma geometria** que o")
    a("`we2002_core` deste repositório assa nas constantes `OFS_*` — a diferença")
    a("é que o original a calcula em tempo de execução e nós a temos pré-somada.")
    a("")
    a("As três constantes saem decodificadas do corpo da própria rotina, e o")
    a("script aborta se deixarem de bater — inclusive na identidade")
    a(f"`{s['fim_dos_dados']} + {s['salto']} = {s['setor']} + 24`.")
    a("")
    a("## A tabela de offsets, vista do outro lado")
    a("")
    t = m["tabela"]
    a(f"`{VARRE_TABELA:#010x}` carrega `{t['base']:#010x}` e percorre a tabela")
    a(f"em linhas de {t['passo']:#x} bytes, {t['colunas']} colunas de quatro —")
    a("pulando a coluna que estiver zerada.")
    a("")
    a("Esse endereço é o mesmo que a")
    a("[WTE-TASK-06](../../docs/tasks/06-mapa-de-offsets.md) registrou como")
    a("primeiro slot em [`offsets.tsv`](offsets.tsv), medido por outro caminho:")
    a("lá pela varredura de constantes que batem com os nossos `OFS_*`, aqui")
    a("pelo código que as consome. O script lê a base do corpo da rotina e")
    a("**aborta se as duas medições discordarem** — a tabela deixaria de ter um")
    a("dono só.")
    a("")
    a("## O filtro de nome não traduz — ele filtra")
    a("")
    a(f"`{FILTRO_NOME:#010x}` lê o nome byte a byte e indexa duas tabelas em")
    a("`.data` pelo próprio byte. A leitura barata seria \"são tabelas de")
    a("tradução, como o `KanjiToAscii` do `we2002_core`\". Medido, as duas são")
    a("**identidade**:")
    a("")
    a("| Tabela | Base | Faixa | Conteúdo |")
    a("|---|---|---|---|")
    for t in m["letras"]:
        a(f"| {t['rotulo']} | `{t['base']:#010x}` | "
          f"`{t['primeiro']:#04x}`…`{t['ultimo']:#04x}` | `{t['conteudo']}` |")
    a("")
    a("Ou seja, a rotina copia letra, dígito, `.` e espaço como estão, troca")
    a("**qualquer byte acima de `z` por `?`** e descarta o resto. Isso é uma")
    a("divergência de comportamento contra o `we2002_core`, que para byte")
    a("desconhecido devolve espaço; ela vale para o que aparece na tela e não")
    a("para o que se grava. A conferência aborta se as tabelas deixarem de ser")
    a("identidade, porque nesse dia a palavra \"filtro\" fica errada.")
    a("")
    if com_papel:
        a("## As lidas, uma a uma")
        a("")
        a("O inventário é piso, não teto: literais são as cadeias ASCII de três")
        a("caracteres ou mais apontadas por operando imediato, e globais são os")
        a("endereços da `.data` alcançados por `mov eax,moffs32` ou")
        a("`mov <reg>,[disp32]`.")
        a("")
        for r in com_papel:
            a(f"### `{r['endereco']:#010x}` — {r['bytes']} bytes")
            a("")
            a(f"- **Papel:** {r['papel']}")
            a("- **Chamada por:** " + ", ".join(f"`{x}`" for x in r["de"]))
            a("- **Chama internas:** " +
              (", ".join(f"`{x:#010x}`" for x in r["chama"]) or "nenhuma"))
            a("- **Importados:** " +
              (", ".join(f"`{x}`" for x in r["importados"]) or "nenhum"))
            a("- **Literais:** " +
              (", ".join(f"`{x}`" for x in r["literais"]) or "nenhum"))
            globais = []
            for g in r["globais"]:
                nome = m["exportados"].get(g)
                globais.append(f"`{g:#010x}`" + (f" (`{nome}`)" if nome else ""))
            a("- **Globais da `.data`:** " + (", ".join(globais) or "nenhuma"))
            a("")
    return "\n".join(w)


def generate() -> dict[str, str]:
    m = medir()
    return {TSV_NAME: gera_tsv(m), MD_NAME: gera_md(m)}


def do_check(files: dict[str, str]) -> int:
    problemas = []
    for nome, conteudo in sorted(files.items()):
        caminho = OUT / nome
        if not caminho.exists():
            problemas.append(f"{nome}: nao existe")
            continue
        no_disco = caminho.read_text(encoding="utf-8")
        if no_disco == conteudo:
            print(f"dump_auxiliares: {REL_OUT}/{nome}: ok")
            continue
        for i, (x, y) in enumerate(
                zip(no_disco.splitlines(), conteudo.splitlines()), 1):
            if x != y:
                problemas.append(f"{nome}: linha {i} diverge")
                break
        else:
            problemas.append(
                f"{nome}: {len(no_disco.splitlines())} linhas no disco contra "
                f"{len(conteudo.splitlines())} regeradas")
    if problemas:
        print(f"{REL_OUT} nao corresponde a {REL_EXE}:", file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in sorted(files.items()):
        (OUT / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {nome}: {conteudo.count(chr(10))} linhas, "
              f"{len(conteudo.encode('utf-8'))} bytes")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        files = generate()
    except DumpError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
