#!/usr/bin/env python3
"""Gera as unidades Pascal de offsets e tabelas estaticas -- WTE-TASK-16.

Entrada, toda deste repositorio (nunca decompilado -- PLAN-WTE-LAZARUS §8.10):

    src/core/include/we2002/Offsets.hpp   69 OFS_* + 3 constantes de setor
    src/core/include/we2002/Tables.hpp    as declaracoes das 16 tabelas
    src/core/Tables.cpp                   os inicializadores

Saida:

    wte/src/we2002_offsets.pas
    wte/src/we2002_tables.pas

O gerador **recusa** em vez de improvisar. Construcao que ele nao reconhece --
literal com sufixo, expressao aritmetica, tipo C++ fora da tabela de mapeamento,
definicao em Tables.cpp que Tables.hpp nao declara -- aborta com a linha e o
motivo. Esse rigor nao e zelo: erro de parsing de literal produz numero
plausivel e errado, e offset errado so aparece quando a gravacao corromper a
imagem de 474 MB.

Mapeamento de tipo conforme wte/re/tipos.md (WTE-TASK-15):

    Offset (int64_t)   -> Int64          constante sem tipo, avaliada em Int64
    const char [N]     -> ShortInt       'char' numerico tem SINAL no x86
    const char [N][M]  -> AnsiChar       'char' de texto, array fixo, sem string
    const int  [N]     -> LongInt        largura fixa; nunca Integer/Cardinal

Uso:
    python3 wte/tools/gen_tables_pas.py            # escreve
    python3 wte/tools/gen_tables_pas.py --check    # confere, sai 2 se divergir
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OFFSETS_HPP = ROOT / "src/core/include/we2002/Offsets.hpp"
TABLES_HPP = ROOT / "src/core/include/we2002/Tables.hpp"
TABLES_CPP = ROOT / "src/core/Tables.cpp"

OUT_OFFSETS = ROOT / "wte/src/we2002_offsets.pas"
OUT_TABLES = ROOT / "wte/src/we2002_tables.pas"

# Os dois dumpers da conferencia obrigatoria. Sao gerados -- e nao escritos a
# mao -- para que tabela nova entre nos dois lados sozinha; o que eles NAO
# compartilham e o que importa: um le o Pascal gerado, o outro le o C++
# original, e cada valor vem de um compilador diferente. Comparar a saida do
# gerador contra o proprio parser do gerador nao provaria nada.
OUT_DUMP_PAS = ROOT / "wte/tests/test_offsets.pas"
OUT_DUMP_CPP = ROOT / "wte/tests/test_offsets.cpp"

# Definicoes que existem em Tables.cpp e que Tables.hpp nao declara. Cada uma
# precisa de motivo escrito: sem esta lista o gerador aborta, e e assim que uma
# tabela nova nao some em silencio.
UNDECLARED_OK = {
    "nomi_squadre": (
        "sobra do extract_legacy_data.py: copia nao-const, com o nome italiano, "
        "de TEAM_NAMES. Nao esta em Tables.hpp, ninguem a referencia, e o nome "
        "italiano nao entra no Pascal. Ver o Log da WTE-TASK-16."
    ),
}

# ---------------------------------------------------------------- utilidades --


class GenError(RuntimeError):
    """Recusa do gerador. Sempre com arquivo, linha e motivo."""


def rel(path: Path) -> str:
    """Caminho relativo a raiz quando der; caso contrario, o proprio caminho.

    Os testes de recusa alimentam o gerador com arquivos plantados em /tmp, que
    nao estao sob a raiz. `relative_to` levantaria ValueError e trocaria a
    mensagem de recusa -- que e o que o teste mede -- por um traceback.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(path: Path, lineno: int, msg: str) -> None:
    raise GenError(f"{rel(path)}:{lineno}: {msg}")


def strip_block_comments(text: str) -> str:
    """Remove /* ... */ preservando a contagem de linhas."""
    def repl(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")

    return re.sub(r"/\*.*?\*/", repl, text, flags=re.S)


# ------------------------------------------------------------------ offsets --

# `inline constexpr Offset NOME = 1012640;  // was OFS_NOMI_SQ1`
RE_OFFSET = re.compile(
    r"^inline\s+constexpr\s+Offset\s+(?P<name>\w+)\s*=\s*"
    r"(?P<value>-?\d+)\s*;"
    r"(?:\s*//\s*(?P<comment>.*?))?\s*$"
)
# Qualquer outra `inline constexpr` -- se aparecer uma que o RE_OFFSET nao casa,
# e construcao nova e o gerador tem de reclamar, nao ignorar.
RE_ANY_CONSTEXPR = re.compile(r"^inline\s+constexpr\b")


@dataclass
class Const:
    name: str
    value: int
    comment: str | None


def parse_offsets(path: Path) -> list[Const]:
    out: list[Const] = []
    text = strip_block_comments(path.read_text(encoding="utf-8"))
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.rstrip()
        if not RE_ANY_CONSTEXPR.match(line):
            continue
        m = RE_OFFSET.match(line)
        if not m:
            fail(path, lineno, f"constexpr que o gerador nao reconhece: {line!r}")
        comment = m.group("comment")
        out.append(Const(m.group("name"), int(m.group("value")),
                         comment.strip() if comment else None))
    if not out:
        raise GenError(f"{path}: nenhum offset encontrado")
    return out


# ------------------------------------------------------------------- tabelas --

# `extern const char TEAM_NAME_LEN_1[95];`
RE_EXTERN = re.compile(
    r"^extern\s+const\s+(?P<ctype>char|int)\s+(?P<name>\w+)"
    r"(?P<dims>(?:\[[^\]]*\])*)\s*;\s*$"
)
# `inline constexpr int N_ROLES = 21;`
RE_HPP_CONST = re.compile(
    r"^inline\s+constexpr\s+int\s+(?P<name>\w+)\s*=\s*(?P<value>-?\d+)\s*;")
# `const char TEAM_NAME_LEN_1[95] =` / `char nomi_squadre[120][20] =`
RE_DEF_HEAD = re.compile(
    r"^(?P<const>const\s+)?(?P<ctype>char|int)\s+(?P<name>\w+)"
    r"(?P<dims>(?:\[[^\]]*\])*)\s*=\s*$")

RE_INT_TOKEN = re.compile(r"^-?\d+$")
RE_STR_TOKEN = re.compile(r'^"([^"\\]*)"$')


@dataclass
class Decl:
    ctype: str
    name: str
    dims: list[str]
    doc: list[str] = field(default_factory=list)


@dataclass
class Element:
    text: str            # ja em Pascal
    comment: str | None
    src_line: int        # linha do inicializador, para preservar agrupamento


@dataclass
class Table:
    decl: Decl
    kind: str            # 'int' | 'byte' | 'text'
    elements: list[Element]
    inner: int | None    # segunda dimensao, quando 'text'


def parse_tables_hpp(path: Path) -> tuple[dict[str, Decl], list[Const], list[str]]:
    """Devolve (declaracoes, constantes inteiras, ordem das declaracoes)."""
    decls: dict[str, Decl] = {}
    consts: list[Const] = []
    order: list[str] = []
    doc: list[str] = []
    text = strip_block_comments(path.read_text(encoding="utf-8"))
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("///"):
            doc.append(s[3:].strip())
            continue
        m = RE_HPP_CONST.match(s)
        if m:
            consts.append(Const(m.group("name"), int(m.group("value")),
                                "\n".join(doc) if doc else None))
            doc = []
            continue
        m = RE_EXTERN.match(s)
        if m:
            dims = re.findall(r"\[([^\]]*)\]", m.group("dims"))
            name = m.group("name")
            decls[name] = Decl(m.group("ctype"), name, dims, doc)
            order.append(name)
            doc = []
            continue
        if s and not s.startswith("//"):
            doc = []
    if not decls:
        raise GenError(f"{path}: nenhuma tabela declarada")
    return decls, consts, order


def split_initializer(body: str, first_line: int, path: Path) -> list[Element]:
    """Quebra o corpo de um inicializador em elementos, com comentario e linha.

    Preserva o agrupamento por linha do C++: as tabelas de comprimento tem
    quebras que separam selecoes / all-stars / clubes de ML, e perder isso
    tornaria o Pascal ilegivel ao lado da fonte.
    """
    elements: list[Element] = []
    for offset, raw in enumerate(body.splitlines()):
        lineno = first_line + offset
        comment = None
        if "//" in raw:
            code, _, comment = raw.partition("//")
            comment = comment.strip() or None
        else:
            code = raw
        for tok in code.split(","):
            tok = tok.strip()
            if not tok:
                continue
            elements.append(Element(tok, None, lineno))
        if comment is not None:
            if elements and elements[-1].src_line == lineno:
                elements[-1].comment = comment
            elif comment:
                # Comentario numa linha sem valor -- so acontece no `}; //462`,
                # que fica fora do corpo. Se aparecer aqui, e construcao nova.
                fail(path, lineno, f"comentario sem elemento: {comment!r}")
    return elements


def parse_tables_cpp(path: Path, decls: dict[str, Decl],
                     consts: dict[str, int]) -> dict[str, Table]:
    text = strip_block_comments(path.read_text(encoding="utf-8"))
    lines = text.splitlines()
    tables: dict[str, Table] = {}
    i = 0
    while i < len(lines):
        m = RE_DEF_HEAD.match(lines[i].strip())
        if not m:
            i += 1
            continue
        head_lineno = i + 1
        name = m.group("name")
        if lines[i + 1].strip() != "{":
            fail(path, head_lineno + 1, "esperava '{' na linha seguinte")
        j = i + 2
        while j < len(lines) and not lines[j].lstrip().startswith("};"):
            j += 1
        if j >= len(lines):
            fail(path, head_lineno, "inicializador sem '};'")
        body = "\n".join(lines[i + 2:j])

        if name not in decls:
            if name not in UNDECLARED_OK:
                fail(path, head_lineno,
                     f"'{name}' definido aqui e nao declarado em Tables.hpp. "
                     f"Acrescente a declaracao, ou registre o motivo em "
                     f"UNDECLARED_OK do gerador.")
            i = j + 1
            continue

        decl = decls[name]
        if decl.ctype != m.group("ctype"):
            fail(path, head_lineno,
                 f"'{name}': tipo {m.group('ctype')} aqui, "
                 f"{decl.ctype} em Tables.hpp")
        if not m.group("const"):
            fail(path, head_lineno, f"'{name}': definicao sem 'const'")

        elements = split_initializer(body, i + 3, path)
        kinds = {"int" if RE_INT_TOKEN.match(e.text) else
                 "str" if RE_STR_TOKEN.match(e.text) else "?"
                 for e in elements}
        if "?" in kinds:
            bad = next(e for e in elements
                       if not RE_INT_TOKEN.match(e.text)
                       and not RE_STR_TOKEN.match(e.text))
            fail(path, bad.src_line,
                 f"'{name}': elemento que o gerador nao reconhece: {bad.text!r}")
        if len(kinds) != 1:
            fail(path, head_lineno,
                 f"'{name}': inicializador mistura numero e string")
        kind_src = kinds.pop()

        inner = None
        if kind_src == "str":
            kind = "text"
            if len(decl.dims) != 2:
                fail(path, head_lineno,
                     f"'{name}': inicializador de string com {len(decl.dims)} "
                     f"dimensao(oes); esperava 2")
            inner = resolve_dim(decl.dims[1], consts, path, head_lineno, name)
        else:
            kind = "int" if decl.ctype == "int" else "byte"
            if len(decl.dims) != 1:
                fail(path, head_lineno,
                     f"'{name}': inicializador numerico com {len(decl.dims)} "
                     f"dimensao(oes); esperava 1")

        outer_txt = decl.dims[0]
        if outer_txt.strip():
            outer = resolve_dim(outer_txt, consts, path, head_lineno, name)
            if outer != len(elements):
                fail(path, head_lineno,
                     f"'{name}': declarado com {outer} elementos, "
                     f"inicializado com {len(elements)}")

        # Comprimento de cada literal contra a dimensao interna: o C++ trunca em
        # silencio quando a string nao cabe, e o Pascal recusa. Conferir aqui da
        # a mensagem util em vez de um erro do fpc.
        if kind == "text":
            assert inner is not None
            for e in elements:
                lit = RE_STR_TOKEN.match(e.text).group(1)  # type: ignore[union-attr]
                if len(lit) > inner:
                    fail(path, e.src_line,
                         f"'{name}': literal de {len(lit)} caracteres "
                         f"nao cabe em [{inner}]")

        tables[name] = Table(decl, kind, elements, inner)
        i = j + 1
    return tables


def resolve_dim(txt: str, consts: dict[str, int], path: Path,
                lineno: int, name: str) -> int:
    txt = txt.strip()
    if RE_INT_TOKEN.match(txt):
        return int(txt)
    if txt in consts:
        return consts[txt]
    fail(path, lineno, f"'{name}': dimensao '{txt}' nao resolve para inteiro")
    raise AssertionError  # inalcancavel; fail() sempre levanta


# ------------------------------------------------------------------- emissao --

HEADER = """\
{{ GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.
  Fonte de verdade: {sources}

  Regenerar:  python3 wte/tools/gen_tables_pas.py
  Conferir:   python3 wte/tools/gen_tables_pas.py --check
              (ou `make -C wte check`, que roda todos os geradores) }}

unit {unit};

{{$mode objfpc}}{{$H+}}
{{$J-}}  {{ constante com tipo e SO leitura -- em C++ elas sao `const` }}

interface
"""

FOOTER = """
implementation

end.
"""


def pascal_comment(text: str) -> str:
    """Comentario Pascal seguro: '}' fecharia o bloco."""
    return "{ " + text.replace("}", ")").replace("{", "(") + " }"


def emit_offsets(offsets: list[Const]) -> str:
    width = max(len(c.name) for c in offsets)
    out = [HEADER.format(unit="we2002_offsets",
                         sources="src/core/include/we2002/Offsets.hpp")]
    out.append("""
type
  { `using Offset = std::int64_t` do Offsets.hpp. Largura fixa por definicao do
    FPC -- nunca Integer, Cardinal, PtrInt ou NativeInt (wte/re/tipos.md). }
  TOffset = Int64;

const
  { Deslocamento absoluto em bytes na imagem MODE2/2352 crua.

    NAO sao offsets de arquivo do ISO9660. Apontam para o fluxo de setores cru e
    foram calibrados a mao para cair dentro da regiao de dados de 2048 bytes de
    um setor (bytes 24..2071); as leituras que cruzariam fronteira de setor sao
    quebradas por seeks explicitos para as variantes *_A / *_B.

    Constantes SEM tipo de proposito: o FPC avalia inteiro constante em Int64,
    e sem tipo elas nao podem ser escritas nem com $J ligado. }
""")
    for c in offsets:
        line = f"  {c.name.ljust(width)} = {c.value};"
        if c.comment:
            line += f"  {pascal_comment(c.comment)}"
        out.append(line)
    out.append(FOOTER)
    return "\n".join(out).replace("\n\n\n", "\n\n")


PASCAL_ELEM_TYPE = {"int": "LongInt", "byte": "ShortInt"}


def emit_table(t: Table) -> list[str]:
    out: list[str] = []
    for d in t.decl.doc:
        out.append(f"  {pascal_comment(d)}")
    n = len(t.elements)
    if t.kind == "text":
        typ = f"array[0..{n - 1}] of array[0..{t.inner - 1}] of AnsiChar"
    else:
        typ = f"array[0..{n - 1}] of {PASCAL_ELEM_TYPE[t.kind]}"
    out.append(f"  {t.decl.name}: {typ} = (")

    # Um elemento por linha quando ha comentario; senao preserva o agrupamento
    # por linha do C++.
    by_line: dict[int, list[Element]] = {}
    for e in t.elements:
        by_line.setdefault(e.src_line, []).append(e)

    last = t.elements[-1]
    for _, group in sorted(by_line.items()):
        if any(e.comment for e in group):
            for e in group:
                sep = "" if e is last else ","
                txt = to_pascal(e.text)
                out.append(f"    {txt}{sep}"
                           + (f"  {pascal_comment(e.comment)}" if e.comment else ""))
        else:
            body = ",".join(to_pascal(e.text) for e in group)
            sep = "" if group[-1] is last else ","
            out.append(f"    {body}{sep}")
    out.append("  );")
    return out


def to_pascal(tok: str) -> str:
    m = RE_STR_TOKEN.match(tok)
    if m:
        return "'" + m.group(1).replace("'", "''") + "'"
    return tok


def emit_tables(consts: list[Const], tables: dict[str, Table],
                order: list[str]) -> str:
    out = [HEADER.format(unit="we2002_tables",
                         sources="src/core/include/we2002/Tables.hpp, "
                                 "src/core/Tables.cpp")]
    out.append("\nconst")
    for c in consts:
        for d in (c.comment or "").splitlines():
            out.append(f"  {pascal_comment(d)}")
        out.append(f"  {c.name} = {c.value};")
    out.append("")
    for name in order:
        out.extend(emit_table(tables[name]))
        out.append("")
    out.append(FOOTER.lstrip("\n"))
    return "\n".join(out)


# ------------------------------------------------------------------ dumpers --

DUMP_DOC = """\
  Despejo das constantes, em formato estavel e diffavel. Existe um irmao em
  {other}: os dois emitem exatamente as mesmas linhas, um lendo o
  {reads}, o outro lendo o {other_reads}.

  Se as duas saidas divergirem, o gerador leu um literal errado -- e offset
  errado so aparece quando a gravacao corromper a imagem de 474 MB.

  Rodado por wte/tools/test_gen_tables_pas.py.
"""


def emit_dump_pas(consts: list[Const], tables: dict[str, Table],
                  order: list[str]) -> str:
    doc = DUMP_DOC.format(other="wte/tests/test_offsets.cpp",
                          reads="Pascal gerado",
                          other_reads="C++ original")
    out = ["{ GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.",
           "", doc.rstrip(), "}", "",
           "program test_offsets;", "",
           "{$mode objfpc}{$H+}", "",
           "uses we2002_offsets, we2002_tables;", "",
           "var", "  i: LongInt;", "  hex: string;", "  j: LongInt;", "",
           "begin"]
    for c in consts:
        out.append(f"  WriteLn('CONST'#9'{c.name}'#9, Int64({c.name}));")
    for name in order:
        t = tables[name]
        n = len(t.elements)
        if t.kind == "text":
            out.append(f"  for i := 0 to {n - 1} do")
            out.append("  begin")
            out.append("    hex := '';")
            out.append(f"    for j := 0 to {t.inner - 1} do")
            out.append(f"      hex := hex + HexStr(Ord({name}[i][j]), 2);")
            out.append(f"    WriteLn('TXT'#9'{name}'#9, i, #9, hex);")
            out.append("  end;")
        else:
            out.append(f"  for i := 0 to {n - 1} do")
            out.append(f"    WriteLn('NUM'#9'{name}'#9, i, #9, "
                       f"LongInt({name}[i]));")
    out.append("end.")
    return "\n".join(out) + "\n"


def emit_dump_cpp(consts: list[Const], tables: dict[str, Table],
                  order: list[str]) -> str:
    doc = DUMP_DOC.format(other="wte/tests/test_offsets.pas",
                          reads="C++ original",
                          other_reads="Pascal gerado")
    out = ["// GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.",
           "//"]
    out += ["// " + line if line else "//" for line in doc.rstrip().splitlines()]
    out += ["",
            '#include <cstdio>',
            '#include <cstdint>',
            '#include "we2002/Offsets.hpp"',
            '#include "we2002/Tables.hpp"',
            "",
            "using namespace we2002;",
            "",
            "int main() {"]
    for c in consts:
        out.append(f'  std::printf("CONST\\t{c.name}\\t%lld\\n", '
                   f'(long long){c.name});')
    for name in order:
        t = tables[name]
        n = len(t.elements)
        if t.kind == "text":
            out.append(f"  for (int i = 0; i < {n}; ++i) {{")
            out.append(f'    std::printf("TXT\\t{name}\\t%d\\t", i);')
            out.append(f"    for (int j = 0; j < {t.inner}; ++j)")
            out.append(f'      std::printf("%02X", '
                       f'(unsigned char){name}[i][j]);')
            out.append('    std::printf("\\n");')
            out.append("  }")
        else:
            out.append(f"  for (int i = 0; i < {n}; ++i)")
            out.append(f'    std::printf("NUM\\t{name}\\t%d\\t%d\\n", i, '
                       f'(int){name}[i]);')
    out.append("  return 0;")
    out.append("}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------- main --

def build() -> dict[Path, str]:
    offsets = parse_offsets(OFFSETS_HPP)
    decls, hpp_consts, order = parse_tables_hpp(TABLES_HPP)
    consts = {c.name: c.value for c in hpp_consts}
    tables = parse_tables_cpp(TABLES_CPP, decls, consts)

    missing = [n for n in order if n not in tables]
    if missing:
        raise GenError(
            f"{rel(TABLES_HPP)}: declarada(s) e sem definicao em "
            f"Tables.cpp: {', '.join(missing)}")

    dump_consts = offsets + hpp_consts
    return {
        OUT_OFFSETS: emit_offsets(offsets),
        OUT_TABLES: emit_tables(hpp_consts, tables, order),
        OUT_DUMP_PAS: emit_dump_pas(dump_consts, tables, order),
        OUT_DUMP_CPP: emit_dump_cpp(dump_consts, tables, order),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    args = ap.parse_args(argv)

    try:
        produced = build()
    except GenError as exc:
        print(f"gen_tables_pas: RECUSA: {exc}", file=sys.stderr)
        return 1

    rc = 0
    for path, text in produced.items():
        relp = rel(path)
        if args.check:
            if not path.exists():
                print(f"gen_tables_pas: {relp}: AUSENTE", file=sys.stderr)
                rc = 2
            elif path.read_text(encoding="utf-8") != text:
                print(f"gen_tables_pas: {relp}: DIVERGE do gerador",
                      file=sys.stderr)
                rc = 2
            else:
                print(f"gen_tables_pas: {relp}: ok")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"gen_tables_pas: {relp}: {len(text)} B")
    return rc


if __name__ == "__main__":
    sys.exit(main())
