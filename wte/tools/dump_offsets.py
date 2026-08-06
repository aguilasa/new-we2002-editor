#!/usr/bin/env python3
"""Cruza a tabela de offsets do we-team-editor.exe com Offsets.hpp.

WTE-TASK-06.

O editor do Obocaman guarda offsets absolutos da imagem de CD em `.data` e como
imediato de instrucao em `.text`. Este script le o `.exe` e o `Offsets.hpp`
deste repositorio e escreve tres respostas em `wte/re/`:

  1. onde a tabela de `.data` comeca e termina, medido, nao estimado;
  2. quais dos `OFS_*` aparecem literalmente e como os demais se classificam;
  3. que dwords plausiveis o Obocaman tem e este repositorio ainda nao nomeou.

    python3 wte/tools/dump_offsets.py            # gera
    python3 wte/tools/dump_offsets.py --check    # regera em memoria e compara

Leitura pura: nem o `.exe` nem o `.hpp` sao abertos para escrita.


Os valores vem do header, nunca do script
-----------------------------------------

`Offsets.hpp` e gerado por `tools/extract_legacy_data.py` a partir do legado
MFC. Copiar os 69 numeros para dentro deste script criaria uma segunda fonte de
verdade que envelhece calada. O header e parseado a cada execucao, e os limites
do filtro de plausibilidade (`LO`, `HI`) saem dele -- se um offset novo entrar
no header, a faixa acompanha sozinha.


O filtro de plausibilidade, e por que nao e o que a tarefa sugeriu
-----------------------------------------------------------------

O markdown da WTE-TASK-06 sugere "entre 1.000.000 e 8.000.000, alinhado,
referenciado por codigo". Medido contra o proprio `Offsets.hpp`, esse criterio
descarta **13 dos 69** offsets conhecidos (os oito `OFS_PLAYER_NAME_*` mais
`OFS_SQUAD_NUMBERS_NATIONAL` ficam abaixo de 1.000.000; os quatro
`OFS_FLAG_COLOURS*` ficam acima de 8.000.000) e "alinhado" derruba outros
quatro, cujo valor nao e multiplo de 4. Um filtro que rejeita 13 verdadeiros
positivos conhecidos nao serve para achar os desconhecidos.

O que este script usa no lugar, tudo derivado de medida:

- **faixa**: `[min, max]` dos valores do proprio header;
- **geometria do setor**: `24 <= v % 2352 < 2072`, isto e, o offset cai dentro
  da regiao de dados de usuario de um setor MODE2/2352. Os 69 passam -- o
  script **aborta** se algum deixar de passar, porque nesse dia o filtro
  passou a estar errado;
- **nao e texto**: os quatro bytes nao formam ASCII imprimivel nem par UTF-16
  de imprimiveis. Um terceiro caso -- "prefixo imprimivel seguido de NUL" --
  foi testado e **descartado**, porque derruba cinco offsets conhecidos; ver o
  comentario de `is_texty`;
- **nao e alvo de realocacao base**. Este e o corte que faz o trabalho. Um
  dword que a `.reloc` manda o carregador ajustar e, por definicao, um
  endereco -- ponteiro ou VA de codigo --, nunca uma constante de offset. Sem
  ele a varredura de `.text` devolve mais de 1.500 candidatos, quase todos VAs
  do proprio modulo.

A alternativa obvia ao corte por realocacao seria descartar valor dentro da
janela `[ImageBase, ImageBase+SizeOfImage)`. Ela **nao serve**: cinco dos 69
offsets conhecidos caem nessa janela por coincidencia numerica
(`OFS_TEAM_ABBREV_3` = 4234484 = 0x409CF4 e um deles). A `.reloc` distingue os
dois casos sem heuristica.


Duas rotas, porque as evidencias sao de natureza diferente
----------------------------------------------------------

- **rota `.data`**: corrida de dwords 4-alinhados consecutivos, cada um
  plausivel ou zero, comecando num endereco referenciado por `.text`. E como
  vive a maioria dos confirmados.
- **rota `.text`**: imediato de 32 bits em codificacao x86 de carga de
  constante (`push imm32`, `mov r32,imm32`, `add eax,imm32`, grupo `81 /r`,
  `lea` com `disp32`, ...). E como vivem os outros tres.

A rota `.text` e uma varredura de padrao de byte, **nao um desmontador**: ela
casa em posicoes que um decodificador linear nunca visitaria, no meio de outra
instrucao. Isso produz falso positivo, e o `offsets.md` diz quantos e da um
exemplo nomeado. A escolha e deliberada -- embutir um desmontador x86 aqui
custaria mais do que vale, e a saida ordenada por numero de ocorrencias ja
separa o que interessa. Nada aqui e conclusao: e lista de alvos para a
WTE-TASK-19.


Falha alta
----------

`.exe` ausente, secao de PE que falta, `Offsets.hpp` que nao parseia, offset
duplicado no header, offset conhecido que nao passa no filtro de
plausibilidade, ou tabela cujos dois criterios de limite discordam -- todos
abortam com contexto. Nenhuma saida parcial vai para o disco: os dois arquivos
so sao escritos depois que tudo foi medido.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
HPP = ROOT / "src" / "core" / "include" / "we2002" / "Offsets.hpp"
OUT = ROOT / "wte" / "re"

# Caminhos relativos nas mensagens e na saida -- nada de caminho absoluto, que
# quebraria a estabilidade byte a byte entre maquinas.
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_HPP = "src/core/include/we2002/Offsets.hpp"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_offsets.py"

TSV_NAME = "offsets.tsv"
MD_NAME = "offsets.md"

# Geometria do setor MODE2/2352, a mesma que o Offsets.hpp deste repositorio
# declara.
SECTOR_SIZE = 2352
SECTOR_DATA_BEGIN = 24
SECTOR_DATA_END = 2072

# Limite de deslocamento aceito ao classificar um offset ausente como derivado
# de uma base: ou o mesmo setor, ou um numero pequeno de setores inteiros. O
# teto existe para que "e multiplo de 2352" nao vire relacao vazia -- entre dois
# offsets quaisquer da imagem quase sempre da para achar um k.
MAX_SECTOR_STEPS = 32


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do dfm_extract.py: o que este
# script precisa do formato cabe em poucas dezenas de linhas, e sem dependencia
# o `make -C wte check` roda em qualquer maquina com Python 3.


def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


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
    """O `.exe` lido: secoes, base, e o conjunto de alvos de realocacao."""

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
        reloc_rva, reloc_size = struct.unpack_from(
            "<II", data, opt + 96 + 5 * 8)
        self.relocs = self._read_relocs(reloc_rva, reloc_size)
        if not self.relocs:
            raise DumpError(
                f"{REL_EXE}: nenhuma realocacao HIGHLOW. O corte por "
                f"realocacao e o que separa offset de ponteiro; sem ele a "
                f"medicao nao vale.")

    # -- conversoes -------------------------------------------------------

    def section(self, name: str) -> Section | None:
        for s in self.sections:
            if s.name == name:
                return s
        return None

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


# ---------------------------------------------------------------- header ---


def read_offsets_hpp(text: str) -> list[tuple[str, int]]:
    """Os `OFS_*` do header, na ordem de declaracao."""
    pairs = re.findall(
        r"^inline constexpr Offset\s+(OFS_\w+)\s*=\s*(\d+);", text, re.M)
    if not pairs:
        raise DumpError(
            f"{REL_HPP}: nenhuma constante OFS_* reconhecida.\n"
            f"       O padrao esperado e "
            f"'inline constexpr Offset OFS_NOME = 123;' no inicio da linha. "
            f"Se o gerador do header mudou a forma, este script tem de "
            f"acompanhar -- ele nao guarda copia dos valores.")
    seen: dict[str, int] = {}
    for name, value in pairs:
        if name in seen:
            raise DumpError(f"{REL_HPP}: {name} declarado duas vezes")
        seen[name] = int(value)
    return [(n, int(v)) for n, v in pairs]


# ------------------------------------------------------------- filtragem ---


def is_texty(value: int) -> bool:
    """Os quatro bytes parecem texto em vez de numero?

    Duas formas, ambas observadas na `.data` deste binario: ASCII imprimivel
    puro, e par UTF-16LE de imprimiveis (a `(null)` larga da RTL da Borland).

    A regra parou aqui de proposito. Um terceiro caso tentador -- "prefixo
    imprimivel seguido de NUL", que e a forma do `xyz\\0` que fecha a tabela de
    alfabeto vizinha aos offsets -- foi **testado e descartado**: como todo
    valor da faixa cabe em tres bytes, esse caso degenera em "os tres bytes
    baixos sao imprimiveis", e ele derruba cinco offsets conhecidos
    (`OFS_TEAM_NAME_4` = 2830160 = `0x002B2F50` e `P`, `/`, `+`, NUL). Quem
    mantem o `xyz\\0` fora da tabela e o recorte pelo endereco-base
    referenciado por codigo, que e criterio de posicao e nao de valor.
    """
    b = value.to_bytes(4, "little")

    def printable(c: int) -> bool:
        return 0x20 <= c <= 0x7E

    if all(printable(c) for c in b):
        return True
    if b[1] == 0 and b[3] == 0 and printable(b[0]) and printable(b[2]):
        return True
    if b[0] == 0 and b[2] == 0 and printable(b[1]) and printable(b[3]):
        return True
    return False


class Plausible:
    """O filtro P(v), com os limites tirados do proprio Offsets.hpp."""

    def __init__(self, values: list[int]):
        self.lo = min(values)
        self.hi = max(values)

    def __call__(self, value: int) -> bool:
        if not self.lo <= value <= self.hi:
            return False
        rem = value % SECTOR_SIZE
        if not SECTOR_DATA_BEGIN <= rem < SECTOR_DATA_END:
            return False
        return not is_texty(value)


# ------------------------------------------------------------ varreduras ---


def scan_literals(img: Image, wanted: set[int]) -> dict[int, list[int]]:
    """Onde cada valor de `wanted` aparece como dword, em qualquer alinhamento.

    Desalinhado de proposito: imediato de instrucao x86 quase nunca cai em
    multiplo de 4, e tres dos offsets confirmados so existem assim. Uma
    varredura alinhada acha 17 dos 19.
    """
    data = img.data
    found: dict[int, list[int]] = {}
    for pos in range(len(data) - 3):
        value = _u32(data, pos)
        if value in wanted:
            found.setdefault(value, []).append(pos)
    return found


# Opcodes com imediato de 32 bits imediatamente apos o byte de opcode.
_IMM32_AFTER_OPCODE = frozenset(
    [0x68,                                            # push imm32
     0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D,  # alu eax, imm32
     0xA9]                                            # test eax, imm32
)
# Opcodes com ModRM antes do imediato ou do deslocamento.
_MODRM_FORMS = frozenset([0x81, 0xC7, 0x69, 0x8D, 0xF7])


def scan_text_immediates(img: Image, plausible: Plausible
                         ) -> dict[int, list[tuple[int, str]]]:
    """Imediatos de 32 bits em `.text` que passam no filtro.

    Varredura de padrao, nao desmontagem -- ver o cabecalho do modulo.
    Devolve valor -> [(offset de arquivo do imediato, forma)].
    """
    sec = img.section(".text")
    assert sec is not None
    data = img.data
    begin, end = sec.raw_ptr, sec.raw_ptr + sec.raw_size
    hits: dict[int, list[tuple[int, str]]] = {}

    def take(imm_at: int, form: str) -> None:
        if imm_at + 4 > end or imm_at in img.relocs:
            return
        value = _u32(data, imm_at)
        if plausible(value):
            hits.setdefault(value, []).append((imm_at, form))

    for pos in range(begin, end - 5):
        op = data[pos]
        if op in _IMM32_AFTER_OPCODE:
            take(pos + 1, "imm32")
        elif 0xB8 <= op <= 0xBF:  # mov r32, imm32
            take(pos + 1, "mov")
        elif op in _MODRM_FORMS:
            modrm = data[pos + 1]
            mod, rm = modrm >> 6, modrm & 7
            length = 2
            if mod != 3 and rm == 4:
                length += 1  # SIB
            if mod == 1:
                length += 1
            elif mod == 2:
                length += 4
            elif mod == 0 and rm == 5:
                length += 4
            if op == 0x8D:  # lea: o que interessa e o disp32, nao o imediato
                if mod == 2 or (mod == 0 and rm == 5):
                    disp = pos + 2 + (1 if (mod != 3 and rm == 4) else 0)
                    take(disp, "lea")
            elif op == 0xF7 and (modrm >> 3 & 7) != 0:
                pass  # so o /0 (test) carrega imediato
            else:
                take(pos + length, "imm32")
    return hits


class Run:
    """Uma corrida de dwords 4-alinhados em `.data`: candidata a tabela."""

    __slots__ = ("va", "end_va", "slots", "referenced", "known")

    def __init__(self, va: int, end_va: int, slots: list[int],
                 referenced: int):
        self.va = va
        self.end_va = end_va
        self.slots = slots          # todos os dwords, zeros inclusive
        self.referenced = referenced
        self.known: list[str] = []

    @property
    def filled(self) -> list[int]:
        return [v for v in self.slots if v != 0]

    @property
    def size(self) -> int:
        return self.end_va - self.va


def scan_data_runs(img: Image, plausible: Plausible) -> list[Run]:
    """Corridas de `.data`, com a contagem de referencias vindas de `.text`.

    Regra de limite, e ela e a resposta da pergunta 1:

    - **inicio**: o primeiro endereco da corrida que o `.text` referencia. Nao
      o primeiro dword plausivel -- o `xyz\\0` que fecha a tabela de alfabeto
      logo abaixo da tabela 1 e numericamente plausivel, e so o recorte pela
      referencia o mantem fora. Corrida sem referencia nenhuma fica com o
      inicio onde o conteudo manda, e nao vira tabela.
    - **fim**: o primeiro dword que **nao** e plausivel nem zero. Zero nao
      encerra -- e buraco, e o codigo que percorre a tabela pula zero em vez de
      parar nele.
    """
    sec = img.section(".data")
    assert sec is not None
    data = img.data
    refs = data_references(img)
    count = sec.raw_size // 4
    words = [_u32(data, sec.raw_ptr + 4 * i) for i in range(count)]

    def ok(i: int) -> bool:
        return plausible(words[i]) and (sec.raw_ptr + 4 * i) not in img.relocs

    runs: list[Run] = []
    i = 0
    while i < count:
        if not ok(i):
            i += 1
            continue
        j = i
        last = i
        while j < count and (ok(j) or words[j] == 0):
            if ok(j):
                last = j
            j += 1
        va = img.image_base + sec.rva + 4 * i
        end_va = img.image_base + sec.rva + 4 * j
        # Recorte pelo inicio referenciado por codigo, quando existe.
        inside = [a for a in refs if va <= a < end_va and (a - va) % 4 == 0]
        start = min(inside) if inside else va
        first = i + (start - va) // 4
        runs.append(Run(start, end_va, words[first:j], refs.get(start, 0)))
        i = j
    return runs


def data_references(img: Image) -> dict[int, int]:
    """Enderecos de `.data` que aparecem como dword absoluto dentro de `.text`.

    Contagem por endereco. Alinhamento livre: o endereco entra no codigo como
    imediato, e imediato nao respeita alinhamento.
    """
    text = img.section(".text")
    data = img.section(".data")
    assert text is not None and data is not None
    lo = img.image_base + data.rva
    hi = lo + data.raw_size
    out: dict[int, int] = {}
    buf = img.data
    for pos in range(text.raw_ptr, text.raw_ptr + text.raw_size - 3):
        value = _u32(buf, pos)
        if lo <= value < hi:
            out[value] = out.get(value, 0) + 1
    return out


# ---------------------------------------------------------- classificacao ---


class Missing:
    __slots__ = ("name", "value", "cls", "base", "base_name", "relation",
                 "delta", "depth")

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
        self.cls = "H3"
        self.base: int | None = None
        self.base_name = ""
        self.relation = ""
        self.delta = 0
        self.depth = 0


def relation(value: int, base: int) -> tuple[str, int] | None:
    """Como `value` se deriva de `base`, se e que se deriva.

    Duas formas, e so duas: cair no mesmo setor (deslocamento menor que um
    setor, que e como o original trata `_A`/`_B`/`_END`) ou estar a um numero
    inteiro e pequeno de setores.
    """
    delta = value - base
    if delta == 0:
        return None
    if abs(delta) < SECTOR_SIZE:
        return "mesmo setor", delta
    if delta % SECTOR_SIZE == 0:
        steps = delta // SECTOR_SIZE
        if abs(steps) <= MAX_SECTOR_STEPS:
            unit = "setor" if abs(steps) == 1 else "setores"
            return f"{steps:+d} {unit}", delta
    return None


def classify_missing(missing_pairs: list[tuple[str, int]],
                     confirmed: set[int],
                     candidates: set[int],
                     names: dict[int, str]) -> list[Missing]:
    """Busca em largura a partir das bases que o Obocaman comprovadamente tem.

    Raizes de profundidade 0: os offsets confirmados (classe H1) e os
    candidatos da varredura (classe H2). A cada camada, um offset ausente se
    liga a uma raiz ou a um ausente ja ligado -- e assim as familias com passo
    de setor (`OFS_PLAYER_ATTR_1..9`, `OFS_PLAYER_NAME_2..8`) entram inteiras
    a partir de um unico ancora.

    Determinismo: as camadas sao processadas em ordem, e dentro de uma camada o
    desempate e (classe, profundidade da base, |delta|, base) -- ordem total.
    """
    items = [Missing(n, v) for n, v in missing_pairs]
    pool: dict[int, tuple[str, int]] = {}
    for value in sorted(confirmed):
        pool[value] = ("H1", 0)
    for value in sorted(candidates):
        pool.setdefault(value, ("H2", 0))

    pending = list(items)
    depth = 0
    while pending:
        depth += 1
        frontier: list[Missing] = []
        for item in pending:
            best = None
            for base in sorted(pool):
                base_cls, base_depth = pool[base]
                rel = relation(item.value, base)
                if rel is None:
                    continue
                key = (0 if base_cls == "H1" else 1, base_depth,
                       abs(rel[1]), base)
                if best is None or key < best[0]:
                    best = (key, base, base_cls, rel)
            if best is not None:
                _, base, base_cls, rel = best
                item.cls = base_cls
                item.base = base
                item.base_name = names.get(base, "")
                item.relation, item.delta = rel
                item.depth = depth
                frontier.append(item)
        if not frontier:
            break
        for item in frontier:
            pool[item.value] = (item.cls, item.depth)
        pending = [i for i in pending if i not in frontier]

    for item in items:
        if item.base is None and confirmed:
            near = min(sorted(confirmed),
                       key=lambda b: (abs(item.value - b), b))
            item.base = near
            item.base_name = names.get(near, "")
            item.delta = item.value - near
            item.relation = "-"
    return items


# ---------------------------------------------------------------- medida ---


class Measurement:
    """Tudo o que foi medido, antes de virar texto."""

    def __init__(self, img: Image, declared: list[tuple[str, int]]):
        self.img = img
        self.declared = declared
        self.names = {v: n for n, v in declared}
        values = [v for _, v in declared]
        self.plausible = Plausible(values)

        bad = [n for n, v in declared if not self.plausible(v)]
        if bad:
            raise DumpError(
                f"{REL_HPP}: {len(bad)} offset(s) nao passam no filtro de "
                f"plausibilidade deste script: {', '.join(sorted(bad)[:6])}.\n"
                f"       O filtro so vale enquanto aceita 100% do que ja se "
                f"sabe ser offset. Corrija o filtro antes de confiar em "
                f"qualquer candidato.")

        self.literals = scan_literals(img, set(values))
        self.confirmed = {v for v in values if v in self.literals}
        self.missing_pairs = [(n, v) for n, v in declared
                              if v not in self.confirmed]

        self.data_refs = data_references(img)
        self.runs = scan_data_runs(img, self.plausible)
        for run in self.runs:
            run.known = [self.names[v] for v in run.filled if v in self.names]

        # Tabelas: corrida com base referenciada por codigo e com pelo menos um
        # offset conhecido dentro. Sao as que a pergunta 1 pede para delimitar.
        self.tables = [r for r in self.runs if r.referenced and r.known]
        self.copies = self.find_copies()

        self.text_hits = scan_text_immediates(img, self.plausible)
        self.text_candidates = {v: h for v, h in self.text_hits.items()
                                if v not in self.names}
        # So as tabelas canonicas: as copias sao byte a byte iguais e nao
        # acrescentam valor nenhum, e as corridas que nao sao tabela nao tem a
        # evidencia de co-residencia que da peso a esta rota.
        self.data_candidates: dict[int, list[int]] = {}
        for table in self.tables:
            for k, value in enumerate(table.slots):
                if value and value not in self.names:
                    self.data_candidates.setdefault(value, []).append(
                        table.va + 4 * k)

        self.missing = classify_missing(
            self.missing_pairs, self.confirmed,
            set(self.text_candidates) | set(self.data_candidates), self.names)

        self.check_table_bounds()

    # -- pergunta 1 -------------------------------------------------------

    def find_copies(self) -> list[tuple[Run, int]]:
        """Onde mais no arquivo a sequencia de bytes de cada tabela aparece.

        Busca pela sequencia crua, nao por igualdade de lista de slots: as
        copias comecam alguns bytes antes (a tabela de alfabeto vizinha tambem
        foi duplicada) e o recorte pelo endereco referenciado nao se aplica a
        elas, ja que nenhuma copia e referenciada por codigo.
        """
        out: list[tuple[Run, int]] = []
        data = self.img.data
        for table in self.tables:
            start = self.img.va_to_offset(table.va)
            if start is None:
                continue
            needle = data[start:start + table.size]
            pos = data.find(needle)
            while pos != -1:
                if pos != start:
                    va = self.img.offset_to_va(pos)
                    if va is not None:
                        out.append((table, va))
                pos = data.find(needle, pos + 1)
        return out

    def check_table_bounds(self) -> None:
        """Confronta os dois criterios de limite superior. Assimetrico.

        Criterio A: a corrida acaba no primeiro dword que nao e plausivel nem
        zero. Criterio B: a tabela vai ate o proximo endereco de `.data` que o
        codigo referencia. Sao independentes -- um olha o conteudo, o outro
        olha quem aponta para la.

        **Os dois sentidos da discordancia nao sao equivalentes, e o
        tratamento tambem nao e:**

        - `B < A` -- o conteudo diz que a tabela vai mais longe do que o codigo
          sustenta. E a armadilha 8.7 em pessoa: emitir numero assim seria
          publicar slot que ninguem referencia como se fosse offset. **Aborta.**
        - `B > A` -- o codigo referencia algo depois do fim medido pelo
          conteudo. O intervalo publicado continua sendo o que o conteudo
          sustenta, entao nao ha numero errado a emitir; o que ha e um vizinho
          que talvez pertenca a tabela. **Avisa**, na saida padrao e no
          markdown.

        Prometer as duas direcoes seria pior do que abortar so numa: quem le
        supoe que `agrees=False` nao passa, e passa.
        """
        self.bounds: list[tuple[Run, int | None, bool]] = []
        for table in self.tables:
            after = [a for a in sorted(self.data_refs) if a > table.va]
            nxt = after[0] if after else None
            agrees = nxt == table.end_va
            self.bounds.append((table, nxt, agrees))
            if nxt is not None and not agrees and nxt < table.end_va:
                raise DumpError(
                    f"{REL_EXE}: a tabela em {table.va:#x} vai ate "
                    f"{table.end_va:#x} pelo conteudo, mas o codigo referencia "
                    f"{nxt:#x} antes disso. Os dois criterios de limite "
                    f"discordam e a tabela nao esta medida -- ver a armadilha "
                    f"8.7 do plano.")
            if nxt is not None and not agrees and nxt > table.end_va:
                print(
                    f"AVISO: a tabela em {table.va:#x} termina em "
                    f"{table.end_va:#x} pelo conteudo, mas a proxima "
                    f"referencia de codigo e {nxt:#x}, "
                    f"{nxt - table.end_va} bytes adiante. O intervalo "
                    f"publicado e o do conteudo; o vizinho pode pertencer a "
                    f"tabela.")


# ------------------------------------------------------------------- TSV ---

TSV_COLUMNS = [
    "registro", "nome", "valor", "hex", "setor", "byte_no_setor", "va",
    "ocorrencias", "classe", "base", "base_nome", "relacao", "delta", "nota",
]


def tsv_row(**kw: object) -> str:
    cells = []
    for col in TSV_COLUMNS:
        value = kw.get(col, "")
        cells.append("" if value is None else str(value))
    return "\t".join(cells)


def sector_of(value: int) -> tuple[int, int]:
    return value // SECTOR_SIZE, value % SECTOR_SIZE


def render_tsv(m: Measurement) -> str:
    lines = ["\t".join(TSV_COLUMNS)]

    for index, table in enumerate(m.tables):
        for slot, value in enumerate(table.slots):
            sec, rem = sector_of(value) if value else ("", "")
            lines.append(tsv_row(
                registro="tabela_slot",
                nome=m.names.get(value, ""),
                valor=value,
                hex=f"0x{value:08x}",
                setor=sec, byte_no_setor=rem,
                va=f"0x{table.va + 4 * slot:08x}",
                nota=f"tabela{index + 1} slot {slot}"
                     + ("" if value else " (buraco)")))

    for table, copy_va in m.copies:
        lines.append(tsv_row(
            registro="tabela_copia",
            va=f"0x{copy_va:08x}",
            nota=f"copia identica de 0x{table.va:08x}, {table.size} bytes"))

    for name, value in m.declared:
        if value not in m.confirmed:
            continue
        places = m.literals[value]
        sections = sorted({
            (m.img.section_of_offset(p).name
             if m.img.section_of_offset(p) else "?") for p in places})
        sec, rem = sector_of(value)
        lines.append(tsv_row(
            registro="confirmado", nome=name, valor=value,
            hex=f"0x{value:08x}", setor=sec, byte_no_setor=rem,
            va="|".join(f"0x{m.img.offset_to_va(p):08x}" for p in places
                        if m.img.offset_to_va(p) is not None),
            ocorrencias=len(places), classe="confirmado",
            nota=",".join(sections)))

    for item in m.missing:
        sec, rem = sector_of(item.value)
        lines.append(tsv_row(
            registro="ausente", nome=item.name, valor=item.value,
            hex=f"0x{item.value:08x}", setor=sec, byte_no_setor=rem,
            classe=item.cls, base=item.base, base_nome=item.base_name,
            relacao=item.relation, delta=item.delta,
            nota=f"profundidade {item.depth}" if item.depth else
                 "sem base derivavel"))

    for value in sorted(m.text_candidates,
                        key=lambda v: (-len(m.text_candidates[v]), v)):
        places = m.text_candidates[value]
        sec, rem = sector_of(value)
        forms = sorted({form for _, form in places})
        lines.append(tsv_row(
            registro="candidato", valor=value, hex=f"0x{value:08x}",
            setor=sec, byte_no_setor=rem,
            va="|".join(f"0x{m.img.offset_to_va(p):08x}" for p, _ in places[:8]
                        if m.img.offset_to_va(p) is not None),
            ocorrencias=len(places), classe="rota .text",
            nota=",".join(forms)))

    for value in sorted(m.data_candidates):
        places = m.data_candidates[value]
        sec, rem = sector_of(value)
        lines.append(tsv_row(
            registro="candidato", valor=value, hex=f"0x{value:08x}",
            setor=sec, byte_no_setor=rem,
            va="|".join(f"0x{a:08x}" for a in places),
            ocorrencias=len(places), classe="rota .data",
            nota="co-residente com offset conhecido"))

    return "\n".join(lines) + "\n"


# -------------------------------------------------------------- markdown ---


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def ascii_view(value: int) -> str:
    """Os quatro bytes do dword como texto, com `.` no que nao e imprimivel."""
    return "".join(chr(c) if 0x20 <= c <= 0x7E else "."
                   for c in value.to_bytes(4, "little"))


def render_md(m: Measurement) -> str:
    img = m.img
    L: list[str] = []
    add = L.append

    n_declared = len(m.declared)
    n_conf = len(m.confirmed)
    n_missing = len(m.missing)
    h1 = [i for i in m.missing if i.cls == "H1"]
    h2 = [i for i in m.missing if i.cls == "H2"]
    h3 = [i for i in m.missing if i.cls == "H3"]

    add("# `re/offsets.md` — a tabela de offsets do `we-team-editor.exe`\n")
    add("Produto da [WTE-TASK-06](../../docs/tasks/06-mapa-de-offsets.md). "
        "Gerado por\n[`../tools/dump_offsets.py`](../tools/dump_offsets.py), a "
        "partir de\n"
        f"`{REL_EXE}` e de\n[`Offsets.hpp`](../../{REL_HPP}).\n"
        "**Não editar à mão** — correção entra no script e o arquivo é "
        "regerado:\n")
    add("```sh\npython3 wte/tools/dump_offsets.py\n"
        "python3 wte/tools/dump_offsets.py --check   # o que `make -C wte "
        "check` roda\n```\n")
    add(f"Os dados em forma de tabela estão em "
        f"[`{TSV_NAME}`]({TSV_NAME}); este arquivo é a\nleitura deles. **Todo "
        f"número daqui saiu do script**, inclusive os do texto corrido —\né "
        f"por isso que o `--check` compara o markdown inteiro byte a byte, e "
        f"não só o\nTSV.\n")

    # ---------------------------------------------------------- método ---
    add("## O que foi medido, e com que régua\n")
    add(f"O `.exe` tem {len(img.data)} bytes, é PE32 i386, `ImageBase` "
        f"`0x{img.image_base:x}`,\n`SizeOfImage` `0x{img.size_of_image:x}`, "
        f"{len(img.sections)} seções. A `.reloc` traz\n{len(img.relocs)} "
        f"realocações `HIGHLOW`.\n")
    add(f"Um dword do binário é tratado como **offset plausível** quando passa "
        f"em quatro\ncortes, todos derivados de medida e nenhum escolhido a "
        f"olho:\n")
    add(f"1. **faixa** — entre {m.plausible.lo} e {m.plausible.hi}, que são o "
        f"menor e o maior\n   valor declarados no `Offsets.hpp`;\n"
        f"2. **geometria do setor** — `{SECTOR_DATA_BEGIN} <= v % "
        f"{SECTOR_SIZE} < {SECTOR_DATA_END}`, isto é, o offset cai\n   dentro "
        f"da região de dados de usuário de um setor MODE2/2352. Os "
        f"{n_declared}\n   offsets conhecidos passam, e o script aborta no dia "
        f"em que um deixar de\n   passar;\n"
        f"3. **não é texto** — os quatro bytes não formam ASCII imprimível "
        f"nem par UTF-16\n   de imprimíveis;\n"
        f"4. **não é alvo de realocação base** — um dword que a `.reloc` manda "
        f"o carregador\n   ajustar é um endereço, não uma constante.\n")
    add("O corte 4 é o que faz o trabalho. Sem ele, a varredura de `.text` "
        "devolve mais\nde mil e quinhentos candidatos, quase todos VAs do "
        "próprio módulo.\n")
    add(f"**O corte 1 sai do nosso próprio `Offsets.hpp`, e isso tem "
        f"consequência.** A faixa\né literalmente o `[min, max]` dos "
        f"{n_declared} valores declarados lá, então a guarda\nque confere "
        f"\"o filtro aceita 100% do que já se sabe ser offset\" é "
        f"**tautológica na\nparte de faixa** — ela morde de verdade nos "
        f"cortes 2 e 3, que não vêm dali.\n")
    add("A consequência é uma acoplagem entre dois projetos que não "
        "compartilham build: o\nlimite medido da tabela do Obocaman se move "
        "quando alguém mexe no `Offsets.hpp`\ndo `newWe2002`. A "
        "**WTE-TASK-19** existe justamente para acrescentar offsets lá; um\n"
        "valor novo fora da faixa atual alarga a janela, e a corrida pode "
        "passar a engolir\no dword seguinte — a armadilha §8.7 entrando pela "
        "porta dos fundos. **Quem\nacrescentar offset tem de reconferir o "
        "limite das duas tabelas.**\n")
    add("Congelar a faixa numa constante foi considerado e recusado: a faixa "
        "derivada é o\nque faz o filtro acompanhar o que o projeto aprende. O "
        "que faltava não era\nrigidez, era esta acoplagem escrita.\n")
    add("O corte 3 parou onde parou de propósito. Um terceiro caso tentador — "
        "\"prefixo\nimprimível seguido de NUL\", que é a forma do `xyz` + NUL "
        "que fecha a tabela de\nalfabeto logo abaixo da tabela 1 — foi testado "
        "e **descartado**: como todo valor da\nfaixa cabe em três bytes, esse "
        "caso degenera em \"os três bytes baixos são\nimprimíveis\" e derruba "
        "cinco offsets conhecidos, `OFS_TEAM_NAME_4` = 2830160 =\n"
        "`0x002B2F50` entre eles. Quem mantém aquele `xyz` fora da tabela é o "
        "recorte pelo\nendereço-base referenciado por código, que é "
        "critério de "
        "posição e não de valor.\n")

    add("### Três critérios da tarefa que não sobreviveram à medição\n")
    lo_out = [n for n, v in m.declared if v < 1_000_000]
    hi_out = [n for n, v in m.declared if v > 8_000_000]
    unaligned = [n for n, v in m.declared if v % 4]
    va_window = [n for n, v in m.declared
                 if img.image_base <= v < img.image_base + img.size_of_image]
    only_unaligned = sorted(
        m.names[v] for v in m.confirmed
        if all(p % 4 for p in m.literals[v]))
    add(f"O markdown da tarefa sugere procurar dword \"entre 1.000.000 e "
        f"8.000.000,\nalinhado, referenciado por código\". Conferido contra o "
        f"próprio `Offsets.hpp`:\n")
    add("| Critério sugerido | Quantos dos "
        f"{n_declared} conhecidos ele descartaria |")
    add("|---|---:|")
    add(f"| valor abaixo de 1.000.000 | {len(lo_out)} |")
    add(f"| valor acima de 8.000.000 | {len(hi_out)} |")
    add(f"| valor não múltiplo de 4 | {len(unaligned)} |")
    add("")
    add(f"São {len(set(lo_out) | set(hi_out) | set(unaligned))} offsets "
        f"conhecidos que o critério sugerido jogaria fora — filtro\nassim não "
        f"serve para achar os desconhecidos, e por isso ele foi trocado pelos "
        f"quatro\ncortes acima. **Isto é uma correção ao enunciado da "
        f"WTE-TASK-06**, não uma\ndivergência de execução.\n")
    add(f"O mesmo vale para a tentação de descartar valor dentro da janela "
        f"`[ImageBase,\nImageBase+SizeOfImage)`: {len(va_window)} dos "
        f"{n_declared} offsets conhecidos caem nessa janela por\ncoincidência "
        f"numérica"
        + (f" (`{sorted(va_window)[0]}` entre eles)" if va_window else "")
        + f". A `.reloc` separa endereço de\nconstante sem heurística; a "
        f"janela de VA não separa.\n")
    aligned_hits = sum(1 for v in m.confirmed
                       if any(p % 4 == 0 for p in m.literals[v]))
    add(f"E \"alinhado\" também não vale para a **posição** do dword: "
        f"{len(only_unaligned)} dos\n{n_conf} offsets confirmados só aparecem "
        f"em posição desalinhada, porque são imediato de\ninstrução"
        + (f" (`{'`, `'.join(only_unaligned)}`)" if only_unaligned else "")
        + ". Uma varredura alinhada acha "
        f"{aligned_hits} "
        f"dos {n_conf}.\n")

    # ------------------------------------------------------ pergunta 1 ---
    add("## 1. Onde a tabela começa e onde termina\n")
    add(f"São **{len(m.tables)} {plural(len(m.tables), 'tabela', 'tabelas')}** "
        f"em `.data`: corrida de dwords 4-alinhados,\ntodos plausíveis ou "
        f"zero, começando num endereço que o `.text` referencia e\ncontendo "
        f"pelo menos um `OFS_*` conhecido.\n")

    for index, (table, nxt, agrees) in enumerate(m.bounds, 1):
        below_va = table.va - 4
        below_off = img.va_to_offset(below_va)
        below = _u32(img.data, below_off) if below_off is not None else 0
        above_off = img.va_to_offset(table.end_va)
        above = _u32(img.data, above_off) if above_off is not None else 0
        holes = [k for k, v in enumerate(table.slots) if v == 0]
        add(f"### Tabela {index} — `0x{table.va:08x}` … "
            f"`0x{table.end_va:08x}`\n")
        add(f"| Medida | Valor |")
        add(f"|---|---|")
        add(f"| primeiro byte | `0x{table.va:08x}` |")
        add(f"| primeiro byte **fora** | `0x{table.end_va:08x}` |")
        add(f"| tamanho | {table.size} bytes, {len(table.slots)} slots |")
        add(f"| slots preenchidos | {len(table.filled)} |")
        add(f"| buracos (`= 0`) | {len(holes)}"
            + (f" — slots {', '.join(str(h) for h in holes)}" if holes else "")
            + " |")
        add(f"| já em `Offsets.hpp` | {len(table.known)} de "
            f"{len(table.filled)} |")
        add(f"| referências a partir de `.text` | {table.referenced} ao "
            f"endereço-base |")
        add(f"| dword logo abaixo | `0x{below:08x}` = {below}"
            f" — bytes `{ascii_view(below)}`"
            + ("" if m.plausible(below)
               else ", não é offset plausível") + " |")
        add(f"| dword logo acima | `0x{above:08x}` = {above}"
            f" — bytes `{ascii_view(above)}`"
            + ("" if m.plausible(above)
               else ", não é offset plausível") + " |")
        add(f"| próximo endereço de `.data` referenciado por `.text` | "
            + (f"`0x{nxt:08x}`" if nxt is not None else "nenhum") + " |")
        add(f"| os dois critérios de limite | "
            + ("**coincidem**" if agrees else "divergem") + " |")
        add("")
        # Discordancia no sentido que nao aborta nao pode sumir dentro de
        # `self.bounds`: sem esta linha, `divergem` acima seria a unica pista,
        # e um leitor supoe que divergencia derruba a geracao.
        if not agrees and nxt is not None and nxt > table.end_va:
            add(f"> **Aviso.** O código referencia `0x{nxt:08x}`, "
                f"{nxt - table.end_va} bytes além do fim medido pelo "
                f"conteúdo.\n> O intervalo acima é o que o conteúdo sustenta; "
                f"o vizinho pode pertencer à\n> tabela. Este sentido da "
                f"discordância **não** derruba a geração — o que derruba é\n> "
                f"a referência *antes* do fim, que é a armadilha §8.7.\n")
        add("Conteúdo, na ordem em que está na memória:\n")
        add("| slot | VA | valor | `Offsets.hpp` |")
        add("|---:|---|---:|---|")
        for slot, value in enumerate(table.slots):
            name = m.names.get(value, "")
            shown = str(value) if value else "0"
            add(f"| {slot} | `0x{table.va + 4 * slot:08x}` | {shown} | "
                + (f"`{name}`" if name else ("— *(buraco)*" if not value
                                             else "— *(não nomeado)*"))
                + " |")
        add("")

    add("### O critério, escrito\n")
    add("O limite superior é medido por **dois testes independentes**, que se "
        "confrontam:\n")
    if m.tables:
        t0 = m.tables[0]
        first_hole = next((k for k, v in enumerate(t0.slots) if v == 0),
                          len(t0.slots))
        lost = len([v for v in t0.slots[first_hole:] if v])
        cut = (f"Tratar zero como terminador cortaria a\n  tabela 1 no slot "
               f"{first_hole} e perderia {lost} offsets")
    else:
        cut = "Zero como terminador cortaria a tabela cedo demais"
    add("- **pelo conteúdo** — a corrida acaba no primeiro dword que não é "
        "plausível nem\n  zero. Zero **não** encerra: é buraco. " + cut + ";\n"
        "- **por quem aponta para lá** — a tabela vai até o próximo endereço "
        "de `.data`\n  que o `.text` referencia. Nada dentro do intervalo é "
        "referenciado; só a base é.\n")
    add("**A discordância entre os dois não é tratada igual nos dois "
        "sentidos**, e o motivo\né que ela não significa a mesma coisa:\n")
    add("- **referência antes do fim medido pelo conteúdo — aborta.** É a "
        "armadilha §8.7\n  em pessoa: o conteúdo estica a tabela além do que o "
        "código sustenta, e publicar\n  isso seria dar como offset um slot que "
        "ninguém referencia;\n"
        "- **referência depois do fim — avisa e segue.** O intervalo publicado "
        "continua\n  sendo o que o conteúdo sustenta, então não há número "
        "errado a emitir; o que há é\n  um vizinho que talvez pertença à "
        "tabela. Sai como `AVISO:` na saída padrão e\n  na tabela de limites "
        "acima.\n")
    add("O limite **inferior** é o endereço-base referenciado pelo código, e "
        "esse critério\nnão é decorativo: no caso da tabela 1, o dword logo "
        "abaixo é numericamente\nplausível — é o `xyz` + NUL que fecha a "
        "tabela de alfabeto ASCII vizinha — e só o\nrecorte pela referência o "
        "mantém fora. Uma corrida sem referência nenhuma não é\ntratada como "
        "tabela.\n")

    if m.tables:
        t0 = m.tables[0]
        ascii_off = img.va_to_offset(t0.va - 16)
        ascii_word = _u32(img.data, ascii_off) if ascii_off is not None else 0
        add("### Uma correção à §8.7 do plano\n")
        add(f"A §8.7 diz que o bloco em `0x{t0.va:08x}` \"é **seguido** de "
            f"dados que não são\noffsets\", e dá como exemplo o valor "
            f"{ascii_word}, que é ASCII. Medido: esse dword\nestá em "
            f"`0x{t0.va - 16:08x}` — **16 bytes abaixo** da tabela, não "
            f"acima. Ele é `{ascii_view(ascii_word)}`, um\npedaço da tabela de "
            f"alfabeto que termina onde a de offsets começa.\n")
        after_off = img.va_to_offset(t0.end_va)
        after = _u32(img.data, after_off) if after_off is not None else 0
        add(f"A conclusão da §8.7 continua valendo — o bloco **é** cercado de "
            f"dado que não é\noffset dos dois lados, e o dword logo acima da "
            f"tabela é {after}\n(`0x{after:08x}`), que não passa no filtro. O "
            f"que muda é o lado: quem obriga a\nmedir o limite **inferior** é "
            f"o ASCII, e é por isso que o critério de início deste\nscript é "
            f"posicional (endereço referenciado por código) e não numérico.\n")

    add("### Corroboração por desmontagem\n")
    add("Transcrito de `objdump`, não do script — e é a terceira medida "
        "independente do\nmesmo limite. Com a `.text` recortada para um "
        "arquivo:\n")
    add("```sh\n"
        "objdump -D -b binary -m i386 -M intel --adjust-vma=0x401000 \\\n"
        "        --start-address=0x40cbc8 --stop-address=0x40cc30 "
        "text.bin\n```\n")
    add("O laço que percorre a tabela 1 é duplo:\n")
    add("```\n"
        "40cbdb:  mov  DWORD PTR [ebp-0x34],0x4231a0   ; ponteiro = base\n"
        "40cbe4:  mov  eax,DWORD PTR [ebp-0x34]        ; inicio da linha\n"
        "40cbeb:  cmp  DWORD PTR [ebx],0x0\n"
        "40cbee:  je   0x40cc18                        ; zero e PULADO\n"
        "  ...    (usa o offset em [ebx])\n"
        "40cc18:  inc  esi\n"
        "40cc19:  add  ebx,0x4\n"
        "40cc1c:  cmp  esi,0x6                         ; 6 colunas\n"
        "40cc1f:  jl   0x40cbeb\n"
        "40cc21:  inc  edi\n"
        "40cc22:  add  DWORD PTR [ebp-0x34],0x18       ; passo de linha = 24\n"
        "40cc26:  cmp  edi,0x3                         ; 3 linhas\n"
        "40cc29:  jl   0x40cbe4\n"
        "```\n")
    if m.tables:
        t0 = m.tables[0]
        add(f"Três linhas × seis colunas × 4 bytes = 72 bytes, exatamente o "
            f"tamanho que o\nscript mede para a tabela 1 ({t0.size} bytes, "
            f"{len(t0.slots)} slots). E o `je` sobre o teste de zero é\na "
            f"prova de que os {len([v for v in t0.slots if v == 0])} buracos "
            f"são buracos, não fim de array.\n")
    add("As duas linhas do bloco correspondem ao agrupamento que os nossos "
        "próprios nomes\njá sugerem: uma linha de nomes completos de time, uma "
        "de abreviações, e uma com\nkanji e caixa mista. Isso é leitura, não "
        "medida — o que está medido é o retângulo.\n")

    if m.copies:
        add("### A tabela não é única no arquivo\n")
        add(f"{len(m.copies)} {plural(len(m.copies), 'cópia', 'cópias')} "
            f"adicionais em `.data`, com a mesma sequência de valores byte a "
            f"byte:\n")
        add("| cópia de | endereço | bytes |")
        add("|---|---|---:|")
        for table, copy_va in sorted(m.copies, key=lambda c: (c[0].va, c[1])):
            add(f"| `0x{table.va:08x}` | `0x{copy_va:08x}` | {table.size} |")
        add("")
        add("Nenhuma das cópias é referenciada pelo `.text`; só o "
            "endereço-base "
            "da tabela\ncanônica é. **Consequência para a WTE-TASK-19:** "
            "candidato tem de ser contado por\n*valor*, não por ocorrência, ou "
            "cada offset apareceria várias vezes.\n")

    # ------------------------------------------------------ pergunta 2 ---
    add(f"## 2. Quais dos {n_declared} batem, e o que os outros "
        f"{n_missing} são\n")
    add(f"**{n_conf} dos {n_declared}** aparecem literalmente no binário — o "
        f"mesmo número que a §1.7\ndo plano registra. A varredura é do arquivo "
        f"inteiro, em qualquer alinhamento.\n")
    add("| `Offsets.hpp` | valor | onde |")
    add("|---|---:|---|")
    for name, value in m.declared:
        if value not in m.confirmed:
            continue
        places = m.literals[value]
        where = []
        for pos in places:
            sec = img.section_of_offset(pos)
            va = img.offset_to_va(pos)
            if sec is None or va is None:
                continue
            where.append(f"`{sec.name}` `0x{va:08x}`")
        add(f"| `{name}` | {value} | " + ", ".join(where) + " |")
    add("")

    text_only = [n for n, v in m.declared if v in m.confirmed
                 and all((img.section_of_offset(p).name if
                          img.section_of_offset(p) else "") == ".text"
                         for p in m.literals[v])]
    add(f"{n_conf - len(text_only)} moram em `.data`, dentro das tabelas da "
        f"seção 1; {len(text_only)} só existem como\nimediato de instrução em "
        f"`.text`"
        + (f" (`{'`, `'.join(sorted(text_only))}`)" if text_only else "")
        + ". As duas formas precisam de\nvarreduras diferentes, e é por isso "
        "que este script faz as duas.\n")

    add(f"### Os {n_missing} restantes, classificados\n")
    add("A classificação é **hipótese priorizada, não prova** — resolver é da "
        "WTE-TASK-19.\nA regra é busca em largura a partir das bases que o "
        "Obocaman comprovadamente tem:\n")
    add(f"- **H1** — deriva de um offset **confirmado**, por deslocamento "
        f"dentro do mesmo\n  setor (`|Δ| < {SECTOR_SIZE}`) ou por um número "
        f"inteiro de setores (`|k| <= {MAX_SECTOR_STEPS}`);\n"
        f"- **H2** — deriva de um **candidato** da seção 3, isto é, de uma "
        f"base que o\n  Obocaman tem e que este repositório ainda não nomeou. "
        f"É a classe mais\n  informativa: ela liga um `OFS_*` nosso a um "
        f"número dele;\n"
        f"- **H3** — nenhuma das duas. Região que o Moriero nomeou e que o "
        f"Obocaman não\n  alcança por esta aritmética.\n")
    add("Bases de profundidade maior que 1 são offsets ausentes já ligados: é "
        "o que faz uma\nfamília inteira de passo de setor entrar a partir de "
        "uma única âncora.\n")
    add("| Classe | Quantos |")
    add("|---|---:|")
    add(f"| H1 — base confirmada | {len(h1)} |")
    add(f"| H2 — base é candidato | {len(h2)} |")
    add(f"| H3 — sem base derivável | {len(h3)} |")
    add(f"| **total** | **{n_missing}** |")
    add("")
    add("| `Offsets.hpp` | valor | classe | base | relação | Δ | prof. |")
    add("|---|---:|---|---:|---|---:|---:|")
    for item in m.missing:
        base = "—" if item.base is None else str(item.base)
        if item.base_name:
            base += f" (`{item.base_name}`)"
        elif item.base is not None and item.cls != "H3":
            base += " *(candidato)*"
        add(f"| `{item.name}` | {item.value} | {item.cls} | {base} | "
            f"{item.relation or '—'} | {item.delta} | "
            f"{item.depth or '—'} |")
    add("")

    anchors = sorted({i.base for i in m.missing
                      if i.cls == "H2" and i.depth == 1 and i.base is not None})
    if anchors:
        add("### Os alvos que valem primeiro\n")
        add(f"{len(anchors)} "
            f"{plural(len(anchors), 'candidato ancora', 'candidatos ancoram')} "
            f"uma família H2 inteira. Confirmar um deles resolve todos os\n"
            f"`OFS_*` pendurados nele:\n")
        add("| candidato | ocorrências | resolve |")
        add("|---:|---:|---|")
        for anchor in anchors:
            occ = len(m.text_candidates.get(anchor,
                                            m.data_candidates.get(anchor, [])))
            attached = [i.name for i in m.missing
                        if i.cls == "H2" and i.base == anchor]
            add(f"| {anchor} | {occ} | `{'`, `'.join(attached)}` |")
        add("")

    if h3:
        add("### Os H3, e por que não é o fim da linha\n")
        all_cand = sorted(set(m.text_candidates) | set(m.data_candidates))
        add("| `Offsets.hpp` | valor | confirmado mais próximo | Δ | "
            "candidato mais próximo | Δ |")
        add("|---|---:|---:|---:|---:|---:|")
        for item in h3:
            near = (min(all_cand, key=lambda c: (abs(item.value - c), c))
                    if all_cand else None)
            add(f"| `{item.name}` | {item.value} | {item.base} | "
                f"{item.delta} | "
                + (f"{near} | {item.value - near} |" if near is not None
                   else "— | — |"))
        add("")
        add("H3 quer dizer \"não derivável pela regra deste script\", não "
            "\"o Obocaman não\nedita isso\". A regra aceita deslocamento "
            "dentro de um setor ou múltiplo inteiro\nde setor; um deslocamento "
            "de dois setores e meio não passa. A coluna do candidato\nmais "
            "próximo mostra que em vários casos há um número do Obocaman na "
            "vizinhança —\né por aí que a WTE-TASK-19 começa.\n")

    # ------------------------------------------------------ pergunta 3 ---
    n_text = len(m.text_candidates)
    n_data = len(m.data_candidates)
    total_cand = len(set(m.text_candidates) | set(m.data_candidates))
    add("## 3. Offsets que o Obocaman tem e nós não\n")
    add(f"**{total_cand} valores distintos** sobraram, todos ausentes do "
        f"`Offsets.hpp`. Não são\nofensivos até a WTE-TASK-19 confirmar cada "
        f"um; são a lista de alvos dela.\n")
    add("| Rota | Critério | Valores distintos |")
    add("|---|---|---:|")
    add(f"| `.text` | imediato de 32 bits em codificação de carga de "
        f"constante, plausível, não relocado | {n_text} |")
    add(f"| `.data` | dword de uma corrida que contém offset conhecido, "
        f"plausível, não relocado | {n_data} |")
    add("")

    if n_data == 0:
        add("**A rota `.data` devolveu zero, e isso é resultado.** Todo dword "
            "plausível que\nmora nas tabelas ao lado de um offset confirmado "
            "**já está** no `Offsets.hpp`: as\ntabelas do Obocaman estão "
            "inteiramente cobertas por este repositório. O que ele\ntem a mais "
            "está no código, não em tabela — e é por isso que a rota `.text` "
            "existe.\n")

    by_occ = sorted(m.text_candidates,
                    key=lambda v: (-len(m.text_candidates[v]), v))
    repeated = [v for v in by_occ if len(m.text_candidates[v]) > 1]
    add(f"### Os {len(repeated)} candidatos com mais de uma ocorrência\n")
    add("Ordenados por número de ocorrências. Repetição é o melhor sinal "
        "barato que\nexiste aqui: artefato de decodificação raramente aparece "
        "duas vezes com o mesmo\nvalor.\n")
    add("| valor | hex | setor | byte no setor | ocorrências | formas |")
    add("|---:|---|---:|---:|---:|---|")
    for value in repeated:
        places = m.text_candidates[value]
        sec, rem = sector_of(value)
        forms = ", ".join(f"`{f}`" for f in sorted({f for _, f in places}))
        add(f"| {value} | `0x{value:08x}` | {sec} | {rem} | {len(places)} | "
            f"{forms} |")
    add("")
    add(f"Os outros {n_text - len(repeated)} aparecem uma vez só e estão no "
        f"[`{TSV_NAME}`]({TSV_NAME}), com a mesma\nclassificação.\n")

    add("### Quanto disso é ruído\n")
    add("A varredura de `.text` casa padrão de byte; ela **não** é um "
        "desmontador, e casa em\nposição que um decodificador linear nunca "
        "visitaria. Exemplo real, para calibrar a\nconfiança: o valor 2204904 "
        "aparece uma única vez, em `0x0042013f`, e o `objdump`\nmostra que "
        "aquele endereço cai no meio de `mov DWORD PTR fs:0x0,ecx` — não "
        "existe\ninstrução ali. Candidato de ocorrência única merece "
        "desconfiança proporcional.\n")
    add("No outro extremo, o candidato mais frequente tem evidência forte de "
        "contexto. Em\n`0x004046ac`:\n")
    add("```\n"
        "40469e:  sar  edx,0xb                   ; indice / 2048\n"
        "4046a1:  lea  ecx,[edx+edx*8]\n"
        "4046a4:  lea  ecx,[edx+ecx*2]           ; ecx = 19 * edx\n"
        "4046a7:  shl  ecx,0x4                   ; ecx = 304 * edx\n"
        "4046aa:  add  eax,ecx\n"
        "4046ac:  add  eax,0x1e8178              ; + base\n"
        "```\n")
    add("`304 = 2352 - 2048` é exatamente o cabeçalho de setor que o formato "
        "obriga a\npular, e essa é a aritmética que o `CLAUDE.md` deste "
        "repositório descreve na seção\ndo formato MODE2/2352. Um valor usado "
        "como base **depois** dessa correção é offset\nde imagem, não "
        "coincidência.\n")

    # ------------------------------------------------------- ressalvas ---
    add("## Ressalvas\n")
    add(f"- **A rota `.text` sub-conta.** Ela cobre as codificações de carga "
        f"de constante\n  listadas no cabeçalho do script; um offset "
        f"construído em duas etapas (por\n  exemplo `mov` de 16 bits seguido "
        f"de `shl`) não aparece.\n"
        f"- **A rota `.text` super-conta.** Ver a seção de ruído acima.\n"
        f"- **Nada aqui foi conferido contra imagem de CD.** Os cortes são "
        f"estruturais\n  (geometria de setor, realocação, faixa); nenhum "
        f"candidato foi lido de uma\n  imagem real para ver o que tem lá. É a "
        f"WTE-TASK-19 que faz isso.\n"
        f"- **A classificação da seção 2 é ordenada por prioridade**, e a "
        f"escolha de base é\n  desempatada por (classe, profundidade, |Δ|, "
        f"base). Um mesmo `OFS_*` pode ter\n  mais de uma base compatível; a "
        f"tabela mostra a de maior confiança, não todas.\n"
        f"- **Nenhum byte do `.exe` foi copiado para cá.** O que este arquivo "
        f"traz são\n  medidas — endereços, contagens e valores numéricos —, no "
        f"espírito da §2 do\n  plano: recuperação de especificação, não "
        f"transcrição.\n")
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
    if not HPP.is_file():
        raise DumpError(f"{REL_HPP} nao existe.")

    img = Image(EXE.read_bytes())
    declared = read_offsets_hpp(HPP.read_text(encoding="utf-8"))
    m = Measurement(img, declared)
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
        print(f"{REL_OUT} nao corresponde a {REL_EXE} + {REL_HPP}:",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivos em dia com {REL_EXE} + {REL_HPP}")
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
