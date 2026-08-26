#!/usr/bin/env python3
"""Extrai os 18 formularios DFM do `.rsrc` do we-team-editor.exe (WTE-TASK-03).

O editor do Obocaman e um binario C++Builder 6: cada formulario da aplicacao
vive em `.rsrc` como um recurso `RT_RCDATA` cujo nome e o nome da classe em
maiusculas (`TMAINFORM`, `TFICHA_ABOUT`, ...) e cujo conteudo e um stream DFM
binario comecando por `TPF0`. Este script le o `.exe`, decodifica os 18 streams
e escreve o equivalente textual em `wte/re/dfm/`.

    python3 wte/tools/dfm_extract.py            # gera
    python3 wte/tools/dfm_extract.py --check    # regera em memoria e compara

Leitura pura: o `.exe` nunca e aberto para escrita.


Blobs binarios: ARQUIVO LATERAL, nao hex inline
-----------------------------------------------

Sao 118 propriedades `vaBinary` (`Icon.Data`, o `Picture.Data` dos 45 `TImage`,
o `Glyph.Data` dos 28 `TSpeedButton`) somando 798 KiB. Inline em hex, como o
DFM/LFM textual faz, isso viraria ~1,6 MiB de texto **versionado**.

A decisao foi arquivo lateral, por causa da secao 2 do plano. Esses 118 blobs
sao a arte do Obocaman, da mesma natureza dos 198 `.bmp` que estao em
`we-team-editor/` -- pasta que este repositorio ignora exatamente por isso
("binario sem fonte e sem licenca nao entra no repositorio", wte/README.md).
Hex e so uma codificacao: colar os bytes em `wte/re/dfm/*.dfm` reintroduziria
no versionamento aquilo que o `.gitignore` mantem fora dele. O que interessa a
fase 2 e a *estrutura* dos formularios -- isso sim e especificacao, e isso sim
fica versionado.

No lugar do hex, o `.dfm` versionado guarda uma referencia com tamanho e
SHA-256 do blob:

    Glyph.Data = {blob SpeedButton1.Glyph.Data.bin 1078 sha256:1a2b...}

Consequencias, todas deliberadas:

- os bytes ficam **preservados, nao resumidos**: `blobs/<form>/<arquivo>.bin`
  contem o blob integral, extraido do `.exe` a cada execucao;
- `--check` continua verificando os 798 KiB byte a byte, pelo SHA-256 que esta
  no `.dfm` -- versionar o hash e o que substitui versionar os bytes;
- `blobs/` e ignorado pelo git e renasce do `.exe`, como `wte/assets` -- mas so
  no **modo de escrita**. `--check` nao materializa nada: blob ausente e o
  estado normal de um clone limpo, e sai como aviso, nao como divergencia.
  Blob presente e diferente do `.exe`, ou blob sobrando, continuam falha;
- o `{...}` com texto nao-hexadecimal faz um leitor de DFM padrao **falhar** ao
  encontrar a referencia, em vez de aceitar lixo em silencio. E o desfecho
  desejado: quem consumir isto tem de saber o que esta lendo.

O `dfm2lfm.py` da WTE-TASK-10 resolve a referencia lendo o `.bin` ao lado.


Formato do texto
----------------

DFM textual padrao (`ObjectBinaryToText`): indentacao de 2 espacos,
`object Nome: TClasse` ... `end`, `[a, b]` para conjuntos, `(...)` para listas,
`<item ... end>` para colecoes, string entre aspas simples com `''` escapando a
aspa e `#NN` para byte nao imprimivel. A unica divergencia e a referencia de
blob descrita acima.

Os 18 streams nao tem um unico byte fora de ASCII imprimivel em string,
identificador ou nome de propriedade -- a saida e ASCII puro por construcao, e
o script aborta se algum dia deixar de ser. Isso tira a questao de codificacao
do caminho: nada de cp1252 contra UTF-8 na fronteira com a fase 2.


Nome do arquivo de saida
------------------------

`<nome do objeto raiz>.dfm`, verbatim -- `MainForm.dfm`, `ficha_about.dfm`. O
nome do objeto e o nome da variavel global do formulario no programa original,
unico por construcao. Nao ha transformacao (nem minusculas, nem prefixo): o
nome e dado recuperado do binario e transforma-lo so cria uma segunda
convencao para manter. A unicidade e conferida em tempo de geracao, sem
distinguir maiusculas, e a colisao aborta.


Falha alta
----------

`TValueType` desconhecido, tamanho negativo ou fim de stream inesperado abortam
com o **offset absoluto no arquivo**, o formulario e o caminho do objeto ate a
propriedade. Nenhuma excecao e engolida e nenhum formulario parcial e escrito:
a saida so vai para o disco depois que os 18 decodificam inteiros.
"""

from __future__ import annotations

import hashlib
import math
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
OUT = ROOT / "wte" / "re" / "dfm"
BLOBS = OUT / "blobs"

# Caminhos relativos usados nas mensagens -- nada de caminho absoluto na saida.
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_OUT = "wte/re/dfm"
GENERATOR = "wte/tools/dfm_extract.py"

RT_RCDATA = 10

# TValueType, na ordem em que o Delphi/C++Builder a declara em classes.pas. Os
# 21 sao tratados; os que nao aparecem nestes 18 formularios (marcados) ficam
# implementados assim mesmo -- o custo e baixo e o alternativo seria abortar
# num binario vizinho por falta de tres linhas.
(VA_NULL, VA_LIST, VA_INT8, VA_INT16, VA_INT32, VA_EXTENDED, VA_STRING,
 VA_IDENT, VA_FALSE, VA_TRUE, VA_BINARY, VA_SET, VA_LSTRING, VA_NIL,
 VA_COLLECTION, VA_SINGLE, VA_CURRENCY, VA_DATE, VA_WSTRING, VA_INT64,
 VA_UTF8STRING) = range(21)

VA_NAMES = [
    "vaNull", "vaList", "vaInt8", "vaInt16", "vaInt32", "vaExtended",
    "vaString", "vaIdent", "vaFalse", "vaTrue", "vaBinary", "vaSet",
    "vaLString", "vaNil", "vaCollection", "vaSingle", "vaCurrency", "vaDate",
    "vaWString", "vaInt64", "vaUTF8String",
]

# Flags do prefixo de objeto (TFilerFlags). O byte so existe quando o nibble
# alto e 0xF -- nome de classe com 240+ caracteres nao acontece, que e o truque
# que o proprio Delphi usa para desambiguar.
FF_INHERITED = 0x01
FF_CHILD_POS = 0x02
FF_INLINE = 0x04


class DfmError(Exception):
    """Erro de decodificacao, sempre com offset absoluto e contexto."""


# --------------------------------------------------------------------- PE ---
#
# Leitor de recursos em stdlib pura. `pefile` daria o mesmo resultado, mas o
# que este script precisa do PE cabe em 60 linhas -- e sem dependencia o
# `make -C wte check` roda em qualquer maquina com Python 3.


def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def read_rcdata(exe: bytes) -> list[tuple[str, int, bytes]]:
    """Devolve [(nome do recurso, offset no arquivo, bytes)] dos RT_RCDATA.

    A ordem e a da arvore de recursos, que o linker mantem ordenada por nome --
    determinismo de graca.
    """
    if exe[:2] != b"MZ":
        raise DfmError(f"{REL_EXE}: nao comeca com 'MZ'")
    pe_off = _u32(exe, 0x3C)
    if exe[pe_off:pe_off + 4] != b"PE\0\0":
        raise DfmError(f"{REL_EXE}: assinatura PE ausente em {pe_off:#x}")

    coff = pe_off + 4
    n_sections = _u16(exe, coff + 2)
    size_opt = _u16(exe, coff + 16)
    opt = coff + 20
    magic = _u16(exe, opt)
    if magic != 0x10B:
        raise DfmError(f"{REL_EXE}: esperado PE32 (0x10b), veio {magic:#x}")
    # NumberOfRvaAndSizes fica em +92 no optional header PE32; o diretorio de
    # recursos e a entrada 2 do array que comeca em +96.
    n_dirs = _u32(exe, opt + 92)
    if n_dirs < 3:
        raise DfmError(f"{REL_EXE}: sem diretorio de recursos")
    res_rva = _u32(exe, opt + 96 + 2 * 8)
    if res_rva == 0:
        raise DfmError(f"{REL_EXE}: diretorio de recursos vazio")

    sections = []
    sec = opt + size_opt
    for i in range(n_sections):
        s = sec + i * 40
        sections.append((_u32(exe, s + 12), _u32(exe, s + 16), _u32(exe, s + 20)))

    def rva_to_off(rva: int) -> int:
        for va, raw_size, raw_ptr in sections:
            if va <= rva < va + raw_size:
                return raw_ptr + (rva - va)
        raise DfmError(f"{REL_EXE}: RVA {rva:#x} fora de qualquer secao")

    base = rva_to_off(res_rva)

    def entries(dir_off: int) -> list[tuple[str | int, int, bool]]:
        named = _u16(exe, dir_off + 12)
        ids = _u16(exe, dir_off + 14)
        out = []
        for i in range(named + ids):
            e = dir_off + 16 + i * 8
            name_field = _u32(exe, e)
            data_field = _u32(exe, e + 4)
            if name_field & 0x80000000:
                s = base + (name_field & 0x7FFFFFFF)
                length = _u16(exe, s)
                name: str | int = exe[s + 2:s + 2 + length * 2].decode("utf-16-le")
            else:
                name = name_field
            out.append((name, data_field & 0x7FFFFFFF,
                        bool(data_field & 0x80000000)))
        return out

    found: list[tuple[str, int, bytes]] = []
    for type_name, type_off, is_dir in entries(base):
        if type_name != RT_RCDATA or not is_dir:
            continue
        for res_name, name_off, name_is_dir in entries(base + type_off):
            if not name_is_dir:
                continue
            for _lang, lang_off, lang_is_dir in entries(base + name_off):
                if lang_is_dir:
                    continue
                data_rva = _u32(exe, base + lang_off)
                size = _u32(exe, base + lang_off + 4)
                off = rva_to_off(data_rva)
                found.append((str(res_name), off, exe[off:off + size]))
    return found


# ---------------------------------------------------------------- leitura ---


class Reader:
    """Leitor do stream DFM, com offset absoluto para as mensagens de erro."""

    def __init__(self, data: bytes, base: int, form: str):
        self.data = data
        self.pos = 0
        self.base = base          # offset do stream dentro do .exe
        self.form = form
        # Duas pilhas, nao uma: a de objetos da o contexto do erro, a de
        # propriedades batiza o arquivo do blob. Juntas num unico `path`, o
        # nome do blob sairia com o dono repetido.
        self.obj_path: list[str] = []
        self.prop_path: list[str] = []

    # -- diagnostico ------------------------------------------------------

    def fail(self, msg: str, at: int | None = None) -> "DfmError":
        where = self.base + (self.pos if at is None else at)
        trail = " > ".join(self.obj_path + self.prop_path) or "(raiz)"
        return DfmError(
            f"{REL_EXE}+{where} (0x{where:x}): {self.form}: {trail}: {msg}")

    def take(self, n: int) -> bytes:
        if n < 0:
            raise self.fail(f"tamanho negativo ({n})")
        if self.pos + n > len(self.data):
            raise self.fail(
                f"fim do stream: pedidos {n} bytes, restam "
                f"{len(self.data) - self.pos}")
        out = self.data[self.pos:self.pos + n]
        self.pos += n
        return out

    # -- primitivos -------------------------------------------------------

    def byte(self) -> int:
        return self.take(1)[0]

    def peek(self) -> int:
        if self.pos >= len(self.data):
            raise self.fail("fim do stream ao espiar o proximo byte")
        return self.data[self.pos]

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def short_str(self) -> bytes:
        return self.take(self.byte())

    def long_str(self) -> bytes:
        return self.take(self.i32())

    def ascii(self, raw: bytes, what: str) -> str:
        for c in raw:
            if not 0x20 <= c <= 0x7E:
                raise self.fail(
                    f"{what} com byte fora de ASCII imprimivel ({c:#04x}): "
                    f"{raw!r}")
        return raw.decode("ascii")

    def integer(self) -> int:
        """ReadInteger: aceita so os tres tamanhos inteiros."""
        t = self.byte()
        if t == VA_INT8:
            return struct.unpack("<b", self.take(1))[0]
        if t == VA_INT16:
            return struct.unpack("<h", self.take(2))[0]
        if t == VA_INT32:
            return self.i32()
        raise self.fail(f"esperado inteiro, veio {va_name(t)}", self.pos - 1)


def va_name(t: int) -> str:
    return VA_NAMES[t] if 0 <= t < len(VA_NAMES) else f"tipo desconhecido {t}"


# ------------------------------------------------------------- estruturas ---


class Blob:
    """Uma propriedade vaBinary, guardada fora do .dfm."""

    __slots__ = ("filename", "data", "sha256")

    def __init__(self, filename: str, data: bytes):
        self.filename = filename
        self.data = data
        self.sha256 = hashlib.sha256(data).hexdigest()

    def reference(self) -> str:
        return f"{{blob {self.filename} {len(self.data)} sha256:{self.sha256}}}"


class Obj:
    __slots__ = ("cls", "name", "flags", "child_pos", "props", "children")

    def __init__(self, cls: str, name: str, flags: int, child_pos: int | None):
        self.cls = cls
        self.name = name
        self.flags = flags
        self.child_pos = child_pos
        self.props: list[tuple[str, object]] = []
        self.children: list[Obj] = []


class CollectionItem:
    __slots__ = ("index", "props")

    def __init__(self, index: int | None):
        self.index = index
        self.props: list[tuple[str, object]] = []


# Envelopes para os valores que precisam de forma propria no texto.
class Ident(str):
    pass


class Float(float):
    pass


class SetValue(list):
    pass


class ListValue(list):
    pass


class Collection(list):
    pass


class Nil:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst


# ------------------------------------------------------------- decodifica ---


def extended(raw: bytes) -> float:
    """Converte o extended de 80 bits do x87 (10 bytes, little endian)."""
    mantissa = int.from_bytes(raw[:8], "little")
    sign_exp = int.from_bytes(raw[8:10], "little")
    sign = -1.0 if sign_exp & 0x8000 else 1.0
    exp = sign_exp & 0x7FFF
    if exp == 0x7FFF:
        return sign * (math.inf if mantissa in (0, 1 << 63) else math.nan)
    if exp == 0 and mantissa == 0:
        return sign * 0.0
    return sign * math.ldexp(mantissa, exp - 16383 - 63)


def read_value(r: Reader, blobs: "BlobSink"):
    at = r.pos
    t = r.byte()

    if t == VA_NULL:
        raise r.fail("vaNull onde se esperava um valor", at)
    if t == VA_LIST:
        items = ListValue()
        while r.peek() != VA_NULL:
            items.append(read_value(r, blobs))
        r.byte()
        return items
    if t == VA_INT8:
        return struct.unpack("<b", r.take(1))[0]
    if t == VA_INT16:
        return struct.unpack("<h", r.take(2))[0]
    if t == VA_INT32:
        return r.i32()
    if t == VA_EXTENDED:
        return Float(extended(r.take(10)))
    if t == VA_STRING:
        return r.short_str()
    if t == VA_IDENT:
        return Ident(r.ascii(r.short_str(), "identificador"))
    if t == VA_FALSE:
        return False
    if t == VA_TRUE:
        return True
    if t == VA_BINARY:
        return blobs.add(r.long_str())
    if t == VA_SET:
        items = SetValue()
        while True:
            raw = r.short_str()
            if not raw:
                break
            items.append(r.ascii(raw, "elemento de conjunto"))
        return items
    if t == VA_LSTRING:
        return r.long_str()
    if t == VA_NIL:
        return Nil()
    if t == VA_COLLECTION:
        coll = Collection()
        while r.peek() != VA_NULL:
            index = r.integer() if r.peek() in (VA_INT8, VA_INT16, VA_INT32) \
                else None
            marker_at = r.pos
            marker = r.byte()
            if marker != VA_LIST:
                raise r.fail(
                    f"esperado vaList abrindo o item da colecao, veio "
                    f"{va_name(marker)}", marker_at)
            item = CollectionItem(index)
            while r.peek() != VA_NULL:
                item.props.append(read_property(r, blobs))
            r.byte()
            coll.append(item)
        r.byte()
        return coll
    if t == VA_SINGLE:
        return Float(struct.unpack("<f", r.take(4))[0])
    if t == VA_CURRENCY:
        return Float(struct.unpack("<q", r.take(8))[0] / 10000.0)
    if t == VA_DATE:
        return Float(struct.unpack("<d", r.take(8))[0])
    if t == VA_WSTRING:
        # Nenhum dos 18 formularios tem WideString. Se um binario vizinho
        # tiver, a parte ASCII passa e o resto aborta: inventar aqui uma
        # convencao de escape para UTF-16 sem ter um caso real para conferir
        # daria uma saida plausivel e errada.
        text = r.take(r.i32() * 2).decode("utf-16-le")
        for ch in text:
            if not 0x20 <= ord(ch) <= 0x7E:
                raise r.fail(
                    f"vaWString com caractere fora de ASCII imprimivel "
                    f"(U+{ord(ch):04X}). A forma textual disso nao foi "
                    f"decidida -- nao ocorre nos 18 formularios.", at)
        return text.encode("ascii")
    if t == VA_INT64:
        return struct.unpack("<q", r.take(8))[0]
    if t == VA_UTF8STRING:
        return r.long_str()

    raise r.fail(
        f"TValueType desconhecido: {t} (0x{t:02x}). Os validos vao de 0 "
        f"(vaNull) a 20 (vaUTF8String).", at)


def read_property(r: Reader, blobs: "BlobSink") -> tuple[str, object]:
    name = r.ascii(r.short_str(), "nome de propriedade")
    r.prop_path.append(name)
    try:
        value = read_value(r, blobs)
    finally:
        r.prop_path.pop()
    return name, value


def read_object(r: Reader, blobs: "BlobSink") -> Obj:
    flags = 0
    child_pos = None
    if (r.peek() & 0xF0) == 0xF0:
        flags = r.byte() & 0x0F
        if flags & FF_CHILD_POS:
            child_pos = r.integer()
    cls = r.ascii(r.short_str(), "nome de classe")
    name = r.ascii(r.short_str(), "nome de objeto")

    obj = Obj(cls, name, flags, child_pos)
    r.obj_path.append(name or cls)
    try:
        while r.peek() != VA_NULL:
            obj.props.append(read_property(r, blobs))
        r.byte()
        while r.peek() != VA_NULL:
            obj.children.append(read_object(r, blobs))
        r.byte()
    finally:
        r.obj_path.pop()
    return obj


class BlobSink:
    """Coleta os vaBinary e batiza cada um com o dono e a propriedade.

    O nome do componente e unico dentro do formulario (o Delphi o publica como
    campo da classe), entao `<dono>.<propriedade>.bin` nao colide. A colisao e
    conferida assim mesmo -- e barata e o alternativo e um blob sobrescrever o
    outro em silencio.
    """

    def __init__(self, r: Reader):
        self.r = r
        self.items: list[Blob] = []
        self._seen: dict[str, str] = {}

    def add(self, data: bytes) -> Blob:
        owner = self.r.obj_path[-1]
        prop = ".".join(self.r.prop_path)
        filename = f"{owner}.{prop}.bin"
        key = filename.lower()
        if key in self._seen:
            raise self.r.fail(f"dois blobs disputam o arquivo {filename}")
        self._seen[key] = filename
        blob = Blob(filename, data)
        self.items.append(blob)
        return blob


def parse_form(res_name: str, offset: int, data: bytes) -> tuple[Obj, list[Blob]]:
    r = Reader(data, offset, res_name)
    magic = r.take(4)
    if magic != b"TPF0":
        raise r.fail(f"esperado 'TPF0', veio {magic!r}", 0)
    blobs = BlobSink(r)
    root = read_object(r, blobs)
    if r.pos != len(data):
        raise r.fail(
            f"sobraram {len(data) - r.pos} bytes depois do fim do formulario")
    return root, blobs.items


# ------------------------------------------------------------------ texto ---


def quote(raw: bytes) -> str:
    """String no formato DFM: trechos entre aspas simples e `#NN` para o resto."""
    parts: list[str] = []
    run: list[str] = []
    for c in raw:
        if 0x20 <= c <= 0x7E:
            run.append("''" if c == 0x27 else chr(c))
        else:
            if run:
                parts.append("'" + "".join(run) + "'")
                run = []
            parts.append(f"#{c}")
    if run:
        parts.append("'" + "".join(run) + "'")
    return "".join(parts) if parts else "''"


def fmt_float(v: float) -> str:
    if math.isnan(v):
        return "NaN"
    if math.isinf(v):
        return "Inf" if v > 0 else "-Inf"
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return repr(v)


def emit_value(value, indent: int, out: list[str]) -> None:
    """Anexa a representacao do valor. `out` ja termina com ' = '."""
    pad = " " * indent
    if isinstance(value, Blob):
        out.append(value.reference())
    elif isinstance(value, bool):
        out.append("True" if value else "False")
    elif isinstance(value, Ident):
        out.append(str(value))
    elif isinstance(value, Nil):
        out.append("nil")
    elif isinstance(value, Float):
        out.append(fmt_float(value))
    elif isinstance(value, int):
        out.append(str(value))
    elif isinstance(value, bytes):
        out.append(quote(value))
    elif isinstance(value, SetValue):
        out.append("[" + ", ".join(value) + "]")
    elif isinstance(value, ListValue):
        out.append("(")
        for item in value:
            out.append(f"\n{pad}  ")
            emit_value(item, indent + 2, out)
        out.append(")")
    elif isinstance(value, Collection):
        out.append("<")
        for item in value:
            head = "item" if item.index is None else f"item [{item.index}]"
            out.append(f"\n{pad}  {head}")
            for name, sub in item.props:
                out.append(f"\n{pad}    {name} = ")
                emit_value(sub, indent + 4, out)
            out.append(f"\n{pad}  end")
        out.append(">")
    else:  # pragma: no cover -- so acontece se read_value ganhar um tipo novo
        raise DfmError(f"valor sem forma textual definida: {value!r}")


def emit_object(obj: Obj, indent: int, out: list[str]) -> None:
    pad = " " * indent
    kind = "object"
    if obj.flags & FF_INHERITED:
        kind = "inherited"
    elif obj.flags & FF_INLINE:
        kind = "inline"
    head = f"{pad}{kind} "
    if obj.name:
        head += f"{obj.name}: "
    head += obj.cls
    if obj.child_pos is not None:
        head += f" [{obj.child_pos}]"
    out.append(head + "\n")

    for name, value in obj.props:
        line: list[str] = [f"{pad}  {name} = "]
        emit_value(value, indent + 2, line)
        out.append("".join(line) + "\n")
    for child in obj.children:
        emit_object(child, indent + 2, out)
    out.append(f"{pad}end\n")


def render(root: Obj) -> str:
    out: list[str] = []
    emit_object(root, 0, out)
    text = "".join(out)
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:  # pragma: no cover
        raise DfmError(f"{root.name}.dfm: saida deixou de ser ASCII: {exc}")
    return text


# ------------------------------------------------------------------ censo ---


def census(root: Obj) -> Counter:
    counts: Counter = Counter()

    def walk(o: Obj) -> None:
        for child in o.children:
            counts[child.cls] += 1
            walk(child)

    walk(root)
    return counts


def order(counts: Counter) -> list[tuple[str, int]]:
    """Ordem estavel: mais frequente primeiro, empate pelo nome."""
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def render_census(forms: list[tuple[str, Obj, list[Blob]]]) -> str:
    total: Counter = Counter()
    lines: list[str] = []
    lines.append("# Censo de componentes dos 18 formularios\n")
    lines.append(
        f"Gerado por `{GENERATOR}` a partir de `{REL_EXE}`.\n"
        "**Nao editar a mao** -- correcao entra no script e o diretorio e "
        "regerado.\n")
    lines.append(
        "A contagem e de **componentes**: o objeto raiz de cada formulario "
        "(a\nclasse `T<nome>`) fica de fora, porque ele e o formulario, nao "
        "um componente\ndentro dele.\n")

    lines.append("## Blobs binarios\n")
    lines.append(
        "As propriedades `vaBinary` (`Icon.Data`, `Picture.Data`, "
        "`Glyph.Data`) **nao**\nestao inline nos `.dfm`. Cada uma virou "
        "`blobs/<formulario>/<dono>.<prop>.bin`,\nreferenciada no `.dfm` por\n"
        "`{blob <arquivo> <tamanho> sha256:<hash>}`.\n")
    lines.append(
        "A razao esta na secao 2 do plano: os 118 blobs somam 798 KiB de arte "
        "do\nObocaman, da mesma natureza dos 198 `.bmp` de `we-team-editor/` "
        "-- pasta que o\nrepositorio ignora justamente por ser binario de "
        "terceiro sem licenca. Hex e so\numa codificacao; colar os bytes no "
        "`.dfm` reintroduziria no versionamento o que\no `.gitignore` mantem "
        "fora dele. O SHA-256 no `.dfm` e o que preserva a\nverificacao byte "
        "a byte sem versionar os bytes: `--check` confere os 798 KiB\ncontra "
        "o hash.\n")
    lines.append(
        "`blobs/` e ignorado pelo git e renasce do `.exe`, como `wte/assets` "
        "-- mas so no\n**modo de escrita**. O `--check` nao materializa nada: "
        "num clone limpo os 118\n`.bin` faltam, e isso sai como aviso, nao "
        "como divergencia. Blob presente e\ndiferente do `.exe`, ou blob "
        "sobrando, continuam falha.\n")

    lines.append("## Por formulario\n")
    lines.append(
        "Na ordem em que os recursos aparecem em `.rsrc` -- que o linker "
        "mantem\nordenada pelo nome do recurso (`TESTRATEGIA`, `TFICHA_*`, "
        "`TJUGADOR`,\n`TMAINFORM`), e nao pelo nome do objeto. Determinismo "
        "sem reordenar nada.\n")
    lines.append("| Formulario | Classe raiz | Componentes | Classes | Blobs |")
    lines.append("|---|---|---:|---:|---:|")
    for name, root, blobs in forms:
        counts = census(root)
        total.update(counts)
        lines.append(
            f"| `{name}` | `{root.cls}` | {sum(counts.values())} | "
            f"{len(counts)} | {len(blobs)} |")
    lines.append("")

    for name, root, _blobs in forms:
        counts = census(root)
        lines.append(f"### `{name}`\n")
        if not counts:
            lines.append("Sem componentes.\n")
            continue
        lines.append("| Classe | Qtd |")
        lines.append("|---|---:|")
        for cls, qty in order(counts):
            lines.append(f"| `{cls}` | {qty} |")
        lines.append("")

    lines.append("## Total\n")
    lines.append("| Classe | Qtd |")
    lines.append("|---|---:|")
    for cls, qty in order(total):
        lines.append(f"| `{cls}` | {qty} |")
    lines.append(f"| **total** | **{sum(total.values())}** |")
    lines.append("")
    lines.append(
        f"{len(total)} classes distintas, {sum(total.values())} componentes "
        f"em {len(forms)} formularios.\n")
    return "\n".join(lines)


# ----------------------------------------------------------------- driver ---


def generate() -> tuple[dict[str, str], dict[str, bytes]]:
    """Decodifica tudo em memoria. Nada e escrito aqui."""
    if not EXE.is_file():
        raise DfmError(
            f"{REL_EXE} nao existe.\n"
            "       A pasta we-team-editor/ nao e versionada (binario de "
            "terceiro sem\n"
            "       licenca -- ver a secao 2 do plano). Coloque-a na raiz do "
            "repositorio.")

    exe = EXE.read_bytes()
    resources = read_rcdata(exe)

    forms: list[tuple[str, Obj, list[Blob]]] = []
    text_files: dict[str, str] = {}
    blob_files: dict[str, bytes] = {}
    seen: dict[str, str] = {}

    for res_name, offset, data in resources:
        if data[:4] != b"TPF0":
            continue  # DVCLAL e afins: RCDATA que nao e formulario
        root, blobs = parse_form(res_name, offset, data)

        stem = root.name or root.cls
        key = stem.lower()
        if key in seen:
            raise DfmError(
                f"{res_name}: o formulario '{stem}' colide com "
                f"'{seen[key]}' -- os dois dariam o mesmo arquivo de saida")
        seen[key] = stem

        text_files[f"{stem}.dfm"] = render(root)
        for blob in blobs:
            blob_files[f"{stem}/{blob.filename}"] = blob.data
        forms.append((stem, root, blobs))

    if len(forms) != 18:
        raise DfmError(
            f"{REL_EXE}: esperados 18 formularios TPF0 em RT_RCDATA, "
            f"achados {len(forms)}")

    text_files["censo.md"] = render_census(forms)
    return text_files, blob_files


def do_check(text_files: dict[str, str], blob_files: dict[str, bytes]) -> int:
    problems: list[str] = []

    for name, content in sorted(text_files.items()):
        path = OUT / name
        if not path.exists():
            problems.append(f"{name}: nao existe")
            continue
        on_disk = path.read_text(encoding="ascii")
        if on_disk != content:
            for i, (a, b) in enumerate(
                    zip(on_disk.splitlines(), content.splitlines()), 1):
                if a != b:
                    problems.append(f"{name}: linha {i} diverge")
                    break
            else:
                problems.append(
                    f"{name}: {len(on_disk.splitlines())} linhas no disco "
                    f"contra {len(content.splitlines())} regeradas")

    # Blob ausente NAO e falha de conferencia: `blobs/` e cache regeneravel,
    # gitignored por decisao da WTE-TASK-03, e este modo nao materializa nada.
    # Num clone limpo os 118 faltam, e tratar isso como divergencia daria o
    # mesmo codigo de saida de um `.dfm` editado a mao -- que e o que o gate
    # existe para pegar. A garantia byte a byte nao depende do `.bin` no disco:
    # ela vem do SHA-256 dentro do `.dfm` versionado, ja coberto pela
    # comparacao de texto acima.
    missing_blobs = 0
    for name, data in sorted(blob_files.items()):
        path = BLOBS / name
        if not path.exists():
            missing_blobs += 1
        elif path.read_bytes() != data:
            problems.append(f"blobs/{name}: conteudo diverge do .exe")

    expected_text = set(text_files)
    for path in sorted(OUT.glob("*.dfm"), key=lambda p: p.as_posix()):
        if path.name not in expected_text:
            problems.append(f"{path.name}: sobra, nao sai do .exe")
    expected_blobs = set(blob_files)
    if BLOBS.is_dir():
        for path in sorted(BLOBS.rglob("*.bin"), key=lambda p: p.as_posix()):
            rel = path.relative_to(BLOBS).as_posix()
            if rel not in expected_blobs:
                problems.append(f"blobs/{rel}: sobra, nao sai do .exe")

    if missing_blobs:
        print(f"AVISO: {missing_blobs} blobs ainda nao materializados -- "
              f"rode `python3 {GENERATOR}` sem --check para gera-los")

    if problems:
        print(f"{REL_OUT} nao corresponde a {REL_EXE}:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1

    present = len(blob_files) - missing_blobs
    print(f"{len(text_files)} arquivos e {present} blobs em dia com {REL_EXE}")
    return 0


def do_write(text_files: dict[str, str], blob_files: dict[str, bytes]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(text_files.items()):
        # newline="\n" para que o arquivo saia igual no Windows -- ele e
        # comparado byte a byte pelo --check.
        (OUT / name).write_text(content, encoding="ascii", newline="\n")
    for name, data in sorted(blob_files.items()):
        path = BLOBS / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    for name in sorted(text_files):
        if name.endswith(".dfm"):
            lines = text_files[name].count("\n")
            print(f"  {name}: {lines} linhas")
    print(f"\n{len(text_files)} arquivos em {REL_OUT}, "
          f"{len(blob_files)} blobs ({sum(map(len, blob_files.values()))} "
          f"bytes) em {REL_OUT}/blobs")
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
        text_files, blob_files = generate()
    except DfmError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    return do_check(text_files, blob_files) if check \
        else do_write(text_files, blob_files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
