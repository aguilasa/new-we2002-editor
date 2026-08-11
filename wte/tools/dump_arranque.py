#!/usr/bin/env python3
"""O que os 18 `FormCreate`/`FormShow` do original fazem.

Gera `wte/re/arranque.md` e `wte/re/arranque.tsv` — insumo da
[WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md), grupo de carga, linha
"`FormCreate` / `FormShow` — 18 endereços".

## O que a medição responde

A leitura barata desses 18 seria "inicialização de formulário, deve ser
trivial". Medido, eles se separam em quatro formas, e a diferença entre elas é
a diferença entre um `.inc` de uma linha e um handler que ainda não dá para
escrever:

| forma | o que o corpo é |
|---|---|
| `vazio` | um `ret` — o handler está ligado no DFM e não faz nada |
| `cor` | uma chamada a `TControl::SetColor` sobre a própria instância |
| `campo` | uma chamada virtual sobre um campo publicado |
| `composto` | qualquer outra coisa, com o inventário do que ela toca |

O script não decide a forma por tamanho nem por palpite: ele casa o corpo
contra o padrão de bytes de cada uma e, quando nenhuma casa, chama de
`composto` e inventaria. Padrão que passa a não casar mais vira `composto`
sozinho — nunca classificação errada em silêncio.

## Três coisas que ele resolve, e que sem resolver não viram spec

**A cor.** `mov edx,0xe68f41` é `TColor` no formato `$00BBGGRR` da VCL, não
`#RRGGBB`. Trocar a ordem daria um formulário laranja onde o original é azul.

**O global.** `mov eax,ds:0x432e34` não diz de quem é a instância. O script
recupera os 18 sítios de `Application->CreateForm` do `WinMain` — a mesma
medição que o cabeçalho do [`../src/wtemain.pas`](../src/wtemain.pas) descreve —
e daí sai `0x432e34` = `ficha_dorsal`. Um `FormCreate` que colorisse outro
formulário que não o seu apareceria aqui como discordância, e o script aborta.

**O campo e o método virtual.** `[eax+0x304]` vem de
[`campos.tsv`](campos.tsv) (WTE-TASK-25); o slot `[edx+0xc0]` é resolvido no
VMT da classe daquele componente dentro do `vcl60.bpl`/`rtl60.bpl`, e sai com
o nome exportado. Sem os dois, a spec pararia em "chama um método de alguma
coisa".

Uso:

    python3 wte/tools/dump_arranque.py            # regenera
    python3 wte/tools/dump_arranque.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
BPLS = ("vcl60.bpl", "rtl60.bpl")
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
CAMPOS = ROOT / "wte" / "re" / "campos.tsv"
OUT = ROOT / "wte" / "re"

REL_EXE = "we-team-editor/we-team-editor.exe"
REL_PUB = "wte/re/published_methods.tsv"
REL_CAMPOS = "wte/re/campos.tsv"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_arranque.py"

TSV_NAME = "arranque.tsv"
MD_NAME = "arranque.md"

# A faixa do WinMain com os 18 `Application->CreateForm`. Comeca em 0x401a22 e
# nao em 0x401a2e pela razao que o wtemain.pas registra: os dois `mov` que
# carregam os operandos vem ANTES da chamada, e comecando na primeira chamada o
# primeiro par fica de fora.
WINMAIN_INI = 0x00401A00
WINMAIN_FIM = 0x00401BD0
CREATEFORM = 0x004226C0

VMT_CLASS_NAME = -44
VMT_INSTANCE_SIZE = -40

# Janela minima lida para casar os padroes de forma curta -- os tres tem 15
# bytes ou menos, e 128 e folga larga.
JANELA = 128

# Teto duro da varredura de `extent`. Nenhum destes 18 chega perto; existe para
# que uma varredura desalinhada pare com mensagem em vez de percorrer a `.text`.
TETO = 8192


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do `dump_units.py`: cada gerador
# de `wte/tools/` roda sozinho, sem importar os irmaos.
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


# ------------------------------------------------------- decodificador x86 ---
#
# COPIA VERBATIM do `dump_units.py`, e a duplicacao e deliberada: cada gerador
# de `wte/tools/` roda sozinho, sem importar os irmaos, pela mesma razao que
# cada um carrega o proprio leitor de PE. O que ele decide -- comprimento da
# instrucao e classe de fluxo -- e fato sobre x86, nao escolha de projeto, e o
# binario que ele le nunca vai mudar. Se um dia mudar num dos dois, tem de
# mudar nos dois.
#
# Ele existe aqui por um motivo so: achar ONDE o corpo de um handler acaba. A
# conta barata -- ate o endereco do handler seguinte -- funciona no meio da
# `.text` e falha na borda: o `MainForm.FormShow` esta em 0x004111d8 e o
# proximo handler publicado so vem em 0x00420e84, 64 KB adiante. Inventariar
# essa janela inteira poria no relatorio codigo que nao e dele.

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


# ------------------------------------------------------------- os 18 sitios --
def globais_dos_formularios(pe: PE) -> dict[int, str]:
    """Endereco da variavel global de instancia -> nome do formulario."""
    o = pe.off(WINMAIN_INI)
    blob = pe.data[o:o + (WINMAIN_FIM - WINMAIN_INI)]
    saida: dict[int, str] = {}
    for m in re.finditer(rb"\xe8", blob):
        p = m.start()
        if p + 5 > len(blob) or p < 12:
            continue
        rel = struct.unpack_from("<i", blob, p + 1)[0]
        if WINMAIN_INI + p + 5 + rel != CREATEFORM:
            continue
        pre = blob[p - 12:p]
        if pre[0:2] != b"\x8b\x0d" or pre[6:8] != b"\x8b\x15":
            raise DumpError(
                f"{REL_EXE}: sitio de CreateForm em {WINMAIN_INI + p:#x} nao tem "
                f"a forma esperada: {pre.hex()}")
        pvar, pcls = (struct.unpack_from("<I", pre, k)[0] for k in (2, 8))
        classe = pe.shortstring(pe.dword(pe.dword(pcls) + VMT_CLASS_NAME))
        saida[pe.dword(pvar)] = classe[1:]      # `TMainForm` -> `MainForm`
    if len(saida) != 18:
        raise DumpError(
            f"{REL_EXE}: {len(saida)} sitios de CreateForm no WinMain, esperava 18")
    return saida


# ----------------------------------------------------------------- entrada ---
def le_handlers() -> list[dict]:
    linhas = PUB.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    saida = []
    for linha in linhas[1:]:
        c = dict(zip(cab, linha.split("\t")))
        saida.append({"endereco": int(c["endereco"], 16),
                      "handler": c["handler"],
                      "formulario": c["formulario"],
                      "regra": c["regra"]})
    return saida


def le_campos() -> dict[str, dict[int, tuple[str, str]]]:
    saida: dict[str, dict[int, tuple[str, str]]] = {}
    linhas = CAMPOS.read_text(encoding="utf-8").splitlines()
    for linha in linhas[1:]:
        form, off, campo, classe = linha.split("\t")
        saida.setdefault(form, {})[int(off, 16)] = (campo, classe)
    return saida


# ------------------------------------------------------------ classificacao --
def classifica(pe: PE, corpo: bytes, tam: int) -> tuple[str, dict]:
    """A forma do corpo, e o que ela carrega."""
    if corpo[:1] == b"\xc3":
        return "vazio", {}
    m = re.match(rb"\xba(....)\xa1(....)\xe8(....)\xc3", corpo)
    if m:
        return "cor", {
            "cor": struct.unpack("<I", m.group(1))[0],
            "global": struct.unpack("<I", m.group(2))[0],
            "alvo": None,   # preenchido pelo chamador, que tem o IAT
            "rel": struct.unpack("<i", m.group(3))[0],
            "bytes": 15,
        }
    m = re.match(rb"\x8b\x80(....)\x8b\x10\xff\x92(....)\xc3", corpo)
    if m:
        return "campo", {
            "campo": struct.unpack("<I", m.group(1))[0],
            "slot": struct.unpack("<I", m.group(2))[0],
            "bytes": 15,
        }
    return "composto", {"bytes": tam}


def inventario(pe: PE, corpo: bytes, ini: int, campos: dict[int, tuple[str, str]],
               iat: dict[int, str]) -> dict:
    """O que um corpo `composto` toca: importados, cores, literais, campos."""
    importados: list[str] = []
    for m in re.finditer(rb"\xe8", corpo):
        p = m.start()
        if p + 5 > len(corpo):
            break
        alvo = ini + p + 5 + struct.unpack_from("<i", corpo, p + 1)[0]
        nome = resolve_thunk(pe, alvo, iat)
        if nome and nome not in importados:
            importados.append(nome)
    cores: list[int] = []
    literais: list[str] = []

    def anota(va: int) -> None:
        texto = pe.cstring(va)
        if texto is not None and len(texto) >= 3 and texto not in literais:
            literais.append(texto)

    for m in re.finditer(rb"[\xb8\xba](....)", corpo):
        anota(struct.unpack("<I", m.group(1))[0])
    # O C++Builder agrupa os literais de uma funcao numa base carregada em EDI
    # (`mov edi,0x424754`) e alcanca cada um por `lea <reg>,[edi+disp32]`. Sem
    # este segundo caminho, o `MainForm.FormCreate` apareceria sem literal
    # nenhum -- e ele monta seis caminhos de pasta.
    base_edi = None
    m = re.search(rb"\xbf(....)", corpo)
    if m and pe.off(struct.unpack("<I", m.group(1))[0]) is not None:
        base_edi = struct.unpack("<I", m.group(1))[0]
    if base_edi is not None:
        for m in re.finditer(rb"\x8d[\x87\x8f\x97\x9f\xa7\xaf\xb7\xbf](....)", corpo):
            anota(base_edi + struct.unpack("<I", m.group(1))[0])
    for m in re.finditer(rb"\xba(....)\xe8(....)", corpo):
        alvo = ini + m.start() + 10 + struct.unpack("<i", m.group(2))[0]
        if (resolve_thunk(pe, alvo, iat) or "").startswith("@Controls@TControl@SetColor"):
            v = struct.unpack("<I", m.group(1))[0]
            if v not in cores:
                cores.append(v)
    tocados: list[str] = []
    for m in re.finditer(rb"\x8b[\x80-\xbf](...)\x00", corpo):
        desl = struct.unpack("<I", corpo[m.start() + 2:m.start() + 6])[0]
        alvo = campos.get(desl)
        if alvo and alvo[0] not in tocados:
            tocados.append(alvo[0])
    return {"importados": importados, "cores": cores,
            "literais": literais, "campos": sorted(tocados)}


def slot_virtual(bpls: list[PE], classe: str, slot: int) -> str:
    """Nome do metodo no slot `slot` do VMT de `classe`, achado nos packages."""
    for pe in bpls:
        vmt = pe.vmts().get(classe)
        if vmt is None:
            continue
        alvo = pe.dword(vmt + slot)
        nome = pe.exports().get(alvo - pe.base)
        if nome:
            return nome
    raise DumpError(
        f"nao achei o slot {slot:#x} de {classe} nos packages -- "
        f"a classe nao esta em {', '.join(BPLS)}?")


# ------------------------------------------------------------------- saida ---
def medir() -> list[dict]:
    pe = PE(EXE.read_bytes(), REL_EXE)
    bpls = []
    for nome in BPLS:
        caminho = EXE.parent / nome
        if not caminho.exists():
            raise DumpError(f"we-team-editor/{nome}: ausente")
        bpls.append(PE(caminho.read_bytes(), f"we-team-editor/{nome}"))
    iat = pe.imports()
    donos = globais_dos_formularios(pe)
    todos = le_handlers()
    campos = le_campos()
    enderecos = sorted(h["endereco"] for h in todos)

    alvo = [h for h in todos if h["regra"] == "R2"]
    if len(alvo) != 18:
        raise DumpError(f"{REL_PUB}: {len(alvo)} handlers R2, esperava 18")

    medidas = []
    for h in sorted(alvo, key=lambda x: x["endereco"]):
        ini = h["endereco"]
        o = pe.off(ini)
        # O teto da varredura e o handler seguinte quando ele esta perto, e o
        # limite duro quando nao esta -- o `MainForm.FormShow` so tem outro
        # handler 64 KB adiante, e inventariar essa janela poria no relatorio
        # codigo que nao e dele. Quem decide o fim e o `extent`, instrucao a
        # instrucao.
        seguinte = next((e for e in enderecos if e > ini), ini + TETO)
        teto = pe.off(min(seguinte, ini + TETO))
        tam = extent(pe.data, o, teto, f"{h['formulario']}.{h['handler']}") - o
        corpo = pe.data[o:o + max(tam, JANELA)]
        forma, dados = classifica(pe, corpo, tam)
        meus = campos.get(h["formulario"], {})

        detalhe = ""
        if forma == "cor":
            dono = donos.get(dados["global"])
            if dono is None:
                raise DumpError(
                    f"{h['formulario']}.{h['handler']}: o global "
                    f"{dados['global']:#010x} nao e instancia de formulario nenhum")
            if dono != h["formulario"]:
                raise DumpError(
                    f"{h['formulario']}.{h['handler']}: colore o {dono}, nao a si")
            # o `call rel32` comeca em +10 e ocupa 5 bytes: o alvo e relativo a +15
            nome = resolve_thunk(pe, ini + 15 + dados["rel"], iat)
            if not (nome or "").startswith("@Controls@TControl@SetColor"):
                raise DumpError(
                    f"{h['formulario']}.{h['handler']}: a chamada nao e SetColor "
                    f"e sim {nome}")
            detalhe = f"Color := ${dados['cor']:08X}"
            dados["simbolo"] = nome
        elif forma == "campo":
            alvo_campo = meus.get(dados["campo"])
            if alvo_campo is None:
                raise DumpError(
                    f"{h['formulario']}.{h['handler']}: {dados['campo']:#x} nao e "
                    f"campo publicado — regere o {REL_CAMPOS}")
            nome_campo, classe = alvo_campo
            metodo = slot_virtual(bpls, classe, dados["slot"])
            dados["nome_campo"], dados["classe"], dados["metodo"] = (
                nome_campo, classe, metodo)
            curto = metodo.split("@")[-1].split("$")[0]
            detalhe = f"{nome_campo}.{curto}"
        elif forma == "vazio":
            dados["bytes"] = 1
            detalhe = "—"
        else:
            dados.update(inventario(pe, corpo[:tam], ini, meus, iat))
            detalhe = f"{len(dados['campos'])} campo(s), {len(dados['cores'])} cor(es)"

        medidas.append({**h, "forma": forma, "dados": dados, "detalhe": detalhe})
    return medidas


def gera_tsv(medidas: list[dict]) -> str:
    linhas = ["endereco\tformulario\thandler\tforma\tbytes\tresumo"]
    for m in medidas:
        linhas.append("\t".join((
            f"{m['endereco']:#010x}", m["formulario"], m["handler"], m["forma"],
            str(m["dados"].get("bytes", 0)), m["detalhe"])))
    return "\n".join(linhas) + "\n"


def gera_md(medidas: list[dict]) -> str:
    por_forma: dict[str, int] = {}
    for m in medidas:
        por_forma[m["forma"]] = por_forma.get(m["forma"], 0) + 1
    cores = sorted({m["dados"]["cor"] for m in medidas if m["forma"] == "cor"})

    w: list[str] = []
    a = w.append
    a("# `re/arranque.md` — o que os 18 `FormCreate`/`FormShow` fazem")
    a("")
    a("Produto da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md), grupo de")
    a("carga. Gerado por [`../tools/dump_arranque.py`](../tools/dump_arranque.py),")
    a(f"a partir de `{REL_EXE}`, de [`published_methods.tsv`](published_methods.tsv)")
    a("e de [`campos.tsv`](campos.tsv). **Não editar à mão:**")
    a("")
    a("```sh")
    a(f"python3 {GENERATOR}")
    a(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    a("```")
    a("")
    a("A tabela está em [`arranque.tsv`](arranque.tsv); este arquivo é a leitura")
    a("dela. **Todo número daqui saiu do script.**")
    a("")
    a("## Eles não são todos triviais, e é isso que a medição diz")
    a("")
    a("A leitura barata seria \"inicialização de formulário, deve ser trivial\".")
    a("Medido, os 18 se separam em quatro formas:")
    a("")
    a("| Forma | Quantos | O que o corpo é |")
    a("|---|---:|---|")
    for forma, texto in (
            ("vazio", "um `ret`. O handler está ligado no DFM e não faz nada"),
            ("cor", "uma chamada a `TControl::SetColor` sobre a própria instância"),
            ("campo", "uma chamada virtual sobre um campo publicado"),
            ("composto", "qualquer outra coisa — inventariada abaixo")):
        a(f"| `{forma}` | {por_forma.get(forma, 0)} | {texto} |")
    a("")
    a("A forma sai de casar o corpo contra o padrão de bytes de cada uma. Quando")
    a("nenhum casa, o script chama de `composto` e inventaria — padrão que deixe")
    a("de valer vira `composto` sozinho, nunca classificação errada em silêncio.")
    a("")
    a("## Os 18")
    a("")
    a("| Endereço | Formulário | Handler | Forma | Bytes | Resumo |")
    a("|---|---|---|---|---:|---|")
    for m in medidas:
        a(f"| `{m['endereco']:#010x}` | `{m['formulario']}` | `{m['handler']}` | "
          f"{m['forma']} | {m['dados'].get('bytes', 0)} | {m['detalhe']} |")
    a("")
    a("## As cores")
    a("")
    a("`TColor` da VCL é `$00BBGGRR`, **não** `#RRGGBB`: trocar a ordem daria um")
    a("formulário laranja onde o original é azul. A coluna RGB abaixo já vem")
    a("invertida, e é ela que o Pascal do port usa.")
    a("")
    a(f"São {len(cores)} valores distintos nos {por_forma.get('cor', 0)} handlers")
    a("de forma `cor`:")
    a("")
    a("| `TColor` | R | G | B | Formulários |")
    a("|---|---:|---:|---:|---|")
    for c in cores:
        quem = ", ".join(f"`{m['formulario']}`" for m in medidas
                         if m["forma"] == "cor" and m["dados"]["cor"] == c)
        a(f"| `${c:08X}` | {c & 0xFF} | {(c >> 8) & 0xFF} | {(c >> 16) & 0xFF} | "
          f"{quem} |")
    a("")
    a("Nos 18 DFM a propriedade `Color` do formulário é `clBtnFace`, `clSilver` ou")
    a("`clNavy` — nenhuma delas é isto. A cor de projeto **nunca aparece na tela**:")
    a("o `OnCreate` a substitui antes de o formulário ser exibido. Um port que")
    a("respeitasse só o DFM ficaria cinza onde o original é colorido, e a")
    a("[WTE-TASK-12](../../docs/tasks/12-comparacao-visual.md) comparou justamente")
    a("as janelas nesse estado.")
    a("")
    compostos = [m for m in medidas if m["forma"] == "composto"]
    if compostos:
        a("## Os `composto`, um a um")
        a("")
        a("O inventário não é a spec — é o que a spec tem de explicar, e é um piso,")
        a("não um teto: campos são os de [`campos.tsv`](campos.tsv) alcançados por")
        a("`mov <reg>,[<reg>+disp32]`, e literais são as cadeias ASCII apontadas por")
        a("operando imediato ou por `lea <reg>,[edi+disp32]` sobre a base que o")
        a("C++Builder carrega em `EDI`.")
        a("")
        for m in compostos:
            d = m["dados"]
            a(f"### `{m['formulario']}.{m['handler']}` — `{m['endereco']:#010x}`, "
              f"{d['bytes']} bytes")
            a("")
            a(f"- **Campos tocados:** " +
              (", ".join(f"`{c}`" for c in d["campos"]) or "nenhum"))
            a(f"- **Cores:** " +
              (", ".join(f"`${c:08X}`" for c in d["cores"]) or "nenhuma"))
            a(f"- **Literais:** " +
              (", ".join(f"`{s}`" for s in d["literais"]) or "nenhum"))
            a(f"- **Importados chamados:** " +
              (", ".join(f"`{s}`" for s in d["importados"]) or "nenhum"))
            a("")
    return "\n".join(w)


def generate() -> dict[str, str]:
    medidas = medir()
    return {TSV_NAME: gera_tsv(medidas), MD_NAME: gera_md(medidas)}


def do_check(files: dict[str, str]) -> int:
    problemas = []
    for nome, conteudo in sorted(files.items()):
        caminho = OUT / nome
        if not caminho.exists():
            problemas.append(f"{nome}: nao existe")
            continue
        no_disco = caminho.read_text(encoding="utf-8")
        if no_disco == conteudo:
            print(f"dump_arranque: {REL_OUT}/{nome}: ok")
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
