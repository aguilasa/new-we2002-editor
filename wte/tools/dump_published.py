#!/usr/bin/env python3
"""Extrai os 96 handlers publicados do we-team-editor.exe (WTE-TASK-04).

Todo formulario do editor do Obocaman e uma classe compilada por C++Builder 6,
e o VMT de cada uma carrega a *published method table* do VCL -- a tabela que o
streaming de DFM usa para resolver `OnClick = boton_mcrClick` em ponteiro de
codigo. Ela sobreviveu ao `/STRIP`. Este script le o `.exe`, percorre os VMTs,
cruza o resultado com os DFM da WTE-TASK-03 e escreve `wte/re/`:

  1. `published_methods.tsv` -- um registro por metodo publicado;
  2. `published_methods.md`  -- a leitura do TSV.

    python3 wte/tools/dump_published.py            # gera
    python3 wte/tools/dump_published.py --check    # regera e compara

Leitura pura: nem o `.exe` nem os `.dfm` sao abertos para escrita.


Duas fontes para o dono, cruzadas -- nunca uma escolhida em silencio
-------------------------------------------------------------------

O nome do handler sozinho nao identifica nada: `FormCreate` aparece em 16
formularios e `BitBtn1Click` em quatro. O dono vem de duas evidencias
independentes, e as duas sao medidas:

- **VMT** -- cada published method table pertence a uma classe, e o nome da
  classe esta no proprio VMT (`vmtClassName`, deslocamento -44). Esta e a
  fonte **autoritativa** da coluna `formulario`: ela existe mesmo para handler
  que nenhum DFM referencia.
- **DFM** -- `OnClick = <nome>` em `wte/re/dfm/*.dfm` diz qual componente de
  qual formulario esta ligado ao handler, e em que evento. E a fonte das
  colunas `componente` e `evento`, e a conferencia da coluna `formulario`.

O script compara os dois conjuntos de pares (formulario, handler) e **reporta**
a diferenca em vez de resolve-la: handler publicado que nenhum DFM referencia
sai marcado na coluna `nota`, e o `.md` o nomeia. Par que aparece no DFM e nao
no VMT seria erro grave (o streaming do original nao acharia o metodo) e
**aborta**.


A geometria do VMT, e por que a assinatura e o auto-ponteiro
------------------------------------------------------------

O VMT que o Delphi/C++Builder emite e um array de metodos virtuais precedido de
um cabecalho de campos em deslocamento **negativo**, fixo desde o Delphi 4:

    -76  vmtSelfPtr        aponta para o proprio VMT
    -52  vmtMethodTable    a published method table (0 quando nao ha nenhuma)
    -44  vmtClassName      short string com o nome da classe
    -40  vmtInstanceSize
    -36  vmtParent

Procurar `vmtSelfPtr` -- dword cujo valor e o endereco dele mesmo mais 76 -- e
o que localiza os VMTs sem depender de simbolo nenhum, e e uma assinatura que
nao da falso positivo por acaso: em `.data` inteira ela casa 19 vezes, e a
19a e rejeitada porque `vmtClassName` e nulo.

A tabela em si e `word contagem` seguida de `contagem` entradas, cada uma
`word tamanho`, `dword endereco`, `byte tamanho do nome`, nome. O campo
`tamanho` cobre a entrada inteira; o script confere `tamanho == 7 + len(nome)`
em todas as 96 e aborta na primeira que discordar.


A coluna `grupo`, e por que ela e regra e nao opiniao
-----------------------------------------------------

`grupo` e o que reparte os 96 entre as WTE-TASK-25 (carga), 26 (edicao), 27
(gravacao) e 28 (auxiliares). O enunciado da WTE-TASK-04 a chama de
"classificacao manual", mas saida de gerador tem de ser reproduzivel: aqui ela
sai de **oito regras ordenadas** (`RULES`) mais uma **tabela de excecoes**
(`EXCEPTIONS`), cada excecao com o motivo escrito ao lado. Assim o `--check`
cobre a coluna, e discordar de uma classificacao vira editar uma linha
identificavel em vez de reabrir um julgamento.

Duas fontes alimentam as regras, e as duas sao medidas do binario:

- as **13 unidades de dialogo exportadas** (`@@Tep2002_<x>@Initialize` em
  `.edata`), que sao os formularios pequenos e dao a regra R6 (auxiliar);
- os nomes que a IDE gera sozinha (`BitBtn1Click`, `SpeedButton2Click`), que
  sao moldura de dialogo -- abrir, fechar, OK/Cancelar -- e dao a R7.

`FORMULA_OWNERS` marca, na coluna `nota`, os 16 handlers que a WTE-TASK-28
expressamente **exclui** do seu escopo por serem formula e nao dialogo (preco
na WTE-TASK-30, render 2D na WTE-TASK-32). Eles continuam com `grupo` entre os
quatro valores -- nao ha um quinto --, e a `nota` evita trabalho dobrado.


Falha alta
----------

`.exe` ausente, secao de PE que falta, entrada de VMT malformada, nome de
tamanho impossivel, contagem que nao fecha, `.dfm` que nao parseia, formulario
sem VMT (ou VMT sem `.dfm`), excecao que nao casa com nenhum handler -- todos
abortam com o offset absoluto e o contexto. Nenhuma saida parcial vai para o
disco: os dois arquivos so sao escritos depois que tudo foi medido.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
DFM = ROOT / "wte" / "re" / "dfm"
OUT = ROOT / "wte" / "re"

# Caminhos relativos nas mensagens e na saida -- caminho absoluto quebraria a
# estabilidade byte a byte entre maquinas.
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_DFM = "wte/re/dfm"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_published.py"

TSV_NAME = "published_methods.tsv"
MD_NAME = "published_methods.md"

# Deslocamentos negativos do VMT do Delphi/C++Builder. Fixos desde o Delphi 4;
# ver o cabecalho do modulo.
VMT_SELF_PTR = -76
VMT_METHOD_TABLE = -52
VMT_CLASS_NAME = -44
VMT_INSTANCE_SIZE = -40
VMT_PARENT = -36

# Tamanho fixo de uma entrada da published method table, sem o nome:
# word tamanho + dword endereco + byte tamanho do nome.
METHOD_ENTRY_FIXED = 7

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Nome de componente que a IDE gera sozinha. Handler pendurado num desses e
# moldura de dialogo -- e a regra R7.
GENERIC_COMPONENT = re.compile(
    r"^(BitBtn|Button|Image|SpeedButton)[0-9]+Click$")


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


# ------------------------------------------------------------- excecoes ---
#
# TABELA DE EXCECOES DA COLUNA `grupo`.
#
# Cada linha e um (formulario, handler) que as oito regras classificariam
# errado, com o motivo. O script aborta se alguma chave daqui nao casar com um
# handler real -- excecao morta e pior do que excecao errada, porque ninguem a
# ve envelhecer.

EXCEPTIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("MainForm", "boton_mcrClick"): (
        "carga",
        "abre o `.mcr` do memory card: lê, não grava. O par que grava é "
        "`boton_mcr2isoClick`, e o prefixo `boton_` sozinho não separa os "
        "dois."),
    ("MainForm", "base_teamClick"): (
        "auxiliar",
        "a WTE-TASK-28 o lista entre os auxiliares; o nome não é genérico o "
        "bastante para a R7 alcançá-lo."),
    ("estrategia", "ComboBoxDrawItem"): (
        "carga",
        "owner-draw do combo de formações — só pinta. A WTE-TASK-25 o "
        "reivindica junto com a lista que ele desenha, e é ela que ordena o "
        "trabalho."),
    ("ficha_color", "botonClick"): (
        "auxiliar",
        "a WTE-TASK-28 o lista entre os auxiliares, ao lado dos BitBtn do "
        "mesmo formulário."),
    ("ficha_color", "lista_col0Change"): (
        "edicao",
        "lista de cor da paleta do editor 2D, não carga de dado do jogo — o "
        "prefixo `lista_` da R4 aponta para o lado errado aqui."),
    ("ficha_color", "lista_col1change"): (
        "edicao",
        "idem `lista_col0Change`. O `c` minúsculo de `change` está no binário "
        "e é transcrito verbatim."),
    ("ficha_color", "lista_col2Change"): (
        "edicao", "idem `lista_col0Change`."),
    ("ficha_color", "lista_col3Change"): (
        "edicao", "idem `lista_col0Change`."),
    ("ficha_dorsal", "scroll_dorsalChange"): (
        "edicao",
        "`ficha_dorsal` está entre os 13 diálogos exportados, mas este "
        "handler edita o número da camisa em vez de ser moldura: a "
        "WTE-TASK-26 o lista nominalmente."),
}

# Os 16 handlers que a WTE-TASK-28 exclui do proprio escopo por serem formula,
# nao dialogo. Nao mudam o `grupo` -- so viram anotacao, para que a fase 4 nao
# os implemente duas vezes. Transcrito da tabela "O que fica de fora, e por
# que" daquela tarefa, com uma correcao medida: `malla1MouseDown` e
# `malla2MouseDown` pertencem a `estrategia`, nao a `ficha_color`.
# Os dez nomes que a WTE-TASK-28 lista como "handlers repetidos por varios
# formularios". A lista e literal -- e citacao de outro documento --, mas o
# veredito de cada nome sai de count_by_name(), e um nome que nao exista entre
# os 96 aborta, como em EXCEPTIONS e FORMULA_OWNERS. A linha de envelhecimento
# saia escrita a mao para um unico nome (`botonClick`) quando a mesma consulta
# responde pelos dez.
TASK28_REPEATED: tuple[str, ...] = (
    "BitBtn1Click", "BitBtn2Click", "BitBtn3Click", "SpeedButton1Click",
    "SpeedButton2Click", "Button2Click", "Image3Click", "botonClick",
    "base_teamClick", "imagen_urlClick",
)

FORMULA_OWNERS: dict[tuple[str, str], str] = {
    ("jugador", "etiqprecioClick"): "WTE-TASK-30",
    ("jugador", "casilla_precioKeyPress"): "WTE-TASK-30",
    ("MainForm", "colorearClick"): "WTE-TASK-32",
    ("ficha_color", "gradienteClick"): "WTE-TASK-32",
    ("ficha_color", "oscurecerClick"): "WTE-TASK-32",
    ("ficha_color", "aclararClick"): "WTE-TASK-32",
    ("ficha_color", "lista_col0Change"): "WTE-TASK-32",
    ("ficha_color", "lista_col1change"): "WTE-TASK-32",
    ("ficha_color", "lista_col2Change"): "WTE-TASK-32",
    ("ficha_color", "lista_col3Change"): "WTE-TASK-32",
    ("ficha_color", "colorMouseDown"): "WTE-TASK-32",
    ("ficha_color", "barraChange"): "WTE-TASK-32",
    ("ficha_color", "barra1Change"): "WTE-TASK-32",
    ("ficha_color", "barra2Change"): "WTE-TASK-32",
    ("estrategia", "malla1MouseDown"): "WTE-TASK-32",
    ("estrategia", "malla2MouseDown"): "WTE-TASK-32",
}

GROUPS = ("carga", "edicao", "gravacao", "auxiliar")

GROUP_LABEL = {
    "carga": "carga",
    "edicao": "edição",
    "gravacao": "gravação",
    "auxiliar": "auxiliar",
}

GROUP_TASK = {
    "carga": ("WTE-TASK-25", "../../docs/tasks/25-handlers-de-carga.md"),
    "edicao": ("WTE-TASK-26", "../../docs/tasks/26-handlers-de-edicao.md"),
    "gravacao": ("WTE-TASK-27", "../../docs/tasks/27-handlers-de-gravacao.md"),
    "auxiliar": ("WTE-TASK-28", "../../docs/tasks/28-handlers-auxiliares.md"),
}


# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do dfm_extract.py e do
# dump_offsets.py: o que este script precisa do formato cabe em poucas dezenas
# de linhas, e sem dependencia o `make -C wte check` roda em qualquer maquina
# com Python 3.


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
    """O `.exe` lido: secoes, base e a tabela de exportacao."""

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
        for needed in (".text", ".data", ".edata"):
            if self.section(needed) is None:
                raise DumpError(f"{REL_EXE}: secao {needed} ausente")

        n_dirs = _u32(data, opt + 92)
        if n_dirs < 1:
            raise DumpError(
                f"{REL_EXE}: optional header sem diretorio de exportacao")
        self.export_rva, self.export_size = struct.unpack_from(
            "<II", data, opt + 96)

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

    # -- leitura ----------------------------------------------------------

    def short_string(self, va: int) -> str | None:
        """Short string do Pascal: byte de tamanho seguido dos caracteres."""
        off = self.va_to_offset(va)
        if off is None:
            return None
        n = self.data[off]
        raw = self.data[off + 1:off + 1 + n]
        if len(raw) != n:
            return None
        return raw.decode("latin-1")

    def asciiz(self, rva: int) -> str | None:
        off = self.rva_to_offset(rva)
        if off is None:
            return None
        end = self.data.find(b"\0", off)
        if end == -1:
            return None
        return self.data[off:end].decode("latin-1")

    def export_names(self) -> list[str]:
        """Os nomes exportados, na ordem da tabela (que e ordenada)."""
        if self.export_rva == 0:
            raise DumpError(f"{REL_EXE}: tabela de exportacao vazia")
        base = self.rva_to_offset(self.export_rva)
        if base is None:
            raise DumpError(
                f"{REL_EXE}: diretorio de exportacao em RVA "
                f"{self.export_rva:#x} fora de qualquer secao")
        n_names = _u32(self.data, base + 24)
        names_rva = _u32(self.data, base + 32)
        table = self.rva_to_offset(names_rva)
        if table is None:
            raise DumpError(
                f"{REL_EXE}: AddressOfNames em RVA {names_rva:#x} fora de "
                f"qualquer secao")
        out: list[str] = []
        for i in range(n_names):
            name = self.asciiz(_u32(self.data, table + 4 * i))
            if name is None:
                raise DumpError(
                    f"{REL_EXE}: nome de exportacao {i} nao termina em NUL")
            out.append(name)
        return out


# -------------------------------------------------------------------- VMT ---


class Method:
    """Uma entrada da published method table."""

    __slots__ = ("addr", "name", "cls", "form", "entry_va")

    def __init__(self, addr: int, name: str, cls: str, entry_va: int):
        self.addr = addr
        self.name = name
        self.cls = cls
        self.form = cls[1:]
        self.entry_va = entry_va


class Vmt:
    __slots__ = ("va", "cls", "form", "instance_size", "table_va", "methods")

    def __init__(self, va: int, cls: str, instance_size: int, table_va: int):
        self.va = va
        self.cls = cls
        self.form = cls[1:]
        self.instance_size = instance_size
        self.table_va = table_va
        self.methods: list[Method] = []


def scan_vmts(img: Image) -> list[Vmt]:
    """Os VMTs de `.data`, achados pelo auto-ponteiro e validados.

    Restrito a `.data` de proposito: e onde o C++Builder emite VMT de classe
    do proprio modulo, e varrer `.rsrc` (891 KiB de bitmap) so acrescentaria
    superficie para falso positivo. O fechamento -- um VMT por `.dfm`, um
    `.dfm` por VMT -- e conferido depois, e ele e que pegaria um VMT perdido
    fora daqui.
    """
    sec = img.section(".data")
    assert sec is not None
    data = img.data
    out: list[Vmt] = []
    rejected = 0
    for off in range(sec.raw_ptr, sec.raw_ptr + sec.raw_size - 4, 4):
        self_va = img.offset_to_va(off)
        if self_va is None:
            continue
        if _u32(data, off) != self_va - VMT_SELF_PTR:
            continue
        va = self_va - VMT_SELF_PTR
        vmt_off = img.va_to_offset(va)
        if vmt_off is None:
            rejected += 1
            continue
        cls_ptr = _u32(data, vmt_off + VMT_CLASS_NAME)
        cls = img.short_string(cls_ptr) if cls_ptr else None
        size = _u32(data, vmt_off + VMT_INSTANCE_SIZE)
        if not cls or not IDENT.match(cls) or size == 0:
            # O binario tem exatamente um casamento assim: um dword que vale o
            # proprio endereco mais 76 por coincidencia, com vmtClassName nulo.
            rejected += 1
            continue
        table_va = _u32(data, vmt_off + VMT_METHOD_TABLE)
        if table_va and img.va_to_offset(table_va) is None:
            raise DumpError(
                f"{REL_EXE}: VMT de {cls} em 0x{va:08x} aponta a published "
                f"method table para 0x{table_va:08x}, que nao cai em secao "
                f"nenhuma.")
        out.append(Vmt(va, cls, size, table_va))
    out.sort(key=lambda v: v.va)
    scan_vmts.rejected = rejected           # type: ignore[attr-defined]
    return out


def read_method_table(img: Image, vmt: Vmt) -> None:
    """Preenche `vmt.methods` a partir de `vmt.table_va`.

    Formato: `word contagem`, depois `contagem` entradas de
    `word tamanho`, `dword endereco`, `byte tamanho do nome`, nome.
    """
    if not vmt.table_va:
        return
    data = img.data
    off = img.va_to_offset(vmt.table_va)
    assert off is not None
    count = _u16(data, off)
    p = off + 2
    text = img.section(".text")
    assert text is not None
    lo = img.image_base + text.rva
    hi = lo + text.raw_size
    for i in range(count):
        if p + METHOD_ENTRY_FIXED > len(data):
            raise DumpError(
                f"{REL_EXE}: fim de arquivo dentro da published method table "
                f"de {vmt.cls} (entrada {i} de {count}, offset {p})")
        size = _u16(data, p)
        addr = _u32(data, p + 2)
        n = data[p + 6]
        name = data[p + 7:p + 7 + n].decode("latin-1")
        if size != METHOD_ENTRY_FIXED + n:
            raise DumpError(
                f"{REL_EXE}: entrada {i} da tabela de {vmt.cls}, offset "
                f"absoluto {p}: tamanho declarado {size}, esperado "
                f"{METHOD_ENTRY_FIXED + n} para o nome {name!r} de {n} "
                f"caracteres. A tabela nao esta alinhada com o formato -- "
                f"medir mais nada aqui seria inventar.")
        if n == 0 or len(name) != n or not IDENT.match(name):
            raise DumpError(
                f"{REL_EXE}: entrada {i} da tabela de {vmt.cls}, offset "
                f"absoluto {p}: nome de {n} bytes nao e identificador "
                f"({name!r}).")
        if not lo <= addr < hi:
            raise DumpError(
                f"{REL_EXE}: {vmt.cls}.{name} aponta para 0x{addr:08x}, fora "
                f"de `.text` (0x{lo:08x}..0x{hi:08x}).")
        entry_va = img.offset_to_va(p)
        assert entry_va is not None
        vmt.methods.append(Method(addr, name, vmt.cls, entry_va))
        p += size


def dialog_units(img: Image, forms: set[str]) -> list[str]:
    """Os formularios cujo diario o linker exportou -- os dialogos pequenos.

    O C++Builder exporta `@@T<unidade>@Initialize` / `@Finalize` para cada
    unidade com codigo de inicializacao a emitir. As telas grandes nao tem, e
    por isso nao aparecem: e exatamente o corte que a secao 1.3 do plano
    descreve, e o mesmo que a WTE-TASK-28 chama de "os 13 dialogos".

    A tabela de nomes deste binario **repete** entrada (79 nomes, 46
    distintos: `@@Tep2002_info@Initialize` aparece tres vezes). O que importa
    aqui e o conjunto, e nao a contagem de linhas da tabela.
    """
    pat = re.compile(r"^@@Tep2002_(\w+)@Initialize$")
    seen: set[str] = set()
    for name in img.export_names():
        m = pat.match(name)
        if not m:
            continue
        form = "ficha_" + m.group(1)
        if form not in forms:
            raise DumpError(
                f"{REL_EXE}: a exportacao {name} sugere o formulario {form}, "
                f"que nao existe entre os {len(forms)} medidos. A regra R6 da "
                f"coluna `grupo` depende dessa correspondencia.")
        seen.add(form)
    out = sorted(seen)
    if len(out) >= len(forms):
        raise DumpError(
            f"{REL_EXE}: {len(out)} unidades exportadas para {len(forms)} "
            f"formularios. A regra R6 separa dialogo pequeno de tela grande; "
            f"se todo formulario exporta unidade, ela nao separa nada.")
    if not out:
        raise DumpError(
            f"{REL_EXE}: nenhuma exportacao `@@Tep2002_<x>@Initialize`. A "
            f"regra R6 da coluna `grupo` sai dai; sem ela a classificacao nao "
            f"tem base medida.")
    return sorted(out)


# -------------------------------------------------------------------- DFM ---


class Binding:
    """Uma ligacao `On<Evento> = <handler>` de um `.dfm`."""

    __slots__ = ("form", "component", "event", "handler", "line")

    def __init__(self, form: str, component: str, event: str, handler: str,
                 line: int):
        self.form = form
        self.component = component
        self.event = event
        self.handler = handler
        self.line = line


_OBJECT = re.compile(
    r"^(\s*)(?:inherited|inline|object)\s+([A-Za-z_]\w*)\s*:\s*"
    r"([A-Za-z_]\w*)\s*$")
# Componente sem nome. O DFM guarda nome e classe separados, e o autor pode
# apagar o nome; o `MainForm` tem exatamente um caso (`object TStaticText`, um
# retangulo de 4x4 sem evento). Sem nome nao ha o que citar na coluna
# `componente`, e a forma `<TClasse>` deixa isso explicito se algum dia um
# desses ganhar um evento.
_OBJECT_ANON = re.compile(r"^(\s*)object\s+([A-Za-z_]\w*)\s*$")
_END = re.compile(r"^\s*end\s*$")
_PROP = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=\s*(.*)$")
_EVENT = re.compile(r"^On[A-Z]\w*$")


def _closes_list(line: str) -> bool:
    """A linha fecha uma lista `(...)` do DFM?

    O Delphi cola o `)` no ultimo item (`'texto')`). Um item que termine em
    `)` dentro da string -- `'Team (A)'` -- nao pode ser confundido com o
    fechamento, e a paridade de aspas resolve: retirado o `)` final, o que
    sobra tem numero par de `'` quando o `)` estava fora da string.
    """
    stripped = line.rstrip()
    if not stripped.endswith(")"):
        return False
    return stripped[:-1].count("'") % 2 == 0


def parse_dfm(path: Path) -> tuple[str, list[Binding]]:
    """Le um `.dfm` textual e devolve (formulario, ligacoes de evento).

    Nao e um parser completo de DFM: e um leitor de estrutura que reconhece
    `object`/`end`, propriedade simples e lista `(...)` multilinha, e
    **aborta** em qualquer outra construcao multilinha (colecao `<...>`,
    string continuada com `+`). Os 18 formularios deste binario nao tem
    nenhuma delas; abortar e o que garante que isso continue verdade.
    """
    rel = f"{REL_DFM}/{path.name}"
    form: str | None = None
    stack: list[tuple[int, str]] = []
    bindings: list[Binding] = []
    in_list = False

    for line_no, line in enumerate(path.read_text(encoding="utf-8")
                                   .splitlines(), 1):
        if in_list:
            if _closes_list(line):
                in_list = False
            continue

        m = _OBJECT.match(line) or _OBJECT_ANON.match(line)
        if m:
            indent = len(m.group(1))
            named = m.re is _OBJECT
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent,
                          m.group(2) if named else f"<{m.group(2)}>"))
            if form is None:
                if not named:
                    raise DumpError(
                        f"{rel}:{line_no}: o objeto raiz nao tem nome")
                form = m.group(2)
            continue

        if _END.match(line):
            if not stack:
                raise DumpError(
                    f"{rel}:{line_no}: `end` sem `object` correspondente")
            stack.pop()
            continue

        m = _PROP.match(line)
        if m:
            if not stack:
                raise DumpError(
                    f"{rel}:{line_no}: propriedade {m.group(1)!r} fora de "
                    f"qualquer objeto")
            name, value = m.group(1), m.group(2).strip()
            if value == "(":
                in_list = True
                continue
            if value.startswith("<") or value.endswith("+"):
                raise DumpError(
                    f"{rel}:{line_no}: construcao DFM multilinha nao "
                    f"suportada em {name!r} ({value!r}). Este leitor cobre "
                    f"`object`/`end`, propriedade simples e lista `(...)`; "
                    f"colecao e string continuada teriam de ser "
                    f"implementadas antes de a saida valer.")
            if _EVENT.match(name):
                if not IDENT.match(value):
                    raise DumpError(
                        f"{rel}:{line_no}: {name} = {value!r} nao e nome de "
                        f"metodo")
                bindings.append(
                    Binding(form or "?", stack[-1][1], name, value, line_no))
            continue

        if line.strip():
            raise DumpError(
                f"{rel}:{line_no}: linha nao reconhecida: {line.strip()!r}")

    if stack:
        raise DumpError(
            f"{rel}: fim de arquivo com {len(stack)} objeto(s) em aberto "
            f"({', '.join(n for _, n in stack)})")
    if form is None:
        raise DumpError(f"{rel}: nenhum objeto raiz")
    if form != path.stem:
        raise DumpError(
            f"{rel}: objeto raiz {form!r} nao corresponde ao nome do arquivo "
            f"{path.stem!r}. O `dfm_extract.py` nomeia o arquivo pelo objeto "
            f"raiz; divergencia aqui quer dizer que algum dos dois mudou.")
    return form, bindings


# --------------------------------------------------------- classificacao ---
#
# AS OITO REGRAS, NA ORDEM EM QUE SAO TENTADAS. A primeira que casar decide, e
# `EXCEPTIONS` vem antes de todas. Cada regra e (id, grupo, motivo, predicado).


def _rules() -> list[tuple[str, str, str, object]]:
    return [
        ("R1", "gravacao",
         "nome começa com `grabar_` ou contém `2iso` — os seis pontos em que "
         "o app escreve",
         lambda h, f: h.startswith("grabar_") or "2iso" in h),
        ("R2", "carga",
         "`FormCreate` / `FormShow` — inicialização de formulário",
         lambda h, f: h in ("FormCreate", "FormShow")),
        ("R3", "carga",
         "nome começa com `boton_dialogo_` — abre arquivo por diálogo",
         lambda h, f: h.startswith("boton_dialogo_")),
        ("R4", "carga",
         "nome começa com `lista_` — seleção numa lista que popula a tela",
         lambda h, f: h.startswith("lista_")),
        ("R5", "carga",
         "nome começa com `mostrar_` — abre uma tela já populada",
         lambda h, f: h.startswith("mostrar_")),
        ("R6", "auxiliar",
         "o formulário está entre as unidades de diálogo exportadas",
         None),                     # depende dos dados; ligado em classify()
        ("R7", "auxiliar",
         "nome de componente gerado pela IDE (`BitBtn1Click`, "
         "`SpeedButton2Click`, ...) — moldura de diálogo",
         lambda h, f: bool(GENERIC_COMPONENT.match(h))),
        ("R8", "edicao",
         "nenhuma das anteriores: altera estado em memória",
         lambda h, f: True),
    ]


def classify(handler: str, form: str, dialogs: set[str]
             ) -> tuple[str, str, str]:
    """Devolve (grupo, id da regra, motivo)."""
    key = (form, handler)
    if key in EXCEPTIONS:
        group, why = EXCEPTIONS[key]
        return group, "EX", why
    for rule_id, group, why, pred in _rules():
        if rule_id == "R6":
            if form in dialogs:
                return group, rule_id, why
            continue
        assert pred is not None
        if pred(handler, form):            # type: ignore[operator]
            return group, rule_id, why
    raise DumpError(f"{handler} em {form}: nenhuma regra casou")


# ----------------------------------------------------------------- medida ---


class Row:
    __slots__ = ("method", "bindings", "group", "rule", "why", "note")

    def __init__(self, method: Method):
        self.method = method
        self.bindings: list[Binding] = []
        self.group = ""
        self.rule = ""
        self.why = ""
        self.note: list[str] = []


class Measurement:
    """Tudo o que foi medido, antes de virar texto."""

    def __init__(self, img: Image, forms: dict[str, list[Binding]]):
        self.img = img
        self.forms = forms

        self.vmts = scan_vmts(img)
        self.rejected = getattr(scan_vmts, "rejected", 0)
        for vmt in self.vmts:
            read_method_table(img, vmt)

        self.check_closure()

        self.dialogs = dialog_units(img, set(forms))

        self.methods = sorted(
            (m for v in self.vmts for m in v.methods),
            key=lambda m: (m.addr, m.form, m.name))
        self.check_unique()

        self.rows = [Row(m) for m in self.methods]
        by_key = {(r.method.form, r.method.name): r for r in self.rows}
        self.by_key = by_key

        # Cruzamento VMT x DFM.
        self.dfm_pairs: dict[tuple[str, str], list[Binding]] = {}
        for form, bindings in forms.items():
            for b in bindings:
                self.dfm_pairs.setdefault((form, b.handler), []).append(b)

        orphans = sorted(set(self.dfm_pairs) - set(by_key))
        if orphans:
            lines = "\n".join(
                f"         {f}.{h} "
                f"({REL_DFM}/{f}.dfm:{self.dfm_pairs[(f, h)][0].line})"
                for f, h in orphans)
            raise DumpError(
                f"{len(orphans)} ligacao(oes) de DFM apontam para um metodo "
                f"que nao esta publicado no VMT da classe:\n{lines}\n"
                f"       Isso nao pode acontecer num binario que roda -- o "
                f"streaming do proprio original nao acharia o metodo. Ou o "
                f"{REL_DFM} foi editado a mao, ou a leitura do VMT esta "
                f"errada.")

        for key, bindings in self.dfm_pairs.items():
            by_key[key].bindings = bindings

        self.unreferenced = [r for r in self.rows if not r.bindings]

        # Classificacao.
        used_exceptions: set[tuple[str, str]] = set()
        used_formula: set[tuple[str, str]] = set()
        dialogs = set(self.dialogs)
        for row in self.rows:
            key = (row.method.form, row.method.name)
            if key in EXCEPTIONS:
                used_exceptions.add(key)
            row.group, row.rule, row.why = classify(
                row.method.name, row.method.form, dialogs)
            if row.group not in GROUPS:
                raise DumpError(
                    f"grupo {row.group!r} fora dos quatro declarados")
            if not row.bindings:
                row.note.append("sem referencia em DFM")
            if key in FORMULA_OWNERS:
                used_formula.add(key)
                row.note.append(FORMULA_OWNERS[key])

        dead = sorted(set(EXCEPTIONS) - used_exceptions)
        if dead:
            raise DumpError(
                "excecao(oes) da tabela EXCEPTIONS que nao casam com nenhum "
                "handler medido: "
                + ", ".join(f"{f}.{h}" for f, h in dead)
                + ".\n       Excecao morta e pior do que excecao errada: "
                  "ninguem a ve envelhecer. Corrija a chave ou remova a "
                  "linha.")
        dead = sorted(set(FORMULA_OWNERS) - used_formula)
        if dead:
            raise DumpError(
                "entrada(s) de FORMULA_OWNERS sem handler correspondente: "
                + ", ".join(f"{f}.{h}" for f, h in dead) + ".")

        medidos = {r.method.name for r in self.rows}
        dead = sorted(set(TASK28_REPEATED) - medidos)
        if dead:
            raise DumpError(
                "nome(s) citado(s) da WTE-TASK-28 que nao existem entre os "
                f"{len(self.rows)} handlers medidos: " + ", ".join(dead)
                + ".\n       A tabela de envelhecimento emitiria uma linha "
                  "sobre um handler que nao\n       existe. Corrija a citacao "
                  "ou remova o nome de TASK28_REPEATED.")

        self.distribution = {g: sum(1 for r in self.rows if r.group == g)
                             for g in GROUPS}

    # -- fechamentos ------------------------------------------------------

    def check_closure(self) -> None:
        """Um VMT por `.dfm`, um `.dfm` por VMT, e a classe e `T` + o objeto.

        Este e o fechamento que substitui confiar na varredura: se um VMT
        tivesse ficado fora de `.data`, ou se um formulario tivesse sido
        perdido, os dois conjuntos deixariam de bater aqui.
        """
        vmt_forms = {v.form for v in self.vmts}
        dfm_forms = set(self.forms)
        only_vmt = sorted(vmt_forms - dfm_forms)
        only_dfm = sorted(dfm_forms - vmt_forms)
        if only_vmt or only_dfm:
            raise DumpError(
                f"os VMTs de `.data` e os arquivos de {REL_DFM} nao fecham.\n"
                f"       so no VMT: {', '.join(only_vmt) or '-'}\n"
                f"       so no DFM: {', '.join(only_dfm) or '-'}\n"
                f"       A coluna `formulario` sai do VMT e e conferida "
                f"contra o DFM; sem a bijecao nao ha o que conferir.")
        for vmt in self.vmts:
            if vmt.cls != "T" + vmt.form:
                raise DumpError(
                    f"{REL_EXE}: a classe {vmt.cls} em 0x{vmt.va:08x} nao e "
                    f"`T` + {vmt.form!r}. A coluna `formulario` deriva o nome "
                    f"do objeto do nome da classe; a regra tem de valer para "
                    f"os {len(self.vmts)}.")

    def check_unique(self) -> None:
        seen: dict[tuple[str, str], Method] = {}
        for m in self.methods:
            key = (m.form, m.name)
            if key in seen:
                raise DumpError(
                    f"{REL_EXE}: {m.cls}.{m.name} publicado duas vezes "
                    f"(0x{seen[key].addr:08x} e 0x{m.addr:08x})")
            seen[key] = m


# ------------------------------------------------------------------- TSV ---

TSV_COLUMNS = ["endereco", "handler", "formulario", "componente", "evento",
               "grupo", "regra", "nota"]


def render_tsv(m: Measurement) -> str:
    lines = ["\t".join(TSV_COLUMNS)]
    for row in m.rows:
        method = row.method
        lines.append("\t".join([
            f"0x{method.addr:08x}",
            method.name,
            method.form,
            "|".join(b.component for b in row.bindings),
            "|".join(b.event for b in row.bindings),
            row.group,
            row.rule,
            "; ".join(row.note),
        ]))
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------- markdown ---


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def count_by_name(m: Measurement) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in m.rows:
        out.setdefault(row.method.name, []).append(row.method.form)
    return out


def render_md(m: Measurement) -> str:
    L: list[str] = []
    add = L.append
    total = len(m.rows)
    n_bind = sum(len(r.bindings) for r in m.rows)
    homonyms = {n: f for n, f in count_by_name(m).items() if len(f) > 1}

    add("# `re/published_methods.md` — os 96 handlers, com dono\n")
    add("Produto da "
        "[WTE-TASK-04](../../docs/tasks/04-mapa-de-handlers.md). "
        "Gerado por\n"
        "[`../tools/dump_published.py`](../tools/dump_published.py), a partir "
        f"de\n`{REL_EXE}` e dos 18 formulários de\n[`dfm/`](dfm/).\n"
        "**Não editar à mão** — correção entra no script e o arquivo é "
        "regerado:\n")
    add("```sh\npython3 wte/tools/dump_published.py\n"
        "python3 wte/tools/dump_published.py --check   # o que `make -C wte "
        "check` roda\n```\n")
    add(f"Os dados em forma de tabela estão em "
        f"[`{TSV_NAME}`]({TSV_NAME}); este arquivo é a\nleitura deles. **Todo "
        f"número daqui saiu do script**, inclusive os do texto corrido — é\n"
        f"por isso que o `--check` compara o markdown inteiro byte a byte, e "
        f"não só o TSV.\n")

    # ----------------------------------------------------------- método ---
    add("## O que foi medido, e com que régua\n")
    add(f"São **{total} métodos publicados** em "
        f"**{len([v for v in m.vmts if v.methods])} dos {len(m.vmts)} "
        f"formulários** — o mesmo número que a §1.4 do plano\nregistra. Eles "
        f"saem da *published method table* que o VCL guarda no VMT de cada\n"
        f"classe: a tabela que o streaming de DFM usa para resolver "
        f"`OnClick = boton_mcrClick`\nem ponteiro de código, e que sobreviveu "
        f"ao `/STRIP`.\n")
    add("### Achar os VMTs\n")
    add("O VMT que o Delphi/C++Builder emite é um array de métodos virtuais "
        "precedido de um\ncabeçalho de campos em deslocamento **negativo**, "
        "fixo desde o Delphi 4:\n")
    add("| Deslocamento | Campo | Uso aqui |")
    add("|---:|---|---|")
    add(f"| {VMT_SELF_PTR} | `vmtSelfPtr` | aponta para o próprio VMT — é a "
        f"assinatura da varredura |")
    add(f"| {VMT_METHOD_TABLE} | `vmtMethodTable` | a published method table "
        f"(0 quando não há nenhuma) |")
    add(f"| {VMT_CLASS_NAME} | `vmtClassName` | short string com o nome da "
        f"classe — a coluna `formulario` |")
    add(f"| {VMT_INSTANCE_SIZE} | `vmtInstanceSize` | validação |")
    add(f"| {VMT_PARENT} | `vmtParent` | — |")
    add("")
    add(f"Procurar o auto-ponteiro — dword cujo valor é o endereço dele mesmo "
        f"mais\n{-VMT_SELF_PTR} — localiza os VMTs sem depender de símbolo "
        f"nenhum. Em `.data` inteira a\nassinatura casa "
        f"{len(m.vmts) + m.rejected} vezes; "
        f"{m.rejected} {plural(m.rejected, 'é rejeitada', 'são rejeitadas')} "
        f"por ter `vmtClassName` nulo e\n`vmtInstanceSize` zero. Sobram os "
        f"**{len(m.vmts)}** formulários — um por arquivo de\n[`dfm/`](dfm/), "
        f"sem sobra dos dois lados. Essa bijeção é o fechamento que "
        f"substitui\nconfiar na varredura, e o script aborta se ela deixar de "
        f"valer.\n")
    add("A tabela em si é `word contagem` seguida de `contagem` entradas de\n"
        "`word tamanho`, `dword endereço`, `byte tamanho do nome`, nome. O "
        f"campo `tamanho`\ncobre a entrada inteira; o script confere "
        f"`tamanho == {METHOD_ENTRY_FIXED} + len(nome)` nas "
        f"{total},\nque o endereço cai dentro de `.text`, e que o nome é "
        f"identificador — e aborta na\nprimeira que discordar.\n")

    add("### Os 18 VMTs\n")
    add("| Formulário | Classe | VMT | `vmtInstanceSize` | tabela | métodos |")
    add("|---|---|---|---:|---|---:|")
    for vmt in m.vmts:
        table = f"`0x{vmt.table_va:08x}`" if vmt.table_va else "— *(nenhuma)*"
        add(f"| `{vmt.form}` | `{vmt.cls}` | `0x{vmt.va:08x}` | "
            f"{vmt.instance_size} | {table} | {len(vmt.methods)} |")
    add("")
    add(f"A classe é `T` + o nome do objeto raiz do `.dfm` nos "
        f"{len(m.vmts)} casos, e o script\naborta se algum dia não for: é "
        f"essa regra que deixa a coluna `formulario` do TSV\nusar o nome do "
        f"objeto (`MainForm`, `ficha_color`) em vez do nome da classe. O nome "
        f"do\nobjeto é o que nomeia o `.dfm`, a variável global do programa "
        f"original e a futura\nunidade Pascal — é a chave útil.\n")

    # --------------------------------------------------------- cruzamento ---
    add("## VMT × DFM\n")
    add(f"As duas fontes do dono, cruzadas em vez de escolhidas:\n")
    add("| Fonte | O que dá | Cobertura |")
    add("|---|---|---|")
    add(f"| VMT | `endereco`, `handler`, `formulario` | os {total}, "
        f"inclusive o que nenhum DFM cita |")
    add(f"| DFM | `componente`, `evento`; confere `formulario` | "
        f"{n_bind} ligações `On<Evento> = <handler>` |")
    add("")
    add(f"As {n_bind} ligações dos 18 `.dfm` se reduzem a "
        f"**{len(m.dfm_pairs)} pares (formulário, handler)\ndistintos**, e os "
        f"{len(m.dfm_pairs)} estão entre os {total} do VMT. **Zero "
        f"discordâncias de dono:**\nnenhum DFM referencia um handler "
        f"publicado por outra classe — o que era esperado,\nporque o "
        f"streaming do próprio original não acharia o método, e é por isso "
        f"que o\nscript trata esse caso como abortar e não como anotar.\n")
    add("A relação é de muitos para um: um handler serve vários componentes. "
        "Os campeões:\n")
    add("| Handler | Formulário | Componentes ligados | Evento |")
    add("|---|---|---:|---|")
    for row in sorted(m.rows, key=lambda r: (-len(r.bindings),
                                             r.method.addr))[:8]:
        events = sorted({b.event for b in row.bindings})
        add(f"| `{row.method.name}` | `{row.method.form}` | "
            f"{len(row.bindings)} | `{'`, `'.join(events)}` |")
    add("")
    add("No TSV as colunas `componente` e `evento` são listas separadas por "
        "`|`, do mesmo\ncomprimento e alinhadas por posição: o *n*-ésimo "
        "componente é ligado pelo *n*-ésimo\nevento. A ordem é a de "
        "aparecimento no `.dfm`.\n")

    titulo = plural(len(m.unreferenced), "O handler publicado",
                    "Os handlers publicados")
    add(f"### {titulo} que nenhum DFM referencia\n")
    if m.unreferenced:
        add("| Endereço | Handler | Formulário |")
        add("|---|---|---|")
        for row in m.unreferenced:
            add(f"| `0x{row.method.addr:08x}` | `{row.method.name}` | "
                f"`{row.method.form}` |")
        add("")
        add("Publicado no VMT, ligado a nenhum componente. As duas leituras "
            "possíveis são\ncódigo morto (o botão foi apagado do formulário e "
            "o método ficou) e ligação em\ntempo de execução "
            "(`Componente->OnClick = ...` em `FormCreate`). **Este script não "
            "as\nseparava** — quem separa é o disassembly do `FormCreate` de "
            "`MainForm`\n(`0x004107c8`), na fase 4. Fica marcado na coluna "
            "`nota` como\n`sem referencia em DFM`.\n")
    else:
        add("Nenhum: todos os métodos publicados têm ao menos uma ligação de "
            "DFM.\n")

    add("### Homônimos — por que a coluna `formulario` existe\n")
    add(f"{len(homonyms)} nomes aparecem em mais de um formulário, cobrindo "
        f"{sum(len(v) for v in homonyms.values())} dos {total} métodos. Sem o "
        f"dono,\n\"implementar `FormCreate`\" não quer dizer nada:\n")
    add("| Handler | Vezes | Formulários |")
    add("|---|---:|---|")
    for name in sorted(homonyms, key=lambda n: (-len(homonyms[n]), n)):
        forms = homonyms[name]
        add(f"| `{name}` | {len(forms)} | `{'`, `'.join(sorted(forms))}` |")
    add("")

    # ------------------------------------------------------ classificacao ---
    add("## A coluna `grupo`\n")
    add("`grupo` é o que reparte os 96 entre as quatro tasks da fase 4. O "
        "enunciado da\nWTE-TASK-04 a chama de \"classificação manual\", mas "
        "saída de gerador tem de ser\nreproduzível: aqui ela sai de **oito "
        "regras ordenadas** mais uma **tabela de\nexceções**, ambas no topo "
        f"do script. A coluna `regra` do TSV diz qual decidiu cada\nlinha "
        f"(`EX` = exceção), então discordar de uma classificação é editar uma "
        f"linha\nidentificável, não reabrir um julgamento.\n")
    add("| Grupo | Task | Quantos |")
    add("|---|---|---:|")
    for g in GROUPS:
        task, href = GROUP_TASK[g]
        add(f"| {GROUP_LABEL[g]} | [{task}]({href}) | {m.distribution[g]} |")
    add(f"| **total** | | **{total}** |")
    add("")

    add("### As oito regras, na ordem em que são tentadas\n")
    add("A primeira que casa decide; a tabela de exceções vem antes de "
        "todas.\n")
    add("| Regra | Grupo | Critério | Handlers |")
    add("|---|---|---|---:|")
    used = {}
    for row in m.rows:
        used[row.rule] = used.get(row.rule, 0) + 1
    add(f"| `EX` | — | tabela de exceções | {used.get('EX', 0)} |")
    for rule_id, group, why, _ in _rules():
        add(f"| `{rule_id}` | {GROUP_LABEL[group]} | {why} | "
            f"{used.get(rule_id, 0)} |")
    add("")
    add("Duas das regras não são adivinhação de nome, e sim medida do "
        "binário:\n")
    add(f"- **R6** usa as **{len(m.dialogs)} unidades exportadas**. O "
        f"C++Builder exporta\n  `@@T<unidade>@Initialize` para cada unidade "
        f"com inicialização a emitir; as telas\n  grandes não têm e por isso "
        f"não aparecem. É o mesmo corte da §1.3 do plano, e é\n  exatamente o "
        f"que a WTE-TASK-28 chama de \"os 13 diálogos\": "
        + ", ".join(f"`{d}`" for d in m.dialogs) + ".\n"
        "- **R7** usa o nome que a IDE gera sozinha (`BitBtn1Click`, "
        "`SpeedButton2Click`,\n  `Image3Click`). Componente que o autor nunca "
        "renomeou é botão de moldura —\n  abrir, fechar, OK/Cancelar —, e é "
        "assim que a WTE-TASK-28 já os enumera.\n")

    add(f"### As {len(EXCEPTIONS)} exceções\n")
    add("| Formulário | Handler | Grupo | Por quê |")
    add("|---|---|---|---|")
    for (form, handler) in sorted(EXCEPTIONS):
        group, why = EXCEPTIONS[(form, handler)]
        add(f"| `{form}` | `{handler}` | {GROUP_LABEL[group]} | {why} |")
    add("")

    add("### Conferência contra a §1.4 do plano\n")
    add("A §1.4 já interpretou dez handlers a olho. Todos os dez caem onde a "
        "leitura dela\nmanda, o que é a âncora de sanidade das regras:\n")
    anchors = [
        ("boton_mcrClick", "abre o `.mcr`"),
        ("boton_mcr2isoClick", "grava o jogador do `.mcr` na imagem"),
        ("grabar_camisetaClick", "grava a camisa editada"),
        ("grabar_memoryClick", "grava para memory card"),
        ("etiqprecioClick", "calcula preço do jogador"),
        ("colorearClick", "pinta camisa/bandeira"),
        ("lista_equiposChange", "carrega time selecionado"),
        ("lista_formacionesClick", "aplica formação"),
        ("ComboBoxDrawItem", "owner-draw do combo"),
        ("malla2MouseDown", "grade do editor de camisa"),
    ]
    add("| Handler | Leitura da §1.4 | Formulário medido | `grupo` | `regra` |")
    add("|---|---|---|---|---|")
    for name, gloss in anchors:
        rows = [r for r in m.rows if r.method.name == name]
        for row in rows:
            add(f"| `{name}` | {gloss} | `{row.method.form}` | "
                f"{GROUP_LABEL[row.group]} | `{row.rule}` |")
    add("")
    add("Duas ressalvas de leitura, não de medida:\n")
    add("- `lista_formacionesClick` é **carga** porque a WTE-TASK-25 o "
        "reivindica, mas a\n  própria tarefa avisa que ele \"aplica formação "
        "sobre o time selecionado — é ação\n  destrutiva disparada por "
        "clique\". Se a fase 4 preferir movê-lo para edição, o\n  lugar de "
        "mudar é a tabela de exceções.\n"
        "- `etiqprecioClick` é **edição** por eliminação: ele calcula e "
        "mostra o preço, não\n  carrega nem grava, e não há um quinto grupo. "
        "A coluna `nota` o marca como\n  `WTE-TASK-30`.\n")

    add(f"### Os {len(FORMULA_OWNERS)} handlers que a WTE-TASK-28 devolve às "
        f"tasks 30 e 32\n")
    add("A WTE-TASK-28 exclui do próprio escopo os handlers de `ficha_color` "
        "e de `jugador`\nque são **fórmula**, não diálogo. Eles continuam com "
        "`grupo` entre os quatro — não\nexiste um quinto —, e a coluna `nota` "
        "diz quem os implementa, para que a fase 4 não\nfaça o trabalho duas "
        "vezes:\n")
    add("| Endereço | Handler | Formulário | `grupo` | `nota` |")
    add("|---|---|---|---|---|")
    for row in m.rows:
        tags = [n for n in row.note if n.startswith("WTE-TASK-")]
        if tags:
            add(f"| `0x{row.method.addr:08x}` | `{row.method.name}` | "
                f"`{row.method.form}` | {GROUP_LABEL[row.group]} | "
                f"{', '.join(tags)} |")
    add("")

    # --------------------------------------------------------- os 96 ---
    add(f"## Os {total}, por endereço\n")
    add("A ordem é a do TSV: endereço crescente, que é a ordem em que o "
        "linker dispôs o\ncódigo. A coluna *componentes* é a contagem de "
        "ligações de DFM; a lista completa\nestá no TSV.\n")
    add("| Endereço | Handler | Formulário | Evento | Componentes | Grupo |")
    add("|---|---|---|---|---:|---|")
    for row in m.rows:
        events = sorted({b.event for b in row.bindings})
        ev = "`" + "`, `".join(events) + "`" if events else "—"
        add(f"| `0x{row.method.addr:08x}` | `{row.method.name}` | "
            f"`{row.method.form}` | {ev} | {len(row.bindings)} | "
            f"{GROUP_LABEL[row.group]} |")
    add("")

    # ------------------------------------------------------- correcoes ---
    add("## Onde o plano e as tarefas envelheceram\n")
    add("Tudo abaixo é contagem do script contra texto já escrito. Nenhuma "
        "delas muda uma\nconclusão; todas mudam um número que alguém usaria "
        "para se conferir.\n")
    add("A coluna **Diz** cita o texto como ele estava quando a WTE-TASK-04 "
        "mediu. A\n[CORR-WTE-006](../../docs/tasks/CORR-WTE-006.md) propagou "
        "estas linhas para os\narquivos citados, então a citação já não é o "
        "que se lê lá — é o registro do que\nfoi corrigido, e envelhece "
        "junto. Quem decide se a seção inteira vira histórico\nao fechar a "
        "fase 1 é a WTE-TASK-09.\n")
    counts = count_by_name(m)
    form_create = len(counts.get("FormCreate", []))
    form_show = len(counts.get("FormShow", []))
    bitbtn1 = len(counts.get("BitBtn1Click", []))
    add("| Onde | Diz | Medido |")
    add("|---|---|---|")
    # Atribuicao pelo arquivo que carrega a frase, nao pelo que se supoe.
    # O "17" nunca esteve no plano: esta na task 04 e no prompt de revisao --
    # e o do prompt reprovaria um dfm2lfm.py correto na fase 2.
    add(f"| WTE-TASK-04 e `docs/prompts/02-revisar.md` | `FormCreate` aparece "
        f"**17** vezes | **{form_create}** — `ficha_error` e `ficha_error2` "
        f"não têm |")
    add(f"| WTE-TASK-04 | `BitBtn1Click` **duas** | **{bitbtn1}** — "
        + ", ".join(f"`{f}`" for f in sorted(counts['BitBtn1Click'])) + " |")
    add(f"| WTE-TASK-25 | `FormCreate` / `FormShow` — **19 endereços** | "
        f"**{form_create + form_show}** = {form_create} `FormCreate` + "
        f"{form_show} `FormShow` |")
    etiq = next(r for r in m.rows if r.method.name == "etiqprecioClick")
    for onde in ("§5.1 do plano", "WTE-TASK-30"):
        add(f"| {onde} | `etiqprecioClick` e o formulário "
            f"`ficha_creditos_equipo` | o dono é **`{etiq.method.form}`**; "
            f"`ficha_creditos_equipo` só publica `FormCreate` |")
    malla = sorted({r.method.form for r in m.rows
                    if r.method.name.startswith("malla")})
    add(f"| WTE-TASK-28 | `malla1MouseDown` / `malla2MouseDown` pertencem a "
        f"`ficha_color` e `ficha_creditos_equipo` | o dono é "
        + ", ".join(f"**`{f}`**" for f in malla) + " |")
    # Os dez nomes que a 28 chama de "repetidos", julgados pela contagem
    # medida em vez de um a um a mao.
    unicos = [n for n in TASK28_REPEATED if len(counts[n]) == 1]
    add(f"| WTE-TASK-28 | `{unicos[0]}` e mais "
        f"{len(unicos) - 1} entre os \"handlers repetidos por vários "
        f"formulários\" | aparecem **uma vez cada**: "
        + ", ".join(f"`{n}` (`{counts[n][0]}`)" for n in unicos) + " |")
    add(f"| WTE-TASK-28 | `BitBtn1Click` (**3×**) na mesma lista | "
        f"**{bitbtn1}×** |")
    ficha = sorted({v.form for v in m.vmts if v.form.startswith("ficha_")})
    add(f"| WTE-TASK-28 | \"os **13** diálogos\", e o escopo lista **"
        f"{len(ficha)}** formulários `ficha_*` | os 13 são as **unidades "
        f"exportadas**; `ficha_color` e `ficha_error` são telas grandes e "
        f"ficam de fora deles |")
    add("")
    add("Duas observações que não são correção, e sim coisa que ninguém "
        "tinha contado:\n")
    err2 = next(v for v in m.vmts if v.form == "ficha_error2")
    add(f"- **`{err2.form}` não publica nenhum método** (`vmtMethodTable` = "
        f"0) e o `.dfm` dele não\n  tem uma ligação de evento sequer. É o "
        f"único formulário do binário nessa situação:\n  aparece, e nada "
        f"acontece nele.\n")
    if m.unreferenced:
        u = m.unreferenced[0]
        add(f"- **`{u.method.name}`** (`{u.method.form}`, "
            f"`0x{u.method.addr:08x}`) é o único dos {total} sem ligação de\n"
            f"  DFM — ver a seção do cruzamento.\n")

    # ------------------------------------------------------- ressalvas ---
    add("## Ressalvas\n")
    add("- **A coluna `grupo` é ordenação de trabalho, não fato do binário.** "
        "As outras\n  colunas são medidas; esta é regra escrita, e as regras "
        "estão no script justamente\n  para poderem ser discutidas e "
        "reexecutadas.\n"
        "- **Nada aqui foi decompilado.** O que se leu do `.exe` foram "
        "estruturas de dados —\n  VMT, tabela de métodos, tabela de "
        "exportação — e nomes. Nenhuma instrução foi\n  interpretada, e "
        "nenhum byte do binário foi copiado para cá: no espírito da §2 do\n  "
        "plano, isto é recuperação de especificação, não transcrição.\n"
        "- **\"Sem referência em DFM\" não quer dizer \"morto\".** Ligação "
        "feita em tempo de\n  execução tem exatamente a mesma aparência aqui. "
        "Separar é da fase 4.\n"
        "- **Os nomes vêm verbatim do binário**, inclusive a inconsistência "
        "de caixa\n  (`lista_col1change` contra `lista_col0Change`). "
        "Normalizar criaria um nome que não\n  existe em lugar nenhum.\n")
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
    if not DFM.is_dir():
        raise DumpError(
            f"{REL_DFM} nao existe. Rode antes: python3 "
            f"wte/tools/dfm_extract.py")
    paths = sorted(DFM.glob("*.dfm"))
    if not paths:
        raise DumpError(f"{REL_DFM} nao tem nenhum .dfm")

    forms: dict[str, list[Binding]] = {}
    for path in paths:
        form, bindings = parse_dfm(path)
        if form in forms:
            raise DumpError(f"{REL_DFM}: formulario {form} duas vezes")
        forms[form] = bindings

    img = Image(EXE.read_bytes())
    m = Measurement(img, forms)
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
        print(f"{REL_OUT} nao corresponde a {REL_EXE} + {REL_DFM}:",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivos em dia com {REL_EXE} + {REL_DFM}")
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
