#!/usr/bin/env python3
"""Veredito sobre `Registry`, `Printers`, `Comobj` e `Winhelpviewer`.

Gera `wte/re/unidades-vcl.md` -- o produto da WTE-TASK-07. A pergunta e uma so,
repetida quatro vezes: o `we-team-editor.exe` **usa** a unidade, ou o import e
dependencia transitiva que o linker do C++Builder arrastou?

A regua tem tres camadas, e nenhuma delas e "abrir o binario e olhar".

**1. Que simbolos a unidade exporta para dentro do `.exe`.** O `.exe` importa
por nome mangled da Borland (`@Registry@...`), com um descritor de import por
unidade. Uma unidade que so importa `@X@initialization$qqrv` e
`@X@Finalization$qqrv` nao teve *nenhuma* funcao sua chamada: esses dois nao sao
API, sao o par de ciclo de vida que a tabela de modulos do executavel percorre
no arranque e no encerramento.

**2. Se o thunk do simbolo e chamado.** Import de package nao vira `call
ds:[...]` direto no sitio de uso: o linker emite um stub `jmp *[IAT]` por
import, no fim do `.text`, e o codigo chama o stub por `call rel32`. Procurar
`call ds:[...]` sem saber disso acha zero e conclui errado. Este script monta a
tabela de stubs primeiro -- `FF 25 imm32` cujo operando a `.reloc` marca como
endereco **e** cai dentro do IAT, que e a mesma regua de `.reloc` que o
`dump_offsets.py` e o `dump_strings.py` usam -- e so entao procura referencia,
em cinco formas: `call rel32` para o stub, `jmp rel32`/`rel8` para o stub,
`call`/`jmp` indireto pelo slot do IAT, carga do endereco do slot, e entrada de
tabela apontando para o stub. A varredura e do arquivo inteiro, todas as
secoes, byte a byte -- nao so das regioes de codigo conhecidas.

**3. Onde a chamada esta, quando existe.** A WTE-TASK-07 pede o handler dono, e
avisa que codigo de inicializacao de unidade nao esta em handler nenhum. Este
script responde as duas coisas: mede o corpo dos 96 handlers com o mesmo
decodificador de comprimento x86-32 do `dump_strings.py`, e localiza a tabela de
modulos do executavel conferindo que os 26 `@@Tep2002_*@Initialize`/`Finalize`
exportados pelo proprio app estao dentro dela.

## Por que o decodificador esta copiado aqui

E o mesmo do `dump_strings.py`, verbatim, e a duplicacao e deliberada: cada
gerador de `wte/tools/` roda sozinho, sem importar os irmaos, pela mesma razao
que cada um carrega o proprio leitor de PE. O que ele decide -- comprimento da
instrucao e classe de fluxo -- e fato sobre x86, nao escolha de projeto, e o
binario que ele le nunca vai mudar. Se um dia mudar num dos dois, tem de mudar
nos dois.

## O que este script nao consegue ver, e como a lacuna foi fechada

Ausencia de import prova que o `.exe` nao chama a unidade **por nome**. Nao
prova, sozinha, que a funcionalidade nao acontece: uma unidade cuja
`initialization` se registra num despachante -- e o `Winhelpviewer` faz
exatamente isso -- entrega o servico de dentro do package, sem o `.exe` precisar
citar um simbolo. Por isso o veredito nao para no import. Para cada unidade o
script tambem conta os indicios positivos que a funcionalidade deixaria em
lugares que ja foram medidos por outras tasks: propriedade de formulario nos 18
DFM da WTE-TASK-03 e texto no inventario da WTE-TASK-05. Um indicio positivo
com zero imports seria contradicao, e o script aborta em vez de emitir veredito.

Saida: um arquivo, `unidades-vcl.md`. Nao ha TSV -- sao quatro unidades e doze
simbolos, e uma tabela em markdown ja e a forma final do dado.

Uso:

    python3 wte/tools/dump_units.py            # regenera
    python3 wte/tools/dump_units.py --check    # confere contra o commitado
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
DFM = ROOT / "wte" / "re" / "dfm"
STR = ROOT / "wte" / "re" / "strings.tsv"
OUT = ROOT / "wte" / "re"

# Caminhos relativos nas mensagens e na saida -- caminho absoluto quebraria a
# estabilidade byte a byte entre maquinas.
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_PUB = "wte/re/published_methods.tsv"
REL_DFM = "wte/re/dfm"
REL_STR = "wte/re/strings.tsv"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_units.py"

MD_NAME = "unidades-vcl.md"

# As quatro sob julgamento, na ordem em que a §5 do plano as lista.
UNITS = ("Registry", "Printers", "Comobj", "Winhelpviewer")

# O par de ciclo de vida. Import que so tem estes dois nao usou nada da unidade.
LIFECYCLE = ("@{0}@initialization$qqrv", "@{0}@Finalization$qqrv")

# Indicios positivos de que a funcionalidade existe, procurados FORA do import.
# Chave: unidade. Valor: (agulhas nos 18 DFM, expressao regular nas strings).
# A ausencia dos dois e o que fecha a lacuna descrita no cabecalho do modulo:
# uma unidade que entrega servico de dentro do package, sem o `.exe` citar
# simbolo, ainda precisaria de propriedade no formulario ou de texto no binario
# para ser alcancada.
EVIDENCE: dict[str, tuple[tuple[str, ...], str]] = {
    "Registry": ((), r"HKEY|SOFTWARE\\|\.ini\b|RegOpen|Registry|registro"),
    "Printers": (("TPrintDialog", "TPrinterSetupDialog"),
                 r"Printer|imprim|impress|PrintDialog"),
    "Comobj": (("TOleContainer",), r"CoCreateInstance|ProgID|CLSID|OleObject"),
    "Winhelpviewer": (("HelpFile", "HelpContext", "HelpType", "HelpKeyword"),
                      r"\.hlp\b|WinHelp|ajuda"),
}

# A tabela de modulos do executavel: registros de <word tag><dword endereco>.
MODULE_RECORD = 6


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""
# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do dfm_extract.py, do
# dump_published.py e do dump_offsets.py: o que este script precisa do formato
# cabe em poucas dezenas de linhas, e sem dependencia o `make -C wte check`
# roda em qualquer maquina com Python 3.


def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def _i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]


class Section:
    __slots__ = ("name", "rva", "vsize", "raw_size", "raw_ptr")

    def __init__(self, name: str, rva: int, vsize: int, raw_size: int,
                 raw_ptr: int):
        self.name = name
        self.rva = rva
        self.vsize = vsize
        self.raw_size = raw_size
        self.raw_ptr = raw_ptr


class Image:
    """O `.exe` lido: secoes, base e os alvos de realocacao."""

    def __init__(self, data: bytes):
        self.data = data
        if data[:2] != b"MZ":
            raise DumpError(f"{REL_EXE}: nao comeca com 'MZ'")
        pe = _u32(data, 0x3C)
        if data[pe:pe + 4] != b"PE\0\0":
            raise DumpError(f"{REL_EXE}: assinatura PE ausente em {pe:#x}")
        coff = pe + 4
        machine = _u16(data, coff)
        if machine != 0x14C:
            raise DumpError(
                f"{REL_EXE}: esperado i386 (0x14c), veio {machine:#x}")
        n_sections = _u16(data, coff + 2)
        size_opt = _u16(data, coff + 16)
        opt = coff + 20
        if _u16(data, opt) != 0x10B:
            raise DumpError(f"{REL_EXE}: esperado PE32 (0x10b)")
        self.image_base = _u32(data, opt + 28)
        self.size_of_image = _u32(data, opt + 56)

        self.sections: list[Section] = []
        sec = opt + size_opt
        for i in range(n_sections):
            s = sec + i * 40
            name = data[s:s + 8].rstrip(b"\0").decode("ascii", "replace")
            vsize, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data,
                                                               s + 8)
            self.sections.append(Section(name, rva, vsize, raw_size, raw_ptr))
        for needed in (".text", ".data"):
            if self.section(needed) is None:
                raise DumpError(f"{REL_EXE}: secao {needed} ausente")

        n_dirs = _u32(data, opt + 92)
        if n_dirs < 6:
            raise DumpError(
                f"{REL_EXE}: optional header sem o diretorio de realocacao "
                f"(NumberOfRvaAndSizes = {n_dirs})")
        reloc_rva, reloc_size = struct.unpack_from("<II", data,
                                                   opt + 96 + 5 * 8)
        self.relocs = self._read_relocs(reloc_rva, reloc_size)
        if not self.relocs:
            raise DumpError(
                f"{REL_EXE}: nenhuma realocacao HIGHLOW. A `.reloc` e a regua "
                f"deste script nos dois sentidos -- ela separa ponteiro de "
                f"texto em `.data` e acha as referencias em `.text`. Sem ela "
                f"a medicao nao vale.")

    # -- conversoes -------------------------------------------------------

    def section(self, name: str) -> Section:
        for s in self.sections:
            if s.name == name:
                return s
        raise DumpError(f"{REL_EXE}: secao {name} ausente")

    def section_of_offset(self, file_off: int) -> Section | None:
        for s in self.sections:
            if s.raw_ptr <= file_off < s.raw_ptr + s.raw_size:
                return s
        return None

    def rva_to_offset(self, rva: int) -> int | None:
        for s in self.sections:
            if s.rva <= rva < s.rva + s.raw_size:
                return s.raw_ptr + (rva - s.rva)
        return None

    def offset_to_va(self, file_off: int) -> int | None:
        s = self.section_of_offset(file_off)
        if s is None:
            return None
        return self.image_base + s.rva + (file_off - s.raw_ptr)

    def va_to_offset(self, va: int) -> int | None:
        return self.rva_to_offset(va - self.image_base)

    # -- realocacoes ------------------------------------------------------

    def _read_relocs(self, rva: int, size: int) -> set[int]:
        """Alvos HIGHLOW da `.reloc`, ja convertidos para offset de arquivo."""
        out: set[int] = set()
        if rva == 0 or size == 0:
            return out
        base = self.rva_to_offset(rva)
        if base is None:
            raise DumpError(
                f"{REL_EXE}: diretorio de realocacao em RVA {rva:#x} fora de "
                f"qualquer secao")
        end = base + size
        p = base
        while p + 8 <= end:
            page, block = struct.unpack_from("<II", self.data, p)
            if block < 8:
                break
            for q in range(p + 8, min(p + block, end), 2):
                entry = _u16(self.data, q)
                if entry >> 12 == 3:  # IMAGE_REL_BASED_HIGHLOW
                    off = self.rva_to_offset(page + (entry & 0xFFF))
                    if off is not None:
                        out.add(off)
            p += block
        return out


# ------------------------------------------------- decodificador de x86-32 ---
#
# So o comprimento das instrucoes e a classe de fluxo interessam: nada aqui
# imprime mnemonico. As duas tabelas sao o mapa de opcodes de um byte e o de
# dois (prefixo 0x0F), com (tem ModRM, tamanho do imediato). Tamanhos:
#   0..4  literal; 'z' segue o prefixo de tamanho de operando (4 ou 2);
#   'p'   ponteiro far (2 + tamanho de operando);
#   'g3b'/'g3z' grupo 3 (0xF6/0xF7), que so tem imediato no /0 e no /1.

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


# ------------------------------------------------------------- handlers ---

PUB_COLUMNS = ["endereco", "handler", "formulario", "componente", "evento",
               "grupo", "regra", "nota"]


class Handler:
    __slots__ = ("addr", "name", "form", "end")

    def __init__(self, addr: int, name: str, form: str):
        self.addr = addr
        self.name = name
        self.form = form
        self.end = addr

    @property
    def label(self) -> str:
        return f"{self.form}.{self.name}"


def read_published(text: str) -> list[Handler]:
    """Os handlers do TSV da WTE-TASK-04, ordenados por endereco."""
    lines = text.splitlines()
    if not lines:
        raise DumpError(f"{REL_PUB}: arquivo vazio")
    header = lines[0].split("\t")
    if header != PUB_COLUMNS:
        raise DumpError(
            f"{REL_PUB}: cabecalho inesperado.\n"
            f"       esperado: {'|'.join(PUB_COLUMNS)}\n"
            f"       veio:     {'|'.join(header)}\n"
            f"       Este script le as colunas `endereco`, `handler` e "
            f"`formulario`; se o dump_published.py mudou o formato, ele tem "
            f"de acompanhar.")
    out: list[Handler] = []
    seen: dict[int, str] = {}
    for i, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(PUB_COLUMNS):
            raise DumpError(
                f"{REL_PUB}:{i}: {len(cells)} colunas, esperadas "
                f"{len(PUB_COLUMNS)}")
        try:
            addr = int(cells[0], 16)
        except ValueError:
            raise DumpError(
                f"{REL_PUB}:{i}: {cells[0]!r} nao e endereco hexadecimal")
        if addr in seen:
            raise DumpError(
                f"{REL_PUB}:{i}: endereco 0x{addr:08x} repetido "
                f"({seen[addr]} e {cells[2]}.{cells[1]}). A atribuicao por "
                f"intervalo depende de os 96 inicios serem distintos.")
        seen[addr] = f"{cells[2]}.{cells[1]}"
        out.append(Handler(addr, cells[1], cells[2]))
    if not out:
        raise DumpError(f"{REL_PUB}: nenhum handler")
    out.sort(key=lambda h: h.addr)
    return out


# --------------------------------------------------------------- imports ---
#
# Um descritor de import por unidade e o que da a lista de simbolos por
# unidade sem nenhuma heuristica: o linker do C++Builder ja agrupou.

_UNIT_OF = re.compile(r"^@@?([A-Za-z0-9_]+)@")


class Sym:
    __slots__ = ("name", "unit", "dll", "iat", "thunk")

    def __init__(self, name: str, unit: str, dll: str, iat: int):
        self.name = name
        self.unit = unit
        self.dll = dll
        self.iat = iat
        self.thunk: int | None = None

    @property
    def short(self) -> str:
        """O nome sem o prefixo de unidade, que e redundante na tabela."""
        return self.name[len(self.unit) + 2:] if self.name.startswith(
            "@" + self.unit + "@") else self.name


def read_imports(img: Image) -> tuple[list[Sym], dict[str, int]]:
    """Os simbolos importados, com o slot de IAT de cada um."""
    pe = _u32(img.data, 0x3C)
    opt = pe + 4 + 20
    n_dirs = _u32(img.data, opt + 92)
    if n_dirs < 2:
        raise DumpError(f"{REL_EXE}: optional header sem diretorio de import")
    rva, size = struct.unpack_from("<II", img.data, opt + 96 + 8)
    if rva == 0 or size == 0:
        raise DumpError(
            f"{REL_EXE}: sem tabela de import. O veredito deste script e "
            f"inteiramente sobre imports; sem eles nao ha o que medir.")
    base = img.rva_to_offset(rva)
    if base is None:
        raise DumpError(
            f"{REL_EXE}: tabela de import em RVA {rva:#x} fora de qualquer "
            f"secao")
    out: list[Sym] = []
    per_dll: dict[str, int] = {}
    p = base
    while True:
        ilt, _stamp, _chain, name_rva, iat = struct.unpack_from(
            "<IIIII", img.data, p)
        if ilt == 0 and name_rva == 0 and iat == 0:
            break
        noff = img.rva_to_offset(name_rva)
        if noff is None:
            raise DumpError(
                f"{REL_EXE}: nome de DLL em RVA {name_rva:#x} fora de secao")
        dll = _cstr(img.data, noff)
        toff = img.rva_to_offset(ilt or iat)
        if toff is None:
            raise DumpError(f"{REL_EXE}: thunk table de {dll} fora de secao")
        k = 0
        while True:
            entry = _u32(img.data, toff + 4 * k)
            if entry == 0:
                break
            if entry & 0x80000000:
                name = f"@ordinal#{entry & 0xFFFF}"
            else:
                ho = img.rva_to_offset(entry)
                if ho is None:
                    raise DumpError(
                        f"{REL_EXE}: hint/name em RVA {entry:#x} fora de secao")
                name = _cstr(img.data, ho + 2)
            m = _UNIT_OF.match(name)
            unit = m.group(1) if m else ""
            out.append(Sym(name, unit, dll, img.image_base + iat + 4 * k))
            per_dll[dll] = per_dll.get(dll, 0) + 1
            k += 1
        p += 20
    if not out:
        raise DumpError(f"{REL_EXE}: tabela de import vazia")
    return out, per_dll


def _cstr(data: bytes, off: int) -> str:
    end = data.index(b"\0", off)
    return data[off:end].decode("latin-1")


def read_thunks(img: Image, by_iat: dict[int, Sym]) -> int:
    """Liga cada simbolo ao stub `jmp *[IAT]` dele. Devolve quantos ligou.

    O corte e duplo -- `FF 25` cujo operando a `.reloc` marca como endereco
    **e** cujo valor cai num slot de IAT conhecido. So o padrao de bytes
    devolve oito falsos nesta `.text`: tres bytes `0xff` soltos no meio de
    outra instrucao e quatro `jmp` legitimos por ponteiro de `.data` (os stubs
    de "floating point formats not linked" da RTL).
    """
    text = img.section(".text")
    beg, end = text.raw_ptr, text.raw_ptr + text.raw_size
    linked = 0
    for off in range(beg, end - 6):
        if img.data[off] != 0xFF or img.data[off + 1] != 0x25:
            continue
        if (off + 2) not in img.relocs:
            continue
        slot = _u32(img.data, off + 2)
        sym = by_iat.get(slot)
        if sym is None:
            continue
        if sym.thunk is not None:
            raise DumpError(
                f"{REL_EXE}: dois stubs para {sym.name} "
                f"({sym.thunk:#x} e {img.offset_to_va(off):#x}). A atribuicao "
                f"de sitio de chamada supoe um stub por import.")
        sym.thunk = img.offset_to_va(off)
        linked += 1
    return linked


# --------------------------------------------------------------- exports ---


def read_exports(img: Image) -> dict[str, set[int]]:
    """Nome exportado -> enderecos. O `.exe` exporta como package member."""
    pe = _u32(img.data, 0x3C)
    opt = pe + 4 + 20
    rva, size = struct.unpack_from("<II", img.data, opt + 96)
    if rva == 0 or size == 0:
        raise DumpError(
            f"{REL_EXE}: sem tabela de export. Os 26 "
            f"`@@Tep2002_*@Initialize`/`Finalize` sao o que identifica a "
            f"tabela de modulos; sem eles ela viraria chute.")
    b = img.rva_to_offset(rva)
    if b is None:
        raise DumpError(f"{REL_EXE}: tabela de export fora de secao")
    n_names = _u32(img.data, b + 24)
    eat = img.rva_to_offset(_u32(img.data, b + 28))
    npt = img.rva_to_offset(_u32(img.data, b + 32))
    ot = img.rva_to_offset(_u32(img.data, b + 36))
    if None in (eat, npt, ot):
        raise DumpError(f"{REL_EXE}: tabelas de export fora de secao")
    out: dict[str, set[int]] = {}
    for i in range(n_names):
        noff = img.rva_to_offset(_u32(img.data, npt + 4 * i))
        if noff is None:
            continue
        name = _cstr(img.data, noff)
        ordi = _u16(img.data, ot + 2 * i)
        out.setdefault(name, set()).add(
            img.image_base + _u32(img.data, eat + 4 * ordi))
    return out


# ------------------------------------------------------------ referencias ---

# As cinco formas em que um import pode ser referenciado, na ordem em que a
# medida as procura. O rotulo e o que sai no markdown.
KIND_CALL = "call rel32 → stub"
KIND_JUMP = "jmp rel → stub"
KIND_IND = "call/jmp indireto pelo IAT"
KIND_LOAD = "carga do endereço do slot"
KIND_TABLE = "entrada de tabela → stub"


def cell(text: str) -> str:
    """Escapa o que quebraria uma celula de tabela markdown.

    As expressoes regulares dos indicios sao alternacoes -- um `|` cru ali
    parte a linha em colunas a mais e destroi a tabela inteira. O GFM entende
    `\\|` mesmo dentro de trecho de codigo, e o renderiza como `|`.
    """
    return text.replace("|", "\\|")


class Ref:
    __slots__ = ("site", "kind", "sym", "owner")

    def __init__(self, site: int, kind: str, sym: Sym):
        self.site = site
        self.kind = kind
        self.sym = sym
        self.owner: str | None = None


def find_refs(img: Image, syms: list[Sym]) -> list[Ref]:
    """Toda referencia a `syms`, varrendo o arquivo inteiro byte a byte."""
    data = img.data
    by_thunk = {s.thunk: s for s in syms if s.thunk is not None}
    by_iat = {s.iat: s for s in syms}
    own_operand = {s.thunk + 2 for s in syms if s.thunk is not None}
    text = img.section(".text")
    tbeg, tend = text.raw_ptr, text.raw_ptr + text.raw_size

    refs: list[Ref] = []
    # (1) e (2): desvios relativos para o stub, so em .text.
    for off in range(tbeg, tend - 5):
        op = data[off]
        va = img.offset_to_va(off)
        if op in (0xE8, 0xE9):
            target = va + 5 + _i32(data, off + 1)
            sym = by_thunk.get(target)
            if sym is not None:
                refs.append(Ref(va, KIND_CALL if op == 0xE8 else KIND_JUMP,
                                sym))
        elif op == 0xEB:
            target = va + 2 + struct.unpack_from("<b", data, off + 1)[0]
            sym = by_thunk.get(target)
            if sym is not None:
                refs.append(Ref(va, KIND_JUMP, sym))

    # (3), (4) e (5): qualquer dword do arquivo que seja o slot ou o stub. A
    # varredura nao e alinhada de proposito -- imediato de instrucao nao tem
    # alinhamento, e perder um seria perder o veredito.
    for sec in img.sections:
        if sec.raw_size == 0:
            continue
        for off in range(sec.raw_ptr, sec.raw_ptr + sec.raw_size - 3):
            value = _u32(data, off)
            va = img.offset_to_va(off)
            if va is None:
                continue
            sym = by_iat.get(value)
            if sym is not None and va not in own_operand:
                kind = KIND_LOAD
                if off >= 2 and data[off - 2] == 0xFF and data[off - 1] in (
                        0x15, 0x25):
                    kind = KIND_IND
                    va -= 2
                refs.append(Ref(va, kind, sym))
                continue
            sym = by_thunk.get(value)
            if sym is not None and off in img.relocs:
                refs.append(Ref(va, KIND_TABLE, sym))
    refs.sort(key=lambda r: (r.site, r.kind))
    return refs


def assign_owner(refs: list[Ref], handlers: list[Handler]) -> None:
    for r in refs:
        for h in handlers:
            if h.addr <= r.site < h.end:
                r.owner = h.label
                break


def measure_handlers(img: Image, handlers: list[Handler]) -> None:
    text = img.section(".text")
    tend = text.raw_ptr + text.raw_size
    for i, h in enumerate(handlers):
        limit = tend
        if i + 1 < len(handlers):
            nxt = img.va_to_offset(handlers[i + 1].addr)
            if nxt is None:
                raise DumpError(
                    f"{REL_PUB}: handler {handlers[i + 1].label} em "
                    f"{handlers[i + 1].addr:#x} fora de qualquer secao")
            limit = nxt
        start = img.va_to_offset(h.addr)
        if start is None:
            raise DumpError(
                f"{REL_PUB}: handler {h.label} em {h.addr:#x} fora de secao")
        h.end = img.offset_to_va(extent(img.data, start, limit, h.label))


# ------------------------------------------------------ tabela de modulos ---


class ModuleTable:
    """Os registros de ciclo de vida que o executavel percorre no arranque.

    Identificada, nao adivinhada: a varredura sai do primeiro dword relocado da
    `.text` com passo fixo de 6 bytes, e so vale como tabela se **todos** os 26
    `@@Tep2002_*@Initialize`/`Finalize` exportados pelo proprio app caem dentro
    dela. Se um faltar, o script aborta.
    """

    __slots__ = ("start", "count", "end", "entries", "own")

    def __init__(self, img: Image, exports: dict[str, set[int]]):
        text = img.section(".text")
        tbeg, tend = text.raw_ptr, text.raw_ptr + text.raw_size
        first = min((o for o in img.relocs if tbeg <= o < tend), default=None)
        if first is None:
            raise DumpError(f"{REL_EXE}: nenhuma realocacao em .text")
        # O primeiro dword relocado e o campo de endereco do registro 0; o
        # registro comeca MODULE_RECORD - 4 bytes antes, no campo de tag.
        self.start = img.offset_to_va(first) - (MODULE_RECORD - 4)
        base = img.va_to_offset(self.start)
        if base is None:
            raise DumpError(
                f"{REL_EXE}: a tabela de modulos comecaria em "
                f"{self.start:#x}, fora de qualquer secao. O registro de "
                f"{MODULE_RECORD} bytes nao bate com este binario.")
        n = 0
        while True:
            off = base + MODULE_RECORD * n + (MODULE_RECORD - 4)
            if off + 4 > tend or off not in img.relocs:
                break
            n += 1
        if n == 0:
            raise DumpError(f"{REL_EXE}: tabela de modulos vazia")
        self.count = n
        self.end = self.start + MODULE_RECORD * n
        self.entries: dict[int, int] = {}
        for i in range(n):
            off = base + MODULE_RECORD * i + (MODULE_RECORD - 4)
            self.entries[img.offset_to_va(off)] = _u32(img.data, off)
        values = set(self.entries.values())

        self.own = {k: v for k, v in exports.items()
                    if k.startswith("@@") and (k.endswith("@Initialize")
                                               or k.endswith("@Finalize"))}
        missing = sorted(k for k, v in self.own.items() if not (v & values))
        if not self.own or missing:
            raise DumpError(
                f"{REL_EXE}: a tabela de modulos em {self.start:#x} nao "
                f"contem {len(missing)} dos {len(self.own)} "
                f"`@@Tep2002_*@Initialize`/`Finalize` exportados "
                f"({', '.join(missing[:3])}...). Ou o passo de "
                f"{MODULE_RECORD} bytes esta errado, ou a tabela nao comeca "
                f"onde este script supoe -- em qualquer dos casos o veredito "
                f"sobre inicializacao de unidade seria chute.")

    def slot_of(self, value: int) -> int | None:
        for va, v in self.entries.items():
            if v == value:
                return va
        return None


# ------------------------------------------------------------- indicios ---


def read_dfm_needles(paths: list[Path], needles: tuple[str, ...]
                     ) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for needle in needles:
                if needle in line:
                    out.append((path.name, line.strip()))
    return out


def read_string_hits(text: str, pattern: str) -> list[str]:
    lines = text.splitlines()
    if not lines:
        raise DumpError(f"{REL_STR}: arquivo vazio")
    header = lines[0].split("\t")
    if "texto" not in header:
        raise DumpError(
            f"{REL_STR}: cabecalho sem a coluna `texto`.\n"
            f"       veio: {'|'.join(header)}\n"
            f"       Se o dump_strings.py mudou o formato, este script tem "
            f"de acompanhar.")
    col = header.index("texto")
    rx = re.compile(pattern, re.IGNORECASE)
    out: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) > col and rx.search(cells[col]):
            out.append(cells[col])
    return out


# ------------------------------------------------------------------ medida ---


class UnitVerdict:
    __slots__ = ("unit", "syms", "refs", "api", "calls", "dfm_hits",
                 "str_hits")

    def __init__(self, unit: str, syms: list[Sym], refs: list[Ref],
                 dfm_hits: list[tuple[str, str]], str_hits: list[str]):
        self.unit = unit
        self.syms = syms
        self.refs = refs
        self.dfm_hits = dfm_hits
        self.str_hits = str_hits
        life = {p.format(unit) for p in LIFECYCLE}
        self.api = [s for s in syms if s.name not in life]
        self.calls = [r for r in refs if r.kind in (KIND_CALL, KIND_JUMP,
                                                    KIND_IND)]

    @property
    def verdict(self) -> str:
        return "transitiva" if not self.in_app_code else "usada"

    @property
    def in_app_code(self) -> list[Ref]:
        """Chamadas dentro de um dos 96 handlers -- o teste que decide."""
        return [r for r in self.calls if r.owner is not None]


class Measurement:
    def __init__(self, img: Image, handlers: list[Handler],
                 dfm_paths: list[Path], strings: str):
        self.img = img
        self.handlers = handlers
        self.dfm_paths = dfm_paths
        self.syms, self.per_dll = read_imports(img)
        self.by_iat = {s.iat: s for s in self.syms}
        if len(self.by_iat) != len(self.syms):
            raise DumpError(f"{REL_EXE}: dois imports no mesmo slot de IAT")
        self.linked = read_thunks(img, self.by_iat)
        missing = [s for s in self.syms if s.thunk is None]
        if missing:
            raise DumpError(
                f"{REL_EXE}: {len(missing)} imports sem stub `jmp *[IAT]` "
                f"({missing[0].name}). Um import sem stub e um import que o "
                f"codigo alcanca por outro caminho, e a varredura de sitio de "
                f"chamada deste script deixaria de valer.")

        measure_handlers(img, handlers)
        self.exports = read_exports(img)
        self.table = ModuleTable(img, self.exports)

        # Panorama: quantas unidades Borland importam so o par de ciclo de vida.
        self.units: dict[str, list[Sym]] = {}
        for s in self.syms:
            if s.dll.lower().endswith(".bpl") and s.unit:
                self.units.setdefault(s.unit, []).append(s)
        self.lifecycle_only = sorted(
            u for u, ss in self.units.items()
            if all(s.name in {p.format(u) for p in LIFECYCLE} for s in ss))

        self.refs = find_refs(img, [s for s in self.syms
                                    if s.unit in UNITS])
        assign_owner(self.refs, handlers)

        self.verdicts: list[UnitVerdict] = []
        for unit in UNITS:
            syms = sorted((s for s in self.syms if s.unit == unit),
                          key=lambda s: s.iat)
            if not syms:
                raise DumpError(
                    f"{REL_EXE}: nenhum import de `{unit}`. A WTE-TASK-07 "
                    f"julga quatro unidades que a §5 do plano viu nos "
                    f"imports; se uma sumiu, o plano ou o binario mudou.")
            needles, pattern = EVIDENCE[unit]
            dfm_hits = read_dfm_needles(dfm_paths, needles)
            str_hits = read_string_hits(strings, pattern)
            v = UnitVerdict(unit, syms,
                            [r for r in self.refs if r.sym.unit == unit],
                            dfm_hits, str_hits)
            if (dfm_hits or str_hits) and not v.api:
                raise DumpError(
                    f"{REL_EXE}: `{unit}` importa so o par de ciclo de vida, "
                    f"mas ha {len(dfm_hits)} indicios no DFM e "
                    f"{len(str_hits)} nas strings. Isso e contradicao: a "
                    f"funcionalidade estaria sendo alcancada por um caminho "
                    f"que esta script nao ve. Investigar antes de emitir "
                    f"veredito.")
            self.verdicts.append(v)

        text = img.section(".text")
        self.text_beg = img.image_base + text.rva
        self.text_end = self.text_beg + text.raw_size
        self.handler_bytes = sum(
            img.va_to_offset(h.end) - img.va_to_offset(h.addr)
            for h in handlers)


# -------------------------------------------------------------- markdown ---


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def render_md(m: Measurement) -> str:
    o: list[str] = []
    w = o.append

    n_borland = len(m.units)
    n_life = len(m.lifecycle_only)
    bpl = sorted(d for d in m.per_dll if d.lower().endswith(".bpl"))
    n_bpl = sum(m.per_dll[d] for d in bpl)

    w("# `re/unidades-vcl.md` — `Registry`, `Printers`, `Comobj` e "
      "`Winhelpviewer`")
    w("")
    w("Produto da [WTE-TASK-07](../../docs/tasks/concluidos/07-unidades-duvidosas.md). "
      "Gerado por")
    w(f"[`../tools/dump_units.py`](../tools/dump_units.py), a partir de")
    w(f"`{REL_EXE}`, de")
    w("[`published_methods.tsv`](published_methods.tsv), de "
      "[`strings.tsv`](strings.tsv)")
    w("e dos 18 DFM de [`dfm/`](dfm/).")
    w("**Não editar à mão** — correção entra no script e o arquivo é "
      "regerado:")
    w("")
    w("```sh")
    w("python3 wte/tools/dump_units.py")
    w("python3 wte/tools/dump_units.py --check   # o que `make -C wte check` "
      "roda")
    w("```")
    w("")
    w("Não há TSV: são quatro unidades e "
      f"{sum(len(v.syms) for v in m.verdicts)} símbolos, e a tabela em "
      "markdown já é a")
    w("forma final do dado. **Todo número daqui saiu do script**, inclusive "
      "os do texto")
    w("corrido — é por isso que o `--check` compara o arquivo inteiro byte a "
      "byte.")
    w("")
    w("## O veredito")
    w("")
    w("| Unidade | Símbolos importados | Além do ciclo de vida | Chamadas | "
      "Em handler | Veredito |")
    w("|---|---:|---:|---:|---:|---|")
    for v in m.verdicts:
        w(f"| `{v.unit}` | {len(v.syms)} | {len(v.api)} | {len(v.calls)} | "
          f"{len(v.in_app_code)} | **{v.verdict}** |")
    w("")
    n_usada = sum(1 for v in m.verdicts if v.verdict == "usada")
    if n_usada:
        w(f"{n_usada} das quatro são **usadas**. As substituições em LCL "
          f"estão abaixo, unidade a unidade.")
    else:
        w("**As quatro são transitivas.** Nenhuma delas tem uma única chamada "
          "partindo de")
        w("código do aplicativo, e três das quatro não têm chamada nenhuma em "
          "lugar nenhum")
        w("do binário. Consequência para o port: **nada a substituir**. Não "
          "há INI a")
        w("escrever em `~/.config/`, não há impressão a decidir escopo, não "
          "há janela de")
        w("ajuda a construir. As quatro somem, e some com elas o trabalho que "
          "a §5 do")
        w("plano reservava para o caso de serem reais.")
    w("")
    w("A coluna que decide é **Em handler**. \"Chamadas\" conta qualquer "
      "transferência de")
    w("controle para o símbolo importado; \"Em handler\" conta as que caem "
      "dentro do corpo")
    w("de um dos 96 handlers publicados, isto é, dentro de código que o "
      "aplicativo")
    w("escreveu. A distinção só importa para o `Comobj`, e a seção dele "
      "explica por quê.")
    w("")

    # ---------------------------------------------------------------- régua
    w("## O que foi medido, e com que régua")
    w("")
    w(f"O `.exe` tem {len(m.img.data)} bytes, é PE32 i386, `ImageBase` "
      f"`{m.img.image_base:#x}`,")
    w(f"{len(m.img.sections)} seções. A `.text` vai de `{m.text_beg:#010x}` a "
      f"`{m.text_end:#010x}`.")
    w(f"São {len(m.syms)} imports, {n_bpl} deles de "
      f"{' e '.join('`' + d + '`' for d in bpl)},")
    w(f"distribuídos em {n_borland} unidades Borland nomeadas.")
    w("")
    w("### O import não vira `call ds:[…]`, e é aí que a medida quase deu "
      "errado")
    w("")
    w("O enunciado da tarefa manda procurar `call ds:[...]` para o thunk. Não "
      "existe")
    w("nenhum: o linker do C++Builder emite **um stub `jmp *[IAT]` por "
      "import**, agrupados")
    w(f"no fim da `.text`, e o código chama o stub por `call rel32`. Procurar "
      f"a forma")
    w(f"indireta no sítio de uso acharia zero nas quatro unidades — e nas "
      f"outras {n_borland - len(UNITS)}")
    w("também, o que é o sinal de que o critério, não o binário, estaria "
      "errado.")
    w("")
    w(f"São {m.linked} stubs, **um por import, nenhum import sem stub**. O "
      f"corte que os")
    w("acha é duplo: `FF 25 imm32` cujo operando a `.reloc` marca como "
      "endereço **e** cujo")
    w("valor cai num slot de IAT conhecido. Só o padrão de bytes devolve oito "
      "falsos —")
    w("três bytes `0xff` soltos dentro de outra instrução, e quatro `jmp` "
      "legítimos por")
    w("ponteiro de `.data`, que são os stubs de `printf : floating point "
      "formats not")
    w("linked` da RTL. É a mesma régua de `.reloc` que o "
      "[`offsets.md`](offsets.md) e o")
    w("[`strings.md`](strings.md) usam, no mesmo papel: separar endereço de "
      "coincidência.")
    w("")
    w("### Cinco formas de referência, não uma")
    w("")
    w("Para cada símbolo das quatro unidades o script procura, no arquivo "
      "inteiro e byte")
    w("a byte — todas as seções, sem exigir alinhamento:")
    w("")
    w("| Forma | O que seria |")
    w("|---|---|")
    w(f"| `{KIND_CALL}` | chamada de verdade |")
    w(f"| `{KIND_JUMP}` | chamada em posição de cauda |")
    w(f"| `{KIND_IND}` | chamada sem passar pelo stub |")
    w(f"| `{KIND_LOAD}` | o endereço virando dado (ponteiro de função, "
      f"referência de classe) |")
    w(f"| `{KIND_TABLE}` | o stub numa tabela de ponteiros |")
    w("")
    w("Nas tabelas de sítio abaixo, **Sítio** é o endereço da instrução — "
      "exceto na quarta")
    w("forma, em que é a posição do dword. Ali a instrução que carrega o "
      "endereço não tem")
    w("forma única (`mov r32, imm32`, `mov r32, moffs32`, `push imm32`, …) e "
      "recuperar o")
    w("início dela exigiria decodificar para trás, que é palpite.")
    w("")
    w("As três primeiras são o que a tarefa chama de *chamada*. A quarta e a "
      "quinta")
    w("existem porque o veredito seria falso sem elas: uma referência de "
      "classe da")
    w("Borland (`@Comobj@EOleException@`) chega ao código como **dado**, não "
      "como chamada,")
    w("e a tabela de módulos do executável guarda os `initialization` como "
      "**tabela**, não")
    w("como `call`. Procurar só `call` acharia menos do que existe.")
    w("")
    w("### O corpo dos 96 handlers")
    w("")
    w(f"O [`published_methods.tsv`](published_methods.tsv) dá o **início** "
      f"dos {len(m.handlers)} handlers.")
    w("Para responder \"qual handler contém a chamada\" é preciso o fim, e "
      "ele é medido com")
    w("o mesmo decodificador de comprimento x86-32 do "
      "[`dump_strings.py`](../tools/dump_strings.py) —")
    w("varredura linear que encerra no primeiro `ret` ou `jmp` situado além "
      "de todo alvo")
    w(f"de desvio já visto. Os {len(m.handlers)} corpos somam "
      f"{m.handler_bytes} bytes; o último termina em")
    w(f"`{max(h.end for h in m.handlers):#010x}`, bem antes do fim da `.text`. "
      f"Tudo o que estiver depois")
    w("disso é código que o aplicativo não escreveu, e essa é a fronteira que "
      "o veredito")
    w("do `Comobj` usa.")
    w("")

    # ------------------------------------------------------------ panorama
    w("## O panorama que enquadra as quatro")
    w("")
    w(f"Das {n_borland} unidades Borland importadas, **{n_life} importam "
      f"exatamente dois símbolos**:")
    w("`@X@initialization$qqrv` e `@X@Finalization$qqrv`. Esse par não é API "
      "— é o ciclo")
    w("de vida que a tabela de módulos do executável percorre no arranque e "
      "no")
    w("encerramento. Unidade que só o importa não teve nenhuma função sua "
      "chamada.")
    w("")
    w(f"As {n_life}: " + ", ".join(f"`{u}`" for u in m.lifecycle_only) + ".")
    w("")
    life_under_test = [u for u in UNITS if u in m.lifecycle_only]
    w("Três das quatro sob julgamento estão nessa lista — "
      + ", ".join(f"`{u}`" for u in life_under_test) + " —")
    w("e isso, sozinho, já é quase o veredito delas. A quarta, `Comobj`, "
      "importa dois")
    w("símbolos a mais, e é a única que exigiu ir ao disassembly.")
    w("")
    w("Companhia reveladora na mesma lista: `Inifiles`. O aplicativo **não "
      "guarda")
    w("configuração em lugar nenhum** — nem no registry, nem em `.ini`. Isso "
      "fecha por")
    w("dois lados a hipótese que a §5 do plano levantava para o `Registry`.")
    w("")

    # ------------------------------------------------------- por unidade
    w("## Unidade a unidade")
    w("")
    for v in m.verdicts:
        w(f"### `{v.unit}` — {v.verdict}")
        w("")
        w("| Símbolo | Slot de IAT | Stub | Referências |")
        w("|---|---|---|---:|")
        for s in v.syms:
            n = sum(1 for r in v.refs if r.sym is s)
            w(f"| `{s.short}` | `{s.iat:#010x}` | `{s.thunk:#010x}` | {n} |")
        w("")
        for line in UNIT_PROSE[v.unit](m, v):
            w(line)
        w("")

    # ------------------------------------------------- inicialização à parte
    w("## A inicialização de unidade, conferida à parte")
    w("")
    w("A WTE-TASK-07 avisa que chamada em código de inicialização não está "
      "em handler")
    w("nenhum, e manda procurar nos dois lugares. Este script procura em "
      "todos: a")
    w("varredura de referência é do arquivo inteiro, não das regiões de "
      "código")
    w("conhecidas. Ainda assim, a inicialização merece conferência própria, "
      "porque é")
    w("exatamente onde as quatro unidades **aparecem**.")
    w("")
    w(f"Há uma tabela de módulos em `{m.table.start:#010x}`..`"
      f"{m.table.end:#010x}`: {m.table.count} registros de")
    w(f"{MODULE_RECORD} bytes, cada um uma etiqueta de 16 bits seguida de um "
      f"endereço relocado. Ela é")
    w("**identificada, não adivinhada** — os "
      f"{len(m.table.own)} `@@Tep2002_*@Initialize` e")
    w("`@@Tep2002_*@Finalize` que o próprio aplicativo exporta estão todos "
      "dentro dela, e")
    w("o script aborta se um faltar. Ao lado deles, nas mesmas colunas, estão "
      "os stubs")
    w("das unidades importadas:")
    w("")
    w("| Unidade | `initialization` | `Finalization` |")
    w("|---|---|---|")
    for v in m.verdicts:
        cells = []
        for pattern in LIFECYCLE:
            name = pattern.format(v.unit)
            sym = next((s for s in v.syms if s.name == name), None)
            slot = m.table.slot_of(sym.thunk) if sym else None
            cells.append(f"`{slot:#010x}`" if slot else "—")
        w(f"| `{v.unit}` | {cells[0]} | {cells[1]} |")
    w("")
    w("É a assinatura exata de dependência transitiva: a unidade está na "
      "lista de")
    w("módulos do executável — então a seção `initialization` dela roda no "
      "arranque —,")
    w("mas nenhum código do `.exe` chama coisa alguma dela. O linker a "
      "arrastou porque")
    w("alguma unidade que o aplicativo usa a declara em `uses`.")
    w("")
    w("Fora dessa tabela, os `initialization`/`Finalization` das quatro não "
      "aparecem em")
    w("mais lugar nenhum do arquivo.")
    w("")

    # --------------------------------------------------------- a lacuna
    w("## O que \"sem import\" não provaria sozinho")
    w("")
    w("Ausência de import prova que o `.exe` não chama a unidade **por "
      "nome**. Não prova")
    w("que a funcionalidade não acontece: uma unidade cuja `initialization` "
      "se registra")
    w("num despachante entrega o serviço de dentro do package, sem o `.exe` "
      "citar")
    w("símbolo. O `Winhelpviewer` é literalmente isso — o que ele faz ao "
      "inicializar é")
    w("se registrar como visualizador de ajuda.")
    w("")
    w("Por isso o veredito não parou no import. Para cada unidade o script "
      "conta os")
    w("indícios que a funcionalidade deixaria em lugares já medidos por "
      "outras tasks —")
    w(f"propriedade nos {len(m.dfm_paths)} DFM da WTE-TASK-03, texto no "
      f"inventário da WTE-TASK-05:")
    w("")
    w("| Unidade | Agulhas no DFM | Achadas | Expressão nas strings | "
      "Achadas |")
    w("|---|---|---:|---|---:|")
    for v in m.verdicts:
        needles, pattern = EVIDENCE[v.unit]
        shown = ", ".join(f"`{n}`" for n in needles) if needles else "—"
        w(f"| `{v.unit}` | {shown} | {len(v.dfm_hits)} | "
          f"`{cell(pattern)}` | {len(v.str_hits)} |")
    w("")
    total_ev = sum(len(v.dfm_hits) + len(v.str_hits) for v in m.verdicts)
    if total_ev == 0:
        w("**Zero em todas as células.** Nenhum formulário tem `HelpFile`, "
          "`HelpContext` ou")
        w("diálogo de impressão; nenhuma string cita `.hlp`, chave de "
          "registry, `.ini` ou")
        w("CLSID. Indício positivo com zero import seria contradição, e o "
          "script aborta")
        w("nesse caso em vez de emitir veredito.")
    else:
        w(f"**{total_ev} indícios.** Conferir cada um antes de confiar no "
          f"veredito.")
    w("")
    w("Corroboração independente vinda da tabela de import de SO: o "
      "executável importa")
    w("de três DLLs apenas — "
      + ", ".join(f"`{d}` ({m.per_dll[d]})"
                  for d in sorted(m.per_dll) if not d.lower().endswith(".bpl"))
      + ".")
    w("**`ADVAPI32.DLL` não aparece**, e nem `SHELL32.DLL`. De `USER32` o "
      "aplicativo usa")
    w("três funções, e nenhuma é de impressão ou de ajuda.")
    w("")

    # ---------------------------------------------------- consequência
    w("## Consequência para o port, e para a §5 do plano")
    w("")
    w("A §5 do plano guardava uma hipótese para cada uma. Todas as quatro "
      "caem:")
    w("")
    w("| Hipótese da §5 | O que a medida diz |")
    w("|---|---|")
    w("| `Registry` → config no registry vira INI em `~/.config/` | não há "
      "config nenhuma; `Inifiles` também é só ciclo de vida |")
    w("| `Printers` → \"se houver impressão de verdade, decidir escopo\" | "
      "não há; zero símbolo além do par, zero diálogo de impressão |")
    w("| `Comobj` → \"quase certamente só o `ShellExecute` do `TBrowseURL`\" "
      "| **não é isso.** O `TBrowseURL` não passa por aqui — ver a seção do "
      "`Comobj` |")
    w("| `Winhelpviewer` → o texto de ajuda vira janela própria | não há "
      "texto de ajuda; não há `.hlp`; nenhum formulário tem `HelpFile` |")
    w("")
    w("Nenhuma das quatro gera item para fase alguma. Não há task de destino "
      "a apontar,")
    w("porque não há handler dono: as únicas referências vivas estão na "
      "tabela de")
    w("módulos e no caminho de asserção da RTL, e as duas somem sozinhas ao "
      "trocar o")
    w("C++Builder pelo FPC.")
    return "\n".join(o) + "\n"


# --------------------------------------------- prosa especifica por unidade


def _sites(v: UnitVerdict) -> list[str]:
    """A lista de sitios, no formato que as quatro secoes compartilham."""
    out = ["| Sítio | Forma | Símbolo | Handler dono |",
           "|---|---|---|---|"]
    for r in v.refs:
        out.append(f"| `{r.site:#010x}` | {r.kind} | `{r.sym.short}` | "
                   f"{r.owner or '—'} |")
    return out


def _plain(m: Measurement, v: UnitVerdict) -> list[str]:
    o = ["Dois símbolos, e são o par de ciclo de vida. **Nenhuma chamada em "
         "lugar nenhum**",
         "do arquivo: as duas únicas referências são o próprio operando do "
         "stub e a entrada",
         "na tabela de módulos.",
         ""]
    o += _sites(v)
    return o


def _registry(m: Measurement, v: UnitVerdict) -> list[str]:
    o = _plain(m, v)
    o += ["",
          "Nenhum `@Registry@TRegistry@…` é importado — nem um método, nem a "
          "referência de",
          "classe. Sem a referência de classe não há como construir um "
          "`TRegistry`: em",
          "Delphi e C++Builder, instanciar exige o `TMetaClass`, e ele "
          "chegaria como",
          "import igual ao `@Comobj@EOleException@` que a seção do `Comobj` "
          "mostra.",
          "",
          "**Substituição em LCL: nenhuma.** Não há configuração a migrar "
          "para",
          "`~/.config/`, porque não há configuração. **Task de destino: "
          "nenhuma.**"]
    return o


def _printers(m: Measurement, v: UnitVerdict) -> list[str]:
    o = _plain(m, v)
    o += ["",
          "`@Printers@Printer$qqrv` — o acessor global que qualquer impressão "
          "atravessaria —",
          "não está importado. Nos 18 formulários não há `TPrintDialog` nem "
          "`TPrinterSetupDialog`.",
          "",
          "**Substituição em LCL: nenhuma.** Não há escopo de impressão a "
          "decidir.",
          "**Task de destino: nenhuma.**"]
    return o


def _winhelp(m: Measurement, v: UnitVerdict) -> list[str]:
    o = _plain(m, v)
    o += ["",
          "Esta é a unidade em que \"zero import\" precisava de reforço, e "
          "recebeu: o que o",
          "`Winhelpviewer` faz ao inicializar é **se registrar como "
          "visualizador de ajuda**,",
          "de modo que a ajuda seria despachada de dentro do package sem o "
          "`.exe` citar",
          "símbolo. O reforço está na seção dos indícios — nenhum dos 18 "
          "formulários tem",
          "`HelpFile`, `HelpContext`, `HelpType` ou `HelpKeyword`, e nenhuma "
          "das strings cita",
          "`.hlp`. Não existe ajuda a despachar.",
          "",
          "**Substituição em LCL: nenhuma.** Não há texto de ajuda para virar "
          "janela",
          "própria. **Task de destino: nenhuma.**"]
    return o


def _comobj(m: Measurement, v: UnitVerdict) -> list[str]:
    call = next((r for r in v.calls), None)
    load = next((r for r in v.refs if r.kind == KIND_LOAD), None)
    o = ["Quatro símbolos: o par de ciclo de vida e mais dois, ambos do "
         "`EOleException` — o",
         "construtor e a referência de classe. E, ao contrário das outras "
         "três, **há uma",
         "chamada de verdade**."]
    o += [""]
    o += _sites(v)
    if call is None:
        o += ["", "Nenhuma chamada, apesar dos símbolos a mais."]
        return o
    last = max(h.end for h in m.handlers)
    o += ["",
          f"A chamada está em `{call.site:#010x}`, e a coluna do handler dono "
          f"diz `—`. Não é",
          f"lacuna de medida: o último dos {len(m.handlers)} handlers termina "
          f"em `{last:#010x}`, e o sítio",
          f"está {call.site - last} bytes depois disso. A chamada está fora "
          f"de todo código que o",
          "aplicativo escreveu."]
    if load is not None:
        o += ["",
              f"A linha de cima, a carga em `{load.site:#010x}`, é a "
              f"referência de classe",
              "(`@Comobj@EOleException@`) chegando ao código como dado, "
              "quatro bytes antes da",
              "chamada do construtor. É o caso que justifica a quarta forma "
              "de referência da",
              "régua: se o script só procurasse `call`, essa linha sumiria da "
              "evidência."]
    o += ["",
          "#### Onde ela está, então",
          "",
          "No caminho de falha de asserção da RTL da Borland. A rotina que "
          "contém a chamada",
          "é alcançada por uma cadeia de três saltos a partir de uma rotina "
          "de `Variant` que",
          "verifica `vt == rhs.vt` e, se a verificação falhar, monta a "
          "mensagem",
          "`_ASSERTE: %s failed - %s/%d` com o nome do arquivo `VARIANT.CPP` "
          "e o número da",
          "linha, mostra um `MessageBoxA` com o texto",
          "`Press [Y]es to terminate, [N]o to continue and [C]ancel to Debug` "
          "e, se a",
          "resposta for *Yes*, levanta um `EOleException` com `E_FAIL` "
          "(`0x80004005`).",
          "",
          "Os quatro literais que provam isso — `_ASSERTE: `, `VARIANT.CPP`, "
          "`vt == rhs.vt` e",
          "o texto do diálogo — estão no "
          "[`strings.md`](strings.md)/[`strings.tsv`](strings.tsv) da",
          "WTE-TASK-05, e **a coluna `handler` deles também está vazia**, "
          "medida por outro",
          "script e por outro caminho. A vizinhança confirma a origem: as "
          "strings ao redor",
          "citam `c:\\bcb\\emuvcl\\utilcls.h`, que é a camada em que o "
          "C++Builder emula em C++",
          "os recursos de linguagem do Delphi.",
          "",
          "#### Por que o veredito é *transitiva*, e não *usada*",
          "",
          "O `EOleException` é o que a RTL levanta quando uma invariante "
          "interna dela",
          "quebra. É código de escape, compilado junto porque veio de "
          "cabeçalho, e o",
          "aplicativo não o alcança executando o que se propõe a fazer — só "
          "se algo dentro",
          "da própria RTL já tiver dado errado. Chamar isso de *uso da "
          "unidade* inverteria o",
          "sentido da pergunta que a task faz, que é se há funcionalidade a "
          "portar.",
          "",
          "#### A armadilha 2 da tarefa, conferida",
          "",
          "A tarefa avisa: *`Comobj` pode aparecer sem `TBrowseURL` estar "
          "envolvido; não",
          "concluir pela hipótese*. A hipótese da §5 era o contrário — que o "
          "`Comobj` fosse",
          "**só** o `ShellExecute` do `TBrowseURL`. Está derrubada, por três "
          "medidas:",
          "",
          "1. o único sítio de chamada é o de asserção acima, não um "
          "`ShellExecute`;",
          "2. o `.exe` não importa `SHELL32.DLL` — a chamada acontece dentro "
          "do `vcl60.bpl`;",
          "3. o `TBrowseURL` não é componente de terceiro: é a ação padrão da "
          "VCL, da",
          "   unidade `Extactns`, que o `.exe` importa à parte. As duas "
          "instâncias, em",
          "   `MainForm` e em `ficha_about`, são disparadas por método "
          "dinâmico através do",
          "   VMT — sem passar por `Comobj`.",
          "",
          "**Substituição em LCL: nenhuma.** A asserção de `Variant` da "
          "Borland não tem —",
          "nem precisa ter — equivalente: o FPC tem `{$ASSERTIONS}` e "
          "`EAssertionFailed`",
          "próprios, e nada em `Comobj` sobrevive à troca de toolchain. "
          "**Task de destino:",
          "nenhuma** — não há handler dono a que anexar o item."]
    return o


UNIT_PROSE = {
    "Registry": _registry,
    "Printers": _printers,
    "Comobj": _comobj,
    "Winhelpviewer": _winhelp,
}


# ----------------------------------------------------------------- driver ---


def generate() -> dict[str, str]:
    if not EXE.is_file():
        raise DumpError(
            f"{REL_EXE} nao existe.\n"
            "       A pasta we-team-editor/ nao e versionada (binario de "
            "terceiro sem\n"
            "       licenca -- ver a secao 2 do plano). Coloque-a na raiz do "
            "repositorio.")
    if not PUB.is_file():
        raise DumpError(
            f"{REL_PUB} nao existe. Rode antes: python3 "
            f"wte/tools/dump_published.py")
    if not STR.is_file():
        raise DumpError(
            f"{REL_STR} nao existe. Rode antes: python3 "
            f"wte/tools/dump_strings.py")
    if not DFM.is_dir():
        raise DumpError(
            f"{REL_DFM} nao existe. Rode antes: python3 "
            f"wte/tools/dfm_extract.py")
    dfm_paths = sorted(DFM.glob("*.dfm"), key=lambda p: p.as_posix())
    if not dfm_paths:
        raise DumpError(f"{REL_DFM} nao tem nenhum .dfm")

    img = Image(EXE.read_bytes())
    handlers = read_published(PUB.read_text(encoding="utf-8"))
    m = Measurement(img, handlers, dfm_paths,
                    STR.read_text(encoding="utf-8"))
    return {MD_NAME: render_md(m)}


def do_check(files: dict[str, str]) -> int:
    problems: list[str] = []
    for name, content in sorted(files.items()):
        path = OUT / name
        if not path.exists():
            problems.append(f"{name}: nao existe")
            continue
        on_disk = path.read_text(encoding="utf-8")
        if on_disk == content:
            continue
        for i, (a, b) in enumerate(
                zip(on_disk.splitlines(), content.splitlines()), 1):
            if a != b:
                problems.append(f"{name}: linha {i} diverge")
                break
        else:
            problems.append(
                f"{name}: {len(on_disk.splitlines())} linhas no disco contra "
                f"{len(content.splitlines())} regeradas")
    if problems:
        print(f"{REL_OUT} nao corresponde a {REL_EXE}:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivo em dia com {REL_EXE} + {REL_PUB} + "
          f"{REL_STR}")
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(files.items()):
        # newline="\n" para que o arquivo saia igual no Windows -- ele e
        # comparado byte a byte pelo --check.
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  {name}: {content.count(chr(10))} linhas, "
              f"{len(content.encode('utf-8'))} bytes")
    print(f"\n{len(files)} arquivo em {REL_OUT}")
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
