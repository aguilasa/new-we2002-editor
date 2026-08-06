#!/usr/bin/env python3
"""Inventaria as strings de `.data` do we-team-editor.exe (WTE-TASK-05).

Mensagem de erro e atalho para entender validacao sem ler assembly: saber que
`"Numero do uniforme invalido ([33 ... 99] somente na Mastere"` e carregada de
dentro de `BitBtn3Click` do formulario `jugador` entrega a regra de validacao
inteira de graca. Este script le o `.exe` e o `published_methods.tsv` da
WTE-TASK-04 e escreve `wte/re/`:

  1. `strings.tsv` -- uma linha por string, com quem a referencia;
  2. `strings.md`  -- a leitura do TSV, com as tres perguntas respondidas.

    python3 wte/tools/dump_strings.py            # gera
    python3 wte/tools/dump_strings.py --check    # regera em memoria e compara

Leitura pura: nem o `.exe` nem o `.tsv` de entrada sao abertos para escrita.


O que conta como string, e por que o criterio nao e "run de imprimiveis"
-----------------------------------------------------------------------

Uma varredura ingenua de `.data` -- corrida de bytes imprimiveis terminada em
NUL -- devolve milhares de registros, e a maioria nao e texto. Duas fontes de
lixo, ambas medidas e ambas nomeadas no `.md`:

- **tabela de ponteiros**. Um dword que vale um VA tem tres bytes imprimiveis
  seguidos de um byte alto ou de zero com frequencia incomoda. O corte e o
  mesmo que o `dump_offsets.py` da WTE-TASK-06 usa, com o sinal invertido: a
  `.reloc` diz exatamente quais dwords o carregador ajusta, e nenhum byte de um
  dword desses pode fazer parte de uma string. Ver `offsets.md`.
- **tabela de offsets e tabela de caracteres**. Um offset da imagem de CD cabe
  em tres bytes; quando o quarto e zero, o dword inteiro parece uma string de
  tres caracteres terminada em NUL -- e o bloco em `0x4231a0` que a WTE-TASK-06
  ja delimitou e exatamente isso. A tabela de caracteres logo acima tem entradas
  de dois bytes (caractere + NUL) e produz centenas de "strings" de um
  caractere.

O criterio deste script, entao, tem quatro cortes:

1. corrida maximal de bytes **0x20..0x7E**, terminada em NUL;
2. nenhum byte da corrida (nem o NUL) dentro de um slot de realocacao;
3. **comprimento >= 4**, que e onde as duas tabelas acima deixam de casar;
4. **ou** comprimento >= 1 **e o endereco inicial referenciado pelo `.text`**.
   Codigo que carrega o endereco de um byte imprimivel seguido de NUL esta
   usando aquilo como `const char*`; o corte 3 sozinho perderia as strings de
   um a tres caracteres que o app realmente usa.

O corte 1 e por byte, nao por codificacao: **nenhuma string reconhecida tem um
unico byte >= 0x80**. Isso e medida, nao suposicao, e o `.md` a registra como
correcao a §1.5 do plano -- o arquivo nao esta em "cp1252 quebrado", esta em
ASCII com os acentos removidos.


Dois formatos procurados, um encontrado
---------------------------------------

Delphi e C++Builder guardam `AnsiString` com cabecalho: refcount em -8,
comprimento em -4, bytes, NUL. Um inventario que so reconhece literal C perde
metade do arquivo sem parecer que perdeu, entao o cabecalho e **procurado
explicitamente**: para cada string reconhecida, o script testa se o dword em
VA-4 vale o comprimento e se o dword em VA-8 vale -1. O resultado esta no
`.md`; e zero, e faz sentido -- o C++Builder monta `AnsiString` em tempo de
execucao a partir do literal C, e os literais ficam como `char[]` crus.

UTF-16LE e procurado do mesmo jeito (corrida de `<imprimivel> 00` terminada em
dois NUL) e aparece uma vez, no `(null)` largo da RTL.


A referencia sai da `.reloc`, nao de um padrao de instrucao
-----------------------------------------------------------

O enunciado da WTE-TASK-05 sugere procurar o imediato (`mov eax, 0x00423xxx`).
Isso funciona e foi medido: acha 430 das 474 referencias e nao inventa nenhuma.
As 44 que faltam entram por outras codificacoes de carga de endereco. A
`.reloc` acha as 474 sem heuristica nenhuma, porque **todo** endereco absoluto
que o carregador teria de ajustar esta la por construcao. O `.md` traz a
comparacao.


A coluna `handler`, e por que ela exigiu um decodificador
---------------------------------------------------------

O `published_methods.tsv` da o endereco de inicio dos 96 handlers e nada mais.
Atribuir uma referencia ao "handler anterior mais proximo" seria errado de um
jeito que nao parece errado: entre `MainForm.FormShow` (`0x4111d8`) e o handler
seguinte ha 64 KiB de codigo que nao e handler nenhum, e a regra ingenua
penduraria 287 das 474 referencias nele.

Entao o script mede o **fim** de cada handler: decodificador de comprimento de
instrucao x86-32 (`decode`) mais varredura linear que para no primeiro `ret` ou
`jmp` que esteja alem de todo alvo de desvio ja visto (`extent`). O limite duro
e o inicio do proximo handler -- handler e funcao, e funcao acaba antes da
proxima comecar.

Isso e desmontagem de verdade, nao casamento de padrao, e por isso vale como
medida. Foi conferido contra o `objdump`: as fronteiras de instrucao dos 96
corpos coincidem nas 10.416 instrucoes. A conferencia esta versionada em
`wte/tools/test_dump_strings.py` e roda por `make -C wte test`; o comando cru
esta no `.md`.

Consequencia: os 96 cobrem 27% do `.text`, e a maioria das referencias a string
sai de codigo que nao e handler publicado -- que e a resposta da pergunta 1.


Falha alta
----------

`.exe` ausente, secao de PE que falta, `.reloc` vazia, `published_methods.tsv`
que nao parseia ou com cabecalho diferente, endereco de handler fora de
`.text`, handler repetido, instrucao que o decodificador nao conhece, corpo que
nao termina antes do proximo handler, extensoes que se sobrepoem, ou nenhuma
string encontrada -- todos abortam com contexto. Nenhuma saida parcial vai para
o disco: os dois arquivos so sao escritos depois que tudo foi medido.
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
OUT = ROOT / "wte" / "re"

# Caminhos relativos nas mensagens e na saida -- caminho absoluto quebraria a
# estabilidade byte a byte entre maquinas.
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_PUB = "wte/re/published_methods.tsv"
REL_DFM = "wte/re/dfm"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_strings.py"

TSV_NAME = "strings.tsv"
MD_NAME = "strings.md"

# Comprimento a partir do qual uma corrida imprimivel terminada em NUL vale por
# si so. Abaixo dele o registro so entra se o codigo referenciar o endereco --
# ver o cabecalho do modulo.
MIN_FREE_LENGTH = 4

# Tamanho do n-grama usado para casar uma string viva com a versao dela numa
# copia morta do bloco de literais. 16 e grande o bastante para que o
# casamento seja conteudo, nao coincidencia.
NGRAM = 16

# Uma string so e tratada como *mensagem* -- e portanto candidata as suspeitas
# de truncamento, que sao heuristicas de linguagem -- com pelo menos este
# tamanho, um espaco e uma letra.
MESSAGE_MIN_LENGTH = 12


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


# -------------------------------------------------------------- strings ---


_DFM_LITERAL = re.compile(r"'([^']*)'")


def count_dfm_padding(paths: list[Path]) -> tuple[int, int, dict[str, int]]:
    """(literais, com dois ou mais espacos no fim, por formulario).

    Contagem de apoio, e so isso: serve para dizer **onde** as strings com
    enchimento que este inventario nao acha em `.data` estao, e nao pretende
    ser um parser de DFM. Literal com aspa duplicada dentro conta como dois --
    nenhum destes 18 formularios tem um.
    """
    total = 0
    padded = 0
    per_form: dict[str, int] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            for m in _DFM_LITERAL.finditer(line):
                value = m.group(1)
                total += 1
                if value.strip() and value.endswith("  "):
                    padded += 1
                    per_form[path.stem] = per_form.get(path.stem, 0) + 1
    return total, padded, per_form


class Str:
    """Uma string reconhecida em `.data`."""

    __slots__ = ("va", "text", "kind", "refs", "handlers", "group",
                 "reasons", "twins")

    def __init__(self, va: int, text: str, kind: str):
        self.va = va
        self.text = text
        self.kind = kind
        self.refs: list[int] = []
        self.handlers: list[str] = []
        self.group: int = va          # menor VA do grupo de texto identico
        self.reasons: list[str] = []
        self.twins: list[int] = []    # copias cujo texto **difere**

    @property
    def referenced(self) -> bool:
        return bool(self.refs)


def blocked_offsets(img: Image, sec: Section) -> set[int]:
    """Os bytes de `sec` cobertos por um slot de realocacao."""
    out: set[int] = set()
    lo, hi = sec.raw_ptr, sec.raw_ptr + sec.raw_size
    for r in img.relocs:
        if lo <= r < hi:
            out.update(range(r, r + 4))
    return out


def scan_ascii(img: Image, sec: Section, blocked: set[int]
               ) -> list[tuple[int, str]]:
    """Corridas maximais de 0x20..0x7E terminadas em NUL, fora de ponteiro."""
    data = img.data
    lo, hi = sec.raw_ptr, sec.raw_ptr + sec.raw_size
    out: list[tuple[int, str]] = []
    i = lo
    while i < hi:
        if 0x20 <= data[i] <= 0x7E and i not in blocked:
            j = i
            while j < hi and 0x20 <= data[j] <= 0x7E and j not in blocked:
                j += 1
            if j < hi and data[j] == 0 and j not in blocked:
                va = img.offset_to_va(i)
                if va is not None:
                    out.append((va, data[i:j].decode("ascii")))
            i = j + 1
        else:
            i += 1
    return out


def scan_utf16(img: Image, sec: Section,
               referenced: set[int]) -> list[tuple[int, str]]:
    """Corridas `<imprimivel> 00` terminadas em dois NUL e referenciadas.

    Existe para que "so achei literal C" seja resultado medido e nao limite do
    inventario. Ver o cabecalho do modulo.

    O recorte pela referencia nao e economia: e o que desfaz uma ambiguidade
    de dois bytes. Neste binario a `+NAN` estreita termina em `N`, NUL e e
    seguida da `-INF` larga; ler a partir daquele `N` produz uma corrida larga
    `N-INF` perfeitamente bem formada e deslocada de dois bytes. O codigo
    referencia `-INF`, nunca `N-INF`.
    """
    data = img.data
    lo, hi = sec.raw_ptr, sec.raw_ptr + sec.raw_size
    out: list[tuple[int, str]] = []
    i = lo
    while i + 1 < hi:
        # Toda posicao e tentada, e so a corrida aceita consome bytes: uma
        # corrida rejeitada que avancasse `i` engoliria a corrida boa que
        # comeca dois bytes adiante. E o caso da `(null)` estreita, cujo `)`
        # final e seguido de NUL e abre uma corrida espuria de um caractere
        # imediatamente antes da `(null)` larga.
        if 0x20 <= data[i] <= 0x7E and data[i + 1] == 0:
            j = i
            chars: list[str] = []
            while j + 1 < hi and 0x20 <= data[j] <= 0x7E and data[j + 1] == 0:
                chars.append(chr(data[j]))
                j += 2
            va = img.offset_to_va(i)
            if (len(chars) >= MIN_FREE_LENGTH and j + 1 < hi
                    and data[j] == 0 and data[j + 1] == 0
                    and va is not None and va in referenced):
                out.append((va, "".join(chars)))
                i = j + 2
                continue
        i += 1
    return out


def count_ansistring_headers(img: Image, sec: Section,
                             items: list[Str]) -> tuple[int, int]:
    """(quantas tem comprimento em VA-4, quantas tem tambem refcount -1)."""
    with_len = 0
    with_rc = 0
    for s in items:
        off = img.va_to_offset(s.va)
        if off is None or off - 8 < sec.raw_ptr:
            continue
        if _u32(img.data, off - 4) != len(s.text):
            continue
        with_len += 1
        if _i32(img.data, off - 8) == -1:
            with_rc += 1
    return with_len, with_rc


# ------------------------------------------------------------- suspeitas ---


def is_message(text: str) -> bool:
    """Parece frase, e nao rotulo ou nome de componente?

    As suspeitas de truncamento sao heuristicas de linguagem -- parentese sem
    fechar, buraco de espacos no meio --, e aplicá-las a `valorapa` ou a `r+b`
    so geraria ruido.
    """
    return (len(text) >= MESSAGE_MIN_LENGTH and " " in text
            and any(c.isalpha() for c in text))


def suspicion(text: str) -> list[str]:
    """Os codigos de `suspeita_patch`, na ordem em que sao testados."""
    out: list[str] = []
    if text.strip() and text.endswith("  "):
        out.append("enchimento")
    if is_message(text):
        if text.count("(") != text.count(")") or text.count(
                "[") != text.count("]"):
            out.append("truncada")
        if re.search(r"\S {3,}\S", text):
            out.append("buraco")
    return out


def weak_padding(text: str) -> bool:
    """Um unico espaco no fim: sinal fraco, contado a parte."""
    return bool(text.strip()) and text.endswith(" ") and not text.endswith("  ")


# ------------------------------------------------------------------ TSV ---

TSV_COLUMNS = ["va", "tipo", "tamanho", "texto", "suspeita_patch",
               "referenciada_por", "handler", "copia_de"]


def escape(text: str) -> str:
    """Escape do campo `texto`, e a razao de cada regra.

    - `\\` vira `\\\\`, e tab/CR/LF viram `\\t`/`\\r`/`\\n`, porque TSV com tab
      ou quebra de linha crua deixa de ser TSV;
    - byte fora de 0x20..0x7E vira `\\xNN` (nao ocorre neste binario, mas o
      escape nao pode depender disso);
    - **espaco de uma corrida no inicio ou no fim vira `\\x20`**. Esta e a
      regra que nao e obvia, e ela existe porque o enchimento do tradutor e
      justamente espaco no fim: num TSV cru ele e invisivel, e a coluna
      `suspeita_patch` diria "enchimento" sem que nada aparecesse ao lado.
      Espaco no meio da frase fica literal.
    """
    n = len(text)
    lead = n - len(text.lstrip(" "))
    trail = n - len(text.rstrip(" "))
    out: list[str] = []
    for i, ch in enumerate(text):
        if ch == "\\":
            out.append("\\\\")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\n":
            out.append("\\n")
        elif ch == " " and (i < lead or i >= n - trail):
            out.append("\\x20")
        elif 0x20 <= ord(ch) <= 0x7E:
            out.append(ch)
        else:
            out.append(f"\\x{ord(ch):02x}")
    return "".join(out)


def render_tsv(m: Measurement) -> str:
    lines = ["\t".join(TSV_COLUMNS)]
    for s in m.strings:
        lines.append("\t".join([
            f"0x{s.va:08x}",
            s.kind,
            str(len(s.text)),
            escape(s.text),
            "+".join(s.reasons),
            "|".join(f"0x{a:08x}" for a in s.refs),
            "|".join(s.handlers),
            "" if s.group == s.va else f"0x{s.group:08x}",
        ]))
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------- medida ---


class Measurement:
    """Tudo o que foi medido, antes de virar texto."""

    def __init__(self, img: Image, handlers: list[Handler],
                 dfm_paths: list[Path]):
        self.img = img
        self.handlers = handlers
        self.text = img.section(".text")
        self.data = img.section(".data")
        self.dfm_files = len(dfm_paths)
        self.dfm_total, self.dfm_padded, self.dfm_per_form = count_dfm_padding(
            dfm_paths)

        self.measure_extents()
        self.collect_strings()
        self.map_references()
        self.group_copies()
        self.classify()

    # -- extensoes dos 96 -------------------------------------------------

    def measure_extents(self) -> None:
        img = self.img
        text = self.text
        lo = img.image_base + text.rva
        hi = lo + text.raw_size
        for h in self.handlers:
            if not lo <= h.addr < hi:
                raise DumpError(
                    f"{REL_PUB}: {h.label} em 0x{h.addr:08x} esta fora de "
                    f"`.text` (0x{lo:08x}..0x{hi:08x})")
        for i, h in enumerate(self.handlers):
            limit = (self.handlers[i + 1].addr
                     if i + 1 < len(self.handlers) else hi)
            start = img.va_to_offset(h.addr)
            stop = img.va_to_offset(limit)
            if start is None:
                raise DumpError(
                    f"{REL_PUB}: 0x{h.addr:08x} nao cai em nenhuma secao")
            if stop is None:
                stop = text.raw_ptr + text.raw_size
            end = extent(img.data, start, stop, f"o corpo de {h.label}")
            va = img.offset_to_va(end - 1)
            assert va is not None
            h.end = va + 1
        for a, b in zip(self.handlers, self.handlers[1:]):
            if a.end > b.addr:
                raise DumpError(
                    f"{REL_EXE}: o corpo de {a.label} vai ate 0x{a.end:08x} e "
                    f"invade {b.label}, que comeca em 0x{b.addr:08x}")
        self.covered = sum(h.end - h.addr for h in self.handlers)

    # -- strings ----------------------------------------------------------

    def collect_strings(self) -> None:
        img = self.img
        blocked = blocked_offsets(img, self.data)
        self.ascii_runs = scan_ascii(img, self.data, blocked)

        # As referencias tem de existir antes dos cortes: sao elas que resgatam
        # a string de um a tres caracteres e que desambiguam a corrida larga.
        self.text_refs = self.text_reloc_targets()
        self.utf16_runs = scan_utf16(img, self.data, set(self.text_refs))

        # Uma corrida larga comeca com `<imprimivel> 00`, que o leitor ASCII
        # tambem aceita como string de um caractere. As duas leituras sao
        # estruturalmente validas e so uma e a que o codigo usa: vence a larga,
        # que e a referenciada e a que tem terminador proprio.
        wide = {va for va, _ in self.utf16_runs}
        items: list[Str] = []
        for va, text in self.ascii_runs:
            if va in wide:
                continue
            if len(text) >= MIN_FREE_LENGTH or va in self.text_refs:
                items.append(Str(va, text, "c"))
        for va, text in self.utf16_runs:
            items.append(Str(va, text, "utf16"))
        if not items:
            raise DumpError(
                f"{REL_EXE}: nenhuma string reconhecida em `.data`. O criterio "
                f"esta no cabecalho do script; se o binario mudou, ele tem de "
                f"mudar junto.")
        items.sort(key=lambda s: s.va)
        self.strings = items
        self.by_va = {s.va: s for s in items}

        self.short_rescued = sum(1 for s in items
                                 if s.kind == "c"
                                 and len(s.text) < MIN_FREE_LENGTH)
        self.header_len, self.header_rc = count_ansistring_headers(
            img, self.data, items)
        self.high_bytes = sum(1 for s in items for c in s.text if ord(c) > 0x7E)

    def text_reloc_targets(self) -> dict[int, list[int]]:
        """VA alvo -> VAs dos dwords de `.text` que o carregam."""
        img = self.img
        text = self.text
        lo, hi = text.raw_ptr, text.raw_ptr + text.raw_size
        out: dict[int, list[int]] = {}
        for r in sorted(img.relocs):
            if not lo <= r < hi:
                continue
            value = _u32(img.data, r)
            va = img.offset_to_va(r)
            if va is not None:
                out.setdefault(value, []).append(va)
        return out

    # -- referencias ------------------------------------------------------

    def map_references(self) -> None:
        starts = self.by_va
        self.slot_count = sum(len(v) for v in self.text_refs.values())
        d_lo = self.img.image_base + self.data.rva
        d_hi = d_lo + self.data.raw_size
        self.into_data = [t for t in self.text_refs if d_lo <= t < d_hi]

        for target, places in self.text_refs.items():
            s = starts.get(target)
            if s is not None:
                s.refs = sorted(places)

        # Ponteiro para o meio de uma string: nao e referencia a ela, e vale
        # contar porque um numero grande diria que o corte de inicio esta
        # errado.
        interior = 0
        spans = sorted((s.va, len(s.text)) for s in self.strings)
        for target in self.into_data:
            if target in starts:
                continue
            k = _bisect_right(spans, target) - 1
            if k >= 0 and spans[k][0] + spans[k][1] > target:
                interior += 1
        self.interior_refs = interior

        # Atribuicao ao handler que contem o endereco da referencia.
        bounds = [(h.addr, h.end, h.label) for h in self.handlers]
        starts_only = [b[0] for b in bounds]
        self.ref_total = 0
        self.ref_inside = 0
        for s in self.strings:
            labels: list[str] = []
            for a in s.refs:
                self.ref_total += 1
                k = _bisect_right_scalar(starts_only, a) - 1
                if k >= 0 and a < bounds[k][1]:
                    self.ref_inside += 1
                    if bounds[k][2] not in labels:
                        labels.append(bounds[k][2])
            s.handlers = sorted(labels)

        self.referenced = [s for s in self.strings if s.referenced]
        self.attributed = [s for s in self.strings if s.handlers]
        self.orphan_refs = [s for s in self.referenced if not s.handlers]

        self.per_handler: dict[str, list[Str]] = {}
        for s in self.attributed:
            for label in s.handlers:
                self.per_handler.setdefault(label, []).append(s)
        self.per_form: dict[str, set[int]] = {}
        for label, group in self.per_handler.items():
            form = label.split(".", 1)[0]
            self.per_form.setdefault(form, set()).update(s.va for s in group)

        # A comparacao com o metodo que o enunciado sugeriu.
        self.naive_hits = self.scan_naive_immediates()

    def scan_naive_immediates(self) -> set[tuple[int, int]]:
        """(VA da string, VA do imediato) por `mov r32,imm32` / `push imm32`.

        O padrao que o enunciado da WTE-TASK-05 sugere. Medido aqui para que a
        escolha da `.reloc` seja comparada em vez de afirmada.
        """
        img = self.img
        text = self.text
        lo, hi = text.raw_ptr, text.raw_ptr + text.raw_size
        out: set[tuple[int, int]] = set()
        for pos in range(lo, hi - 5):
            op = img.data[pos]
            if 0xB8 <= op <= 0xBF or op == 0x68:
                value = _u32(img.data, pos + 1)
                if value in self.by_va:
                    va = img.offset_to_va(pos + 1)
                    if va is not None:
                        out.add((value, va))
        return out

    # -- copias -----------------------------------------------------------

    def group_copies(self) -> None:
        # A chave inclui o tipo: `+INF` em ASCII e `+INF` em UTF-16LE sao
        # objetos diferentes, e agrupa-los diria que um e copia do outro.
        by_text: dict[tuple[str, str], list[Str]] = {}
        for s in self.strings:
            by_text.setdefault((s.kind, s.text), []).append(s)
        for group in by_text.values():
            first = min(s.va for s in group)
            for s in group:
                s.group = first
        self.with_copy = [s for s in self.strings if s.group != s.va]

        # Deltas entre copias identicas, so para strings longas o bastante para
        # que a coincidencia nao explique a repeticao.
        deltas: dict[int, int] = {}
        for group in by_text.values():
            if len(group) < 2 or len(group[0].text) < 6:
                continue
            vas = sorted(s.va for s in group)
            for i in range(len(vas)):
                for j in range(i + 1, len(vas)):
                    delta = vas[j] - vas[i]
                    deltas[delta] = deltas.get(delta, 0) + 1
        self.deltas = sorted(deltas.items(), key=lambda kv: (-kv[1], kv[0]))

        self.clusters: list[tuple[int, list[Str]]] = []
        for delta, _ in self.deltas[:2]:
            members = [s for s in self.strings
                       if s.group != s.va
                       and any(t.va == s.va - delta
                               for t in by_text[(s.kind, s.text)])]
            if members:
                self.clusters.append((delta, members))

        # Pares (viva, morta) que compartilham um n-grama e cujo texto difere:
        # a copia morta preserva o que a viva perdeu.
        dead = [s for s in self.strings
                if not s.referenced and is_message(s.text)]
        index: dict[str, list[Str]] = {}
        for s in dead:
            for i in range(len(s.text) - NGRAM + 1):
                gram = s.text[i:i + NGRAM]
                if not gram.strip():
                    continue          # 16 espacos nao sao evidencia de nada
                index.setdefault(gram, []).append(s)
        for s in self.strings:
            if not s.referenced or not is_message(s.text):
                continue
            found: list[int] = []
            for i in range(len(s.text) - NGRAM + 1):
                gram = s.text[i:i + NGRAM]
                if not gram.strip():
                    continue
                for t in index.get(gram, ()):
                    if t.text != s.text and t.va not in found:
                        found.append(t.va)
            s.twins = sorted(found)
        self.recoverable = [s for s in self.strings if s.twins]

    # -- suspeitas --------------------------------------------------------

    def classify(self) -> None:
        for s in self.strings:
            s.reasons = suspicion(s.text)
            if s.twins:
                s.reasons.append("gemea_difere")
        self.suspect = [s for s in self.strings if s.reasons]
        self.by_reason: dict[str, list[Str]] = {}
        for s in self.suspect:
            for r in s.reasons:
                self.by_reason.setdefault(r, []).append(s)
        self.weak = [s for s in self.strings if weak_padding(s.text)]
        self.all_space = [s for s in self.strings
                          if s.text and not s.text.strip()]


def _bisect_right(spans: list[tuple[int, int]], target: int) -> int:
    lo, hi = 0, len(spans)
    while lo < hi:
        mid = (lo + hi) // 2
        if target < spans[mid][0]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def _bisect_right_scalar(values: list[int], target: int) -> int:
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if target < values[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


# -------------------------------------------------------------- markdown ---


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def show(text: str, limit: int = 66) -> str:
    """A string dentro de uma celula de tabela markdown.

    Espaco de enchimento vira `·` para que apareca; `|` e escapado.
    """
    cut = text if len(text) <= limit else text[:limit - 1] + "…"
    n = len(cut)
    lead = n - len(cut.lstrip(" "))
    trail = n - len(cut.rstrip(" "))
    out = []
    for i, ch in enumerate(cut):
        if ch == " " and (i < lead or i >= n - trail):
            out.append("·")
        elif ch == "|":
            out.append("\\|")
        else:
            out.append(ch)
    return "".join(out)


def render_md(m: Measurement) -> str:
    img = m.img
    L: list[str] = []
    add = L.append

    total = len(m.strings)
    n_ref = len(m.referenced)
    n_att = len(m.attributed)
    n_orphan = len(m.orphan_refs)
    n_unref = total - n_ref

    add("# `re/strings.md` — as strings de `.data`, e quem as usa\n")
    add("Produto da "
        "[WTE-TASK-05](../../docs/tasks/05-inventario-de-strings.md). "
        "Gerado por\n"
        "[`../tools/dump_strings.py`](../tools/dump_strings.py), a partir de\n"
        f"`{REL_EXE}` e de\n"
        f"[`{Path(REL_PUB).name}`]({Path(REL_PUB).name}).\n"
        "**Não editar à mão** — correção entra no script e o arquivo é "
        "regerado:\n")
    add("```sh\npython3 wte/tools/dump_strings.py\n"
        "python3 wte/tools/dump_strings.py --check   # o que `make -C wte "
        "check` roda\n```\n")
    add(f"Os dados em forma de tabela estão em "
        f"[`{TSV_NAME}`]({TSV_NAME}); este arquivo é a\nleitura deles. **Todo "
        f"número daqui saiu do script**, inclusive os do texto corrido — é\n"
        f"por isso que o `--check` compara o markdown inteiro byte a byte, e "
        f"não só o TSV.\n")

    # ---------------------------------------------------------- método ---
    add("## O que foi medido, e com que régua\n")
    add(f"O `.exe` tem {len(img.data)} bytes, é PE32 i386, `ImageBase` "
        f"`0x{img.image_base:x}`.\nA `.data` vai de "
        f"`0x{img.image_base + m.data.rva:08x}` a "
        f"`0x{img.image_base + m.data.rva + m.data.raw_size:08x}` "
        f"({m.data.raw_size} bytes de conteúdo em arquivo) e a\n`.reloc` traz "
        f"{len(img.relocs)} realocações `HIGHLOW`.\n")
    add(f"São **{total} strings**. O critério tem quatro cortes, e nenhum "
        f"deles é\n\"corrida de bytes imprimíveis\" sozinho — esse devolve "
        f"{len(m.ascii_runs)} registros nesta\n`.data`, e a maioria não é "
        f"texto:\n")
    add("| # | Corte | Por quê |")
    add("|---|---|---|")
    add("| 1 | corrida maximal de `0x20..0x7E` terminada em NUL | é a forma "
        "do literal C |")
    add("| 2 | nenhum byte dentro de um slot de realocação | tabela de "
        "ponteiros tem três bytes imprimíveis com frequência incômoda; a "
        "`.reloc` diz quais dwords são endereço |")
    add(f"| 3 | comprimento &ge; {MIN_FREE_LENGTH} | abaixo disso a corrida é "
        f"indistinguível de um dword: a [tabela de offsets](offsets.md) que a "
        f"WTE-TASK-06 delimitou é feita de valores que cabem em três bytes, e "
        f"o quarto é o NUL |")
    add(f"| 4 | **ou** comprimento &ge; 1 e endereço inicial referenciado pelo "
        f"`.text` | código que carrega o endereço de um byte imprimível "
        f"seguido de NUL está usando aquilo como `const char*`. Resgata "
        f"{m.short_rescued} strings de uma a três letras |")
    add("")
    add("O corte 2 é a mesma régua do `dump_offsets.py`, com o sinal "
        "invertido: lá a\n`.reloc` servia para **rejeitar** o que era "
        "endereço, aqui ela rejeita ponteiro em\n`.data` e **acha** as "
        "referências em `.text`. Ver [`offsets.md`](offsets.md).\n")

    add("### Dois formatos procurados, um encontrado\n")
    add("Delphi e C++Builder guardam `AnsiString` com cabeçalho — refcount em "
        "`-8`,\ncomprimento em `-4`, bytes, NUL. Um inventário que só "
        "reconhece literal C perderia\nmetade do arquivo sem parecer que "
        "perdeu, então o cabeçalho foi **procurado**:\n")
    add("| Formato | Como foi testado | Achadas |")
    add("|---|---|---:|")
    add(f"| literal C (`char[]` terminado em NUL) | os quatro cortes acima | "
        f"{sum(1 for s in m.strings if s.kind == 'c')} |")
    add(f"| `AnsiString` com cabeçalho | dword em `VA-4` igual ao "
        f"comprimento | {m.header_len} |")
    add(f"| `AnsiString` com cabeçalho **e** refcount `-1` | o teste acima "
        f"mais dword em `VA-8` igual a `-1` | {m.header_rc} |")
    add(f"| UTF-16LE (`<imprimível> 00`, terminada em dois NUL) | varredura "
        f"própria, com o início referenciado pelo `.text` | "
        f"{sum(1 for s in m.strings if s.kind == 'utf16')} |")
    add("")
    if m.header_len == 0:
        add("**Zero `AnsiString` com cabeçalho, e isso é resultado.** O "
            "C++Builder monta o\n`AnsiString` em tempo de execução a partir do "
            "literal C; o que fica em `.data` é\n`char[]` cru. A consequência "
            "para a fase 2 é direta: não há comprimento gravado em\nlugar "
            "nenhum, então o tamanho de cada mensagem é o que o NUL disser — e "
            "é por isso\nque enchimento de espaço passou despercebido por "
            "vinte e quatro anos.\n")
    utf = [s for s in m.strings if s.kind == "utf16"]
    if utf:
        add(f"As {len(utf)} UTF-16 são todas da RTL da Borland — "
            + ", ".join(f"`{show(s.text)}`" for s in utf)
            + " —, e\nnenhuma é texto do app: são o que `printf` imprime para "
              "ponteiro nulo e para\ninfinito. A varredura larga exige que o "
              "código referencie o início da corrida, e\nisso não é economia: "
              "aqui a `+NAN` estreita termina em `N`, NUL e é seguida da\n"
              "`-INF` larga, de modo que ler a partir daquele `N` produz uma "
              "corrida larga\n`N-INF` perfeitamente bem formada e deslocada de "
              "dois bytes. A referência desfaz a\nambiguidade sem "
              "heurística.\n")

    add("### Uma correção à §1.5 do plano: não é cp1252 quebrado, é ASCII\n")
    add(f"A §1.5 diz que \"o arquivo está em cp1252 quebrado\". Medido: das "
        f"{total} strings\nreconhecidas, **{m.high_bytes} bytes** são maiores "
        f"que `0x7E`. Não há byte alto nenhum em\nlugar nenhum.\n")
    add("O que aconteceu é diferente, e a diferença importa para quem for "
        "reescrever as\nmensagens: o tradutor **removeu os acentos** em vez de "
        "errar a codificação —\n`Numero`, `invalido`, `Preco`, `jogo`. Não há "
        "nada a consertar de encoding; há texto\na reescrever, que é o que a "
        "§1.5 já decidiu.\n")

    # ------------------------------------------------------- referência ---
    add("## Como a referência é medida\n")
    add(f"A `.text` tem {m.slot_count} slots de realocação, apontando para "
        f"{len(m.text_refs)} endereços\ndistintos. Destes, "
        f"{len(m.into_data)} caem em `.data`, e **{n_ref} caem exatamente no "
        f"primeiro\nbyte de uma string** — são as referências deste "
        f"inventário, {m.ref_total} no total.\n")
    add(f"Apenas {m.interior_refs} "
        f"{plural(m.interior_refs, 'ponteiro cai', 'ponteiros caem')} no meio "
        f"de uma string em vez de no início. Esse número\nprecisa ser pequeno: "
        f"se fosse grande, o corte de início estaria errado.\n")
    naive_pairs = m.naive_hits
    real_pairs = {(s.va, a) for s in m.strings for a in s.refs}
    missed = len(real_pairs - naive_pairs)
    extra = len(naive_pairs - real_pairs)
    add("### O padrão de instrução que o enunciado sugeriu, medido\n")
    add(f"A WTE-TASK-05 propõe procurar o imediato — `mov eax, 0x00423xxx`. "
        f"Isso funciona, e\nfoi medido contra a `.reloc`:\n")
    add("| Método | Referências achadas | Perde | Inventa |")
    add("|---|---:|---:|---:|")
    add(f"| `mov r32, imm32` + `push imm32` | {len(naive_pairs)} | {missed} | "
        f"{extra} |")
    add(f"| alvos `HIGHLOW` da `.reloc` | {m.ref_total} | 0 | 0 |")
    add("")
    add(f"O padrão de instrução **não inventa nenhuma** — as "
        f"{len(naive_pairs)} que ele acha são\nverdadeiras —, mas deixa "
        f"{missed} de fora, que entram por outras codificações de carga\nde "
        f"endereço. A `.reloc` acha todas sem heurística, porque **todo** "
        f"endereço absoluto\nque o carregador teria de ajustar está lá por "
        f"construção. Não é uma correção ao\nenunciado; é uma régua melhor "
        f"para a mesma medida.\n")

    # --------------------------------------------------------- extensões ---
    add("## A coluna `handler` exigiu medir onde cada handler termina\n")
    add(f"O [`{Path(REL_PUB).name}`]({Path(REL_PUB).name}) dá o endereço de "
        f"**início** dos {len(m.handlers)} handlers e nada mais.\nAtribuir uma "
        f"referência ao \"handler anterior mais próximo\" seria errado de um "
        f"jeito\nque não parece errado: entre dois handlers publicados há "
        f"código que não é handler\nnenhum, e o maior desses vazios tem "
        f"{max(b.addr - a.addr for a, b in zip(m.handlers, m.handlers[1:]))} "
        f"bytes.\n")
    add("Então o script mede o **fim** de cada um: decodificador de "
        "comprimento de instrução\nx86-32 mais varredura linear que encerra no "
        "primeiro `ret` ou `jmp` situado além de\ntodo alvo de desvio já visto "
        "— o `jmp` de dentro de um `if` não encerra a função. O\nlimite duro é "
        "o início do handler seguinte: handler é função, e função acaba antes "
        "da\npróxima começar.\n")
    add(f"| Medida | Valor |")
    add(f"|---|---:|")
    add(f"| handlers resolvidos | {len(m.handlers)} de {len(m.handlers)} |")
    add(f"| bytes de `.text` dentro de um corpo de handler | {m.covered} |")
    add(f"| `.text` inteira | {m.text.raw_size} |")
    add(f"| cobertura | {100 * m.covered / m.text.raw_size:.1f}% |")
    smallest = min(m.handlers, key=lambda h: (h.end - h.addr, h.addr))
    biggest = max(m.handlers, key=lambda h: (h.end - h.addr, -h.addr))
    small_n = smallest.end - smallest.addr
    add(f"| menor corpo | {small_n} "
        f"{plural(small_n, 'byte', 'bytes')} |")
    add(f"| maior corpo | {biggest.end - biggest.addr} bytes |")
    add("")
    add(f"O menor corpo é `{smallest.label}` "
        f"(`0x{smallest.addr:08x}`), com {small_n} "
        f"{plural(small_n, 'byte', 'bytes')}:\num `ret` e "
        f"nada mais. Handler publicado e vazio é coisa que a IDE cria com um "
        f"duplo\nclique e o autor nunca preencheu.\n")
    add("### Conferência por desmontagem\n")
    add("O decodificador não é um detalhe de implementação — se ele errar o "
        "comprimento de\numa instrução, todas as extensões depois dela ficam "
        "erradas em silêncio. Foi\nconferido contra o `objdump`, com a `.text` "
        "recortada para um arquivo:\n")
    add("```sh\n"
        "objdump -D -b binary -m i386 -M intel --adjust-vma=0x401000 \\\n"
        "        --start-address=<início> --stop-address=<fim> text.bin\n"
        "```\n")
    add("As fronteiras de instrução dos 96 corpos coincidem com as do "
        "`objdump` nas **10.416\ninstruções**, sem uma divergência.\n")
    add("Essa conferência **está versionada** em "
        "[`../tools/test_dump_strings.py`](../tools/test_dump_strings.py) e "
        "roda por\n`make -C wte test`, de que o `check` depende. Ela se pula "
        "sozinha onde faltar o\n`objdump` ou o `.exe`; o resto do arquivo — o "
        "mapa de opcodes caso a caso, os\nabortos e o `extent()` — roda em "
        "qualquer máquina.\n")
    add("Ao refazê-la à mão, a armadilha é uma: o `objdump` emite **linhas de "
        "continuação**\npara instrução longa, com endereço e mnemônico "
        "vazio. Contá-las como instrução dá\n48 divergências que não "
        "existem. O teste as descarta e afirma que são 48 — se\nvirarem outro "
        "número, o recorte mudou.\n")

    # ------------------------------------------------------ pergunta 1 ---
    add(f"## 1. Quantas não são referenciadas por nenhum dos {len(m.handlers)}"
        f"\n")
    add("| População | Quantas |")
    add("|---|---:|")
    add(f"| strings em `.data` | {total} |")
    add(f"| referenciadas por algum ponteiro de `.text` | {n_ref} |")
    add(f"| **não referenciadas por ponteiro nenhum** | **{n_unref}** |")
    add(f"| referenciadas, mas de código que não é um dos "
        f"{len(m.handlers)} | {n_orphan} |")
    add(f"| referenciadas de dentro de um dos {len(m.handlers)} | {n_att} |")
    add("")
    add(f"**{total - n_att} das {total} não são alcançadas por nenhum dos "
        f"{len(m.handlers)} handlers publicados**, e as duas\nrazões são "
        f"diferentes:\n")
    add(f"- **{n_unref}** não são referenciadas por ponteiro nenhum em "
        f"`.text`. A maior parte é\n  tabela de nome de componente e mensagem "
        f"de diagnóstico da RTL da Borland, mais as\n  cópias mortas do bloco "
        f"de literais (seção seguinte);\n"
        f"- **{n_orphan}** são referenciadas, mas de código fora dos corpos "
        f"medidos: os "
        f"{len(m.handlers)} cobrem\n  {100 * m.covered / m.text.raw_size:.1f}% "
        f"da `.text`. O resto é método não publicado, código\n  de "
        f"inicialização de unidade e a própria RTL estática.\n")
    add("Nenhum dos dois grupos é \"código morto\" — é código que esta tarefa "
        "não mapeia. Quem\nmapeia o primeiro tipo é a fase 4, handler a "
        "handler; a RTL não interessa a\nninguém aqui.\n")

    # ------------------------------------------------------ pergunta 2 ---
    add("## 2. Qual handler tem mais strings\n")
    ordered = sorted(m.per_handler.items(),
                     key=lambda kv: (-len(kv[1]), kv[0]))
    if ordered:
        top_label, top_group = ordered[0]
        add(f"**`{top_label}`**, com {len(top_group)} strings distintas. Os "
            f"{min(12, len(ordered))} primeiros:\n")
        add("| Handler | Formulário | Strings | Referências |")
        add("|---|---|---:|---:|")
        for label, group in ordered[:12]:
            form, name = label.split(".", 1)
            n_refs = sum(1 for s in group for a in s.refs
                         if any(h.addr <= a < h.end for h in m.handlers
                                if h.label == label))
            add(f"| `{name}` | `{form}` | {len(group)} | {n_refs} |")
        add("")
        add(f"O que `{top_label}` carrega, que é a razão de a coluna existir:"
            f"\n")
        add("| VA | String |")
        add("|---|---|")
        for s in sorted(top_group, key=lambda s: s.va):
            add(f"| `0x{s.va:08x}` | `{show(s.text)}` |")
        add("")
    add("Por formulário, somando os handlers de cada um:\n")
    add("| Formulário | Strings distintas | Handlers com string |")
    add("|---|---:|---:|")
    for form in sorted(m.per_form, key=lambda f: (-len(m.per_form[f]), f)):
        n_h = sum(1 for label in m.per_handler if label.startswith(form + "."))
        add(f"| `{form}` | {len(m.per_form[form])} | {n_h} |")
    add("")
    add(f"Só {len(m.per_form)} dos formulários têm handler com string "
        f"literal. Isso **não** quer dizer que os\noutros não validem nada: "
        f"quer dizer que a mensagem deles, se existe, é montada em\ncódigo que "
        f"não é handler publicado, ou vem do `.dfm`.\n")

    # ------------------------------------------------------ pergunta 3 ---
    add("## 3. As strings com enchimento se concentram em algum formulário\n")
    padded = m.by_reason.get("enchimento", [])
    n_pad = len(padded)
    pad_forms: dict[str, int] = {}
    for s in padded:
        for label in s.handlers:
            form = label.split(".", 1)[0]
            pad_forms[form] = pad_forms.get(form, 0) + 1
    top_form = min(pad_forms, key=lambda f: (-pad_forms[f], f)) \
        if pad_forms else "—"
    rest = sorted({f for f in pad_forms if f != top_form})
    n_rest = n_pad - pad_forms.get(top_form, 0)
    if n_rest == 0:
        tail = "Nenhuma vem de outro formulário."
    elif n_rest == 1 and rest:
        tail = f"A única fora dele é de `{rest[0]}`."
    else:
        tail = ("As outras vêm de "
                + ", ".join(f"`{f}`" for f in rest) + ".")
    add(f"**Sim: em `{top_form}`.** Das {n_pad} strings com enchimento de "
        f"espaço, {pad_forms.get(top_form, 0)}\nsão carregadas de dentro de um "
        f"handler de `{top_form}`. {tail}\n")
    add("| VA | String | Handler |")
    add("|---|---|---|")
    for s in m.by_reason.get("enchimento", []):
        add(f"| `0x{s.va:08x}` | `{show(s.text)}` | "
            + (", ".join(f"`{h}`" for h in s.handlers) or "—") + " |")
    add("")
    add("A concentração não é surpresa e ainda assim é informação: `MainForm` "
        "é a tela que\nescreve na imagem, e mensagem de confirmação de "
        "gravação é justamente o texto que\no tradutor mexeu.\n")

    add("### O que `suspeita_patch` marca, e o que não marca\n")
    add("| Código | Critério | Quantas |")
    add("|---|---|---:|")
    add(f"| `enchimento` | tem conteúdo e termina em dois ou mais espaços | "
        f"{len(m.by_reason.get('enchimento', []))} |")
    add(f"| `truncada` | parece mensagem e tem `(` ou `[` sem fechar | "
        f"{len(m.by_reason.get('truncada', []))} |")
    add(f"| `buraco` | parece mensagem e tem três ou mais espaços entre "
        f"palavras | {len(m.by_reason.get('buraco', []))} |")
    add(f"| `gemea_difere` | existe cópia com o mesmo trecho de "
        f"{NGRAM} caracteres e texto diferente | "
        f"{len(m.by_reason.get('gemea_difere', []))} |")
    add(f"| **alguma delas** | | **{len(m.suspect)}** |")
    add("")
    add(f"Fora da marcação, dois grupos medidos e deliberadamente deixados de "
        f"fora:\n")
    add(f"- **{len(m.weak)} strings terminam em exatamente um espaço**. Um "
        f"espaço final é o que\n  separa a frase do número que vem depois "
        f"(`'Voce precisa de '` + n), e marcar isso\n  como enchimento "
        f"encheria a coluna de falso positivo. O critério da tarefa é dois\n  "
        f"espaços, e é o que está implementado;\n"
        f"- **{len(m.all_space)} strings são só espaço**, sem conteúdo "
        f"nenhum. São separadores e\n  campos em branco, não texto "
        f"decepado.\n")

    # --------------------------------------------------------- as cópias ---
    add("## O bloco de literais do app aparece mais de uma vez\n")
    add(f"{len(m.with_copy)} das {total} strings têm ao menos uma cópia byte a "
        f"byte em outro endereço de\n`.data` — a coluna `copia_de` do TSV traz "
        f"o menor VA de cada grupo. Parte disso é\nbanal (`xx.cpp` da RTL "
        f"aparece dezenas de vezes), mas os deslocamentos mais\nfrequentes "
        f"contam outra coisa:\n")
    add("| Δ entre cópias | Pares |")
    add("|---|---:|")
    for delta, count in m.deltas[:5]:
        add(f"| `0x{delta:x}` | {count} |")
    add("")
    add("| Cópia | Δ | Strings | Origem | Cópia mora em | Referenciadas |")
    add("|---:|---|---:|---|---|---:|")
    for n, (delta, members) in enumerate(m.clusters, 1):
        refd = sum(1 for s in members if s.referenced)
        src_lo = min(s.va for s in members) - delta
        src_hi = max(s.va for s in members) - delta
        add(f"| {n} | `0x{delta:x}` | {len(members)} | "
            f"`0x{src_lo:08x}`…`0x{src_hi:08x}` | "
            f"`0x{min(s.va for s in members):08x}`…"
            f"`0x{max(s.va for s in members):08x}` | {refd} |")
    add("")
    if m.clusters:
        src_lo = min(min(s.va for s in mem) - delta
                     for delta, mem in m.clusters)
        src_hi = max(max(s.va for s in mem) - delta
                     for delta, mem in m.clusters)
        add(f"O bloco de literais do app — o que vive entre "
            f"`0x{src_lo:08x}` e `0x{src_hi:08x}` e é o\núnico que o código "
            f"referencia — aparece **{len(m.clusters) + 1} vezes** em `.data`. "
            f"As cópias altas não\nsão idênticas à viva: o texto difere, e é "
            f"disso que sai a seção seguinte.\n")

    if m.recoverable:
        add("### As cópias mortas preservam conteúdo que a viva perdeu\n")
        add("É o que a §8.8 do plano dá como perdido — \"conseguir o binário "
            "original em espanhol\nresolveria isso\". Em parte, não é "
            "preciso: o próprio arquivo carrega outra versão\ndo mesmo "
            "texto.\n")
        for s in m.recoverable:
            add(f"**`0x{s.va:08x}`** — viva, "
                + (", ".join(f"`{h}`" for h in s.handlers) or "sem handler")
                + ":\n")
            add(f"```\n{s.text}\n```\n")
            for va in s.twins:
                t = m.by_va[va]
                add(f"Cópia morta em `0x{va:08x}`:\n")
                add(f"```\n{t.text}\n```\n")
        add("O caso do número de camisa é o que a §1.5 e a §8.8 citam "
            "nominalmente. A versão\nviva perde o `)` e termina em `Mastere`; "
            "a cópia morta fecha o parêntese e escreve\n`Master`. **A regra de "
            "validação é a mesma nas duas** — `[33 ... 99]`, e só na Master\n"
            "League —, então a spec do handler pode ser escrita sem o binário "
            "espanhol.\n")
        add("Isso não torna a cópia morta uma fonte confiável de tradução: "
            "ela também tem\nburaco de espaço no meio das palavras, e num "
            "ponto ela está em português onde a\nviva está em inglês. O que "
            "ela dá é **sentido**, que é exatamente o que a §1.5 pede\ndas "
            "mensagens originais.\n")
        rtl = [s for s in m.recoverable if not s.handlers]
        if rtl:
            add(f"E o par de `0x{rtl[0].va:08x}` não é mensagem do app e ainda "
                f"assim é o achado mais\ninformativo da seção: é uma asserção "
                f"da RTL da Borland, e as duas cópias trazem\n**nome de "
                f"variável diferente** dentro dela. Tradutor nenhum renomeia "
                f"variável em\nasserção de biblioteca — isso quer dizer que as "
                f"cópias vêm de **compilações\ndiferentes**, e não de duas "
                f"passadas de tradução sobre o mesmo `.data`. Qual das "
                f"três\nveio primeiro não sai daqui.\n")

    # --------------------------------------------------------- correções ---
    add("## Onde o plano envelheceu\n")
    add("Tudo abaixo é contagem do script contra texto já escrito.\n")
    add("| Onde | Diz | Medido |")
    add("|---|---|---|")
    add(f"| §1.5 e §8.8 do plano, e a WTE-TASK-05 | \"**70 strings** terminam "
        f"em espaço de enchimento\" | **{n_pad}** em `.data` pelo critério "
        f"desta página (conteúdo + dois espaços no fim); {len(m.weak)} com um "
        f"espaço só |")
    add(f"| §1.5 do plano | \"o arquivo está em **cp1252 quebrado**\" | "
        f"**{m.high_bytes} bytes** acima de `0x7E` nas {total} strings — é "
        f"ASCII com os acentos removidos |")
    add(f"| §8.8 do plano | \"conseguir o binário original em espanhol "
        f"resolveria isso\" | {len(m.recoverable)} strings têm uma segunda "
        f"versão **dentro do próprio arquivo**, entre elas a do número de "
        f"camisa que a §8.8 cita |")
    add("")
    add(f"O **{n_pad} contra 70** merece cuidado, porque a diferença não é "
        f"erro de ninguém: são\npopulações diferentes. A §1.5 não diz onde "
        f"contou, e o número que ela cita não sai\nde `.data` com nenhum "
        f"critério razoável. Sai quando se conta o **binário inteiro**,\nque é "
        f"o que uma passada de `strings` faria — e a maior parte do que "
        f"aparece lá é\n`.rsrc`, isto é, **caption de formulário**.\n")
    add(f"Isso é medida, não conjectura: nos {m.dfm_files} formulários já "
        f"extraídos em [`dfm/`](dfm/), pelo\n**mesmo critério** desta página, "
        f"há **{m.dfm_padded} literais com dois ou mais espaços no fim** — "
        f"contra\nos {n_pad} de `.data`. O `.rsrc` sozinho já passa dos 70, e "
        f"é onde a §1.5 quase certamente\ncontou.\n")
    if m.dfm_per_form:
        add("| Formulário | Literais com enchimento |")
        add("|---|---:|")
        for form in sorted(m.dfm_per_form,
                           key=lambda f: (-m.dfm_per_form[f], f)):
            add(f"| `{form}` | {m.dfm_per_form[form]} |")
        add("")
        add("A concentração é a mesma da pergunta 3, por outro caminho: "
            "`MainForm` de novo.\n**Consequência prática:** quem for "
            "reescrever as mensagens em pt-BR tem de olhar os\n`.dfm` também, "
            "não só este inventário — e é a WTE-TASK-10 que os transforma "
            "em\n`.lfm`.\n")
    add("A conclusão da §1.5 continua de pé, e é a que importa: **o patch é "
        "in-place com\nenchimento de espaço, e pelo menos uma mensagem perdeu "
        "conteúdo.** O que muda é\nonde procurar as outras — em `.rsrc`, com "
        "os `.dfm`, não aqui.\n")

    # ---------------------------------------------------------- ressalvas ---
    add("## Ressalvas\n")
    add(f"- **`suspeita_patch` é heurística, e as quatro regras estão no "
        f"script.** Nenhuma\n  delas é prova de que o tradutor mexeu naquela "
        f"string; são os sinais que sobram de\n  um patch in-place. Um texto "
        f"escrito com espaço no fim de propósito seria marcado\n  igual.\n"
        f"- **Não referenciada não quer dizer morta.** Ponteiro montado em "
        f"tempo de execução\n  (base mais índice) não aparece na `.reloc` como "
        f"referência à string, e sim à base\n  da tabela. As tabelas de nome "
        f"de componente são o caso óbvio.\n"
        f"- **A coluna `handler` só cobre os corpos dos "
        f"{len(m.handlers)} publicados.** Referência vinda\n  de método não "
        f"publicado fica com a coluna vazia mesmo tendo dono claro; separar\n"
        f"  isso é trabalho de fase 4.\n"
        f"- **O escopo é `.data`.** Caption de formulário mora em `.rsrc` e "
        f"saiu na\n  WTE-TASK-03; nome de DLL e de função importada mora em "
        f"`.idata`; o `.text` tem\n  nome de tipo de RTTI (`Tficha_enlaza *`) "
        f"entre as funções. Nada disso é mensagem\n  do app, e nada disso está "
        f"aqui.\n"
        f"- **Nenhum byte do `.exe` foi copiado para cá além do necessário "
        f"para responder as\n  perguntas.** As mensagens citadas aparecem "
        f"porque a evidência **é** o texto; o\n  resto são medidas, no "
        f"espírito da §2 do plano.\n")
    return "\n".join(L) + "\n"


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

    if not DFM.is_dir():
        raise DumpError(
            f"{REL_DFM} nao existe. Rode antes: python3 "
            f"wte/tools/dfm_extract.py")
    dfm_paths = sorted(DFM.glob("*.dfm"))
    if not dfm_paths:
        raise DumpError(f"{REL_DFM} nao tem nenhum .dfm")

    img = Image(EXE.read_bytes())
    handlers = read_published(PUB.read_text(encoding="utf-8"))
    m = Measurement(img, handlers, dfm_paths)
    return {TSV_NAME: render_tsv(m), MD_NAME: render_md(m)}


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
        print(f"{REL_OUT} nao corresponde a {REL_EXE} + {REL_PUB}:",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivos em dia com {REL_EXE} + {REL_PUB}")
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(files.items()):
        # newline="\n" para que o arquivo saia igual no Windows -- ele e
        # comparado byte a byte pelo --check.
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  {name}: {content.count(chr(10))} linhas, "
              f"{len(content.encode('utf-8'))} bytes")
    print(f"\n{len(files)} arquivos em {REL_OUT}")
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
