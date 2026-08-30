#!/usr/bin/env python3
"""Converte os FAQs de texto do PES2 em Markdown legivel.

Os dois FAQs usam convencoes de cabecalho diferentes -- `=====` e `-----`
cercando o titulo no do BigCj34, `+++++` no do Dzanic -- e ambos misturam
prosa com blocos alinhados por espaco.  Prosa em Markdown reflui sozinha,
entao ela fica como esta; o que precisa de cuidado sao os blocos, que
refluiriam e virariam sopa.  Cada bloco separado por linha em branco e
classificado em um de tres:

  mapeamento  `Nome do jogo -Nome real`  -> tabela Markdown
  lista       nomes curtos, um por linha -> bloco de codigo
  prosa       o resto                    -> intacto

Uso:  python3 tools/pes2/faq2md.py ENTRADA.txt SAIDA.md
"""
import re
import sys

FENCE_EQ = re.compile(r"^={3,}\s*$")
FENCE_DASH = re.compile(r"^-{3,}\s*$")
FENCE_PLUS = re.compile(r"^\+{3,}\s*$")
# O grupo do meio precisa ter algo que nao seja `+`: sem isso a regua pura
# `++++++...` casa consigo mesma, com o miolo virando um unico `+`.
PLUS_TITLED = re.compile(r"^\+{5,}([^+].*?)\+{5,}\s*$")
# "Aragon        -Manchester United" e "Sorncek   -Srincek"
MAPPING = re.compile(r"^(\S.*?\S|\S)\s*-\s*(\S.*)$")


def is_short_name(line):
    s = line.strip()
    return 0 < len(s) <= 30 and "  " not in s and not s.endswith((".", ":", ","))


def classify(block):
    body = [l for l in block if l.strip()]
    if len(body) < 2:
        return "prose"
    mapped = sum(1 for l in body if MAPPING.match(l.strip()) and len(l) < 80)
    if mapped >= len(body) * 0.8 and mapped >= 3:
        return "mapping"
    if all(is_short_name(l) for l in body) and len(body) >= 3:
        return "list"
    if sum(1 for l in body if "  " in l.strip()) >= len(body) * 0.6:
        return "block"
    return "prose"


def emit(block, out):
    kind = classify(block)
    body = [l.rstrip() for l in block if l.strip()]
    if kind == "mapping":
        rows, pre = [], []
        for l in body:
            m = MAPPING.match(l.strip())
            if m:
                rows.append((m.group(1).strip(), m.group(2).strip()))
            elif rows:
                pre.append(l)          # cauda solta: vira nota depois da tabela
            else:
                pre.append(l)          # cabecalho da coluna, some na tabela
        out.append("| No jogo | Nome real |")
        out.append("|---|---|")
        for a, b in rows:
            out.append(f"| {a} | {b} |")
        if pre:
            out.append("")
            out.extend(pre)
    elif kind in ("list", "block"):
        out.append("```")
        out.extend(body)
        out.append("```")
    else:
        out.extend(l.rstrip() for l in block)
    out.append("")


def headings_bigcj34(lines):
    """Marca (indice, nivel, titulo) para titulos cercados por ==== ou ----."""
    heads = {}
    skip = set()
    for i in range(len(lines) - 2):
        top, mid, bot = lines[i], lines[i + 1], lines[i + 2]
        if FENCE_EQ.match(top) and FENCE_EQ.match(bot) and mid.strip():
            heads[i] = (2, mid.strip())
            skip |= {i, i + 1, i + 2}
        elif FENCE_DASH.match(top) and FENCE_DASH.match(bot) and mid.strip():
            heads[i] = (3, mid.strip())
            skip |= {i, i + 1, i + 2}
    return heads, skip


def headings_dzanic(lines):
    heads = {}
    skip = set()
    for i, l in enumerate(lines):
        m = PLUS_TITLED.match(l)
        if m:
            heads[i] = (3, m.group(1).strip())
            skip.add(i)
            continue
        if FENCE_PLUS.match(l) and len(l.strip()) >= 70:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            after = lines[i + 2] if i + 2 < len(lines) else ""
            if nxt.strip() and len(nxt.strip()) <= 40 and not after.strip():
                heads[i] = (2, nxt.strip())
                skip |= {i, i + 1}
            else:
                skip.add(i)          # regua decorativa, some
            continue
        # "Ireland" seguido de "+++++++"
        if FENCE_PLUS.match(l) and len(l.strip()) < 70 and i > 0:
            prev = lines[i - 1].strip()
            if prev and len(prev) <= 40 and i - 1 not in skip and "+" not in prev:
                heads[i - 1] = (3, prev)
                skip |= {i - 1, i}
    return heads, skip


def convert(path, title):
    lines = open(path, encoding="latin-1").read().splitlines()
    dzanic = sum(1 for l in lines if FENCE_PLUS.match(l)) > sum(
        1 for l in lines if FENCE_EQ.match(l)
    )
    heads, skip = (headings_dzanic if dzanic else headings_bigcj34)(lines)

    out = [f"# {title}", ""]
    block = []
    for i, l in enumerate(lines):
        if i in heads:
            if block:
                emit(block, out)
                block = []
            level, text = heads[i]
            out.append("#" * level + " " + text)
            out.append("")
            continue
        if i in skip:
            continue
        if not l.strip():
            if block:
                emit(block, out)
                block = []
            continue
        block.append(l)
    if block:
        emit(block, out)

    # colapsa linhas em branco repetidas
    clean, blank = [], False
    for l in out:
        if not l.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        clean.append(l)
    return "\n".join(clean).rstrip() + "\n"


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "FAQ"
    open(dst, "w", encoding="utf-8").write(convert(src, title))
    print(f"{src} -> {dst}")
