#!/usr/bin/env python3
"""Gera e valida wte/re/spec/INDICE.md a partir dos 96 handlers.

WTE-TASK-23. Le `wte/re/published_methods.tsv` (a lista canonica dos 96,
produzida pelo dump_published.py na WTE-TASK-04) e, para cada um, procura
`wte/re/spec/<formulario>.<handler>.md`. O que nao existe entra no indice como
`aberto`.

Nao e so indexador: ele **valida** cada spec, e e por isso que as regras do
GABARITO.md nao dependem de memoria de ninguem.

    python3 wte/tools/spec_index.py           # regera o INDICE.md
    python3 wte/tools/spec_index.py --check   # o que `make -C wte check` roda

Sai 2 quando o indice commitado diverge do gerado, ou quando alguma spec
quebra uma regra. Sai 0 e imprime uma linha de resumo quando esta em dia.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TSV = RAIZ / "wte" / "re" / "published_methods.tsv"
SPEC = RAIZ / "wte" / "re" / "spec"
INDICE = SPEC / "INDICE.md"

# Fechado de proposito -- ver o GABARITO.md. Sem acento e sem variante: duas
# grafias do mesmo veredito e a maneira mais barata de o indice mentir.
VEREDITOS = (
    "implementado",
    "trivial",
    "divergencia deliberada",
    "nao portado",
    "aberto",
)

# As seis do gabarito, na ordem. `Notas` e opcional e nao entra aqui.
SECOES = (
    "Entrada",
    "Saida",
    "Bytes tocados",
    "Pre-condicoes",
    "Comportamento de erro",
)

# `Saida`, `Pre-condicoes` e `Evidencia` aparecem acentuados no markdown real;
# a comparacao e feita sobre a forma sem acento para nao depender de como quem
# escreveu digitou.
ACENTOS = str.maketrans("áàâãéêíóôõúüç", "aaaaeeiooouuc")

CABECALHO_EVIDENCIA = re.compile(r"^\*\*Evid[eê]ncia:\*\*\s*(.+?)\s*$", re.M)
EVIDENCIAS = ("diff medido", "disassembly lido", "observacao de tela",
              "nao medido")

# O que denuncia decompilado colado. Sao os nomes que o Ghidra inventa quando
# nao tem simbolo, mais a marca da convencao da Borland. Ver PLAN-WTE-LAZARUS
# secao 2 e 8.10 -- transcrever decompilado faz obra derivada, e a saida de
# C++Builder importa a estrutura de 2002 junto.
MARCAS_DE_DECOMPILADO = (
    re.compile(r"^```\s*(c|cpp|c\+\+)\s*$", re.M | re.I),
    re.compile(r"\bundefined[0-9]?\b"),
    re.compile(r"\b[iuf]Var[0-9]+\b"),
    re.compile(r"\blocal_[0-9a-f]+\b"),
    re.compile(r"\bparam_[0-9]+\b"),
    re.compile(r"\b(DAT|FUN|LAB|PTR)_[0-9a-f]{6,}\b"),
    re.compile(r"__fastcall\b"),
)


class SpecError(Exception):
    pass


def sem_acento(s: str) -> str:
    return s.translate(ACENTOS)


def le_handlers() -> list[dict]:
    """Os 96, na ordem em que o dump_published.py os emite (por endereco)."""
    if not TSV.exists():
        raise SpecError(f"{TSV} nao existe -- rode a WTE-TASK-04 antes")
    linhas = TSV.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    fora = []
    for linha in linhas[1:]:
        if not linha.strip():
            continue
        fora.append(dict(zip(cab, linha.split("\t"))))
    if not fora:
        raise SpecError(f"{TSV} nao tem nenhum handler")
    return fora


def le_frontmatter(texto: str, rotulo: str) -> dict:
    if not texto.startswith("---\n"):
        raise SpecError(f"{rotulo}: falta o frontmatter YAML no topo")
    fim = texto.find("\n---\n", 3)
    if fim < 0:
        raise SpecError(f"{rotulo}: frontmatter nao fechado com ---")
    campos = {}
    for linha in texto[4:fim].splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if ":" not in linha:
            raise SpecError(f"{rotulo}: linha de frontmatter sem ':' -- {linha!r}")
        chave, valor = linha.split(":", 1)
        campos[chave.strip()] = valor.strip()
    return campos


def secoes_de(texto: str) -> dict[str, str]:
    """Mapeia titulo de `## ` (sem acento) para o corpo ate o proximo `## `."""
    fora: dict[str, str] = {}
    atual = None
    corpo: list[str] = []
    for linha in texto.splitlines():
        if linha.startswith("## "):
            if atual is not None:
                fora[atual] = "\n".join(corpo)
            atual = sem_acento(linha[3:].strip())
            corpo = []
        elif atual is not None:
            corpo.append(linha)
    if atual is not None:
        fora[atual] = "\n".join(corpo)
    return fora


def valida(caminho: Path, esperado: dict) -> tuple[str, list[str]]:
    """Confere uma spec. Devolve (veredito, evidencias) ou levanta SpecError."""
    rotulo = caminho.name
    texto = caminho.read_text(encoding="utf-8")

    for marca in MARCAS_DE_DECOMPILADO:
        achado = marca.search(texto)
        if achado:
            raise SpecError(
                f"{rotulo}: parece decompilado colado ({achado.group(0)!r}). "
                "A secao 2 do plano manda parafrasear, nunca copiar -- marque "
                "o bloco como ```text e reescreva")

    fm = le_frontmatter(texto, rotulo)
    for chave in ("handler", "formulario", "endereco", "veredito"):
        if chave not in fm:
            raise SpecError(f"{rotulo}: falta '{chave}' no frontmatter")
    for chave in ("handler", "formulario", "endereco"):
        if fm[chave] != esperado[chave]:
            raise SpecError(
                f"{rotulo}: {chave} e {fm[chave]!r} mas o published_methods.tsv "
                f"diz {esperado[chave]!r}")

    veredito = fm["veredito"]
    if veredito not in VEREDITOS:
        raise SpecError(
            f"{rotulo}: veredito {veredito!r} fora do vocabulario "
            f"({', '.join(VEREDITOS)})")

    secs = secoes_de(texto)
    faltando = [s for s in SECOES if s not in secs]
    if faltando:
        raise SpecError(f"{rotulo}: faltam as secoes {', '.join(faltando)}")

    evidencias = []
    for nome in SECOES:
        achados = CABECALHO_EVIDENCIA.findall(secs[nome])
        if not achados:
            raise SpecError(f"{rotulo}: secao '{nome}' sem linha **Evidencia:**")
        for bruto in achados:
            valor = sem_acento(bruto.strip().lower())
            if valor not in EVIDENCIAS:
                raise SpecError(
                    f"{rotulo}: evidencia {bruto!r} em '{nome}' fora do "
                    f"vocabulario ({', '.join(EVIDENCIAS)})")
            evidencias.append(valor)

    # Duas regras do gabarito que sao mecanicas, e por isso moram aqui.
    if veredito == "nao portado":
        just = [s for s in secs if s.lower().startswith("justificativa")]
        if not just or not secs[just[0]].strip():
            raise SpecError(
                f"{rotulo}: veredito 'nao portado' exige uma secao "
                "'## Justificativa' nao vazia -- o criterio de pronto da fase "
                "4 depende disso")
    if veredito == "implementado" and set(evidencias) <= {"observacao de tela",
                                                          "nao medido"}:
        raise SpecError(
            f"{rotulo}: veredito 'implementado' com toda evidencia em "
            "'observacao de tela'/'nao medido' -- isso e hipotese, nao spec")

    return veredito, evidencias


def eventos_de(bruto: str) -> str:
    """Celula da coluna Evento.

    O TSV guarda um evento POR CONTROLE que o handler atende, separados por
    `|` -- `ficha_color.barraChange` sai como `OnChange|OnChange|OnChange`,
    porque serve tres barras. O `|` cru quebraria a tabela markdown, e repetir
    o mesmo nome tres vezes nao diz nada: vira `OnChange x3`.
    """
    if not bruto:
        return "—"
    nomes: list[str] = []
    for nome in bruto.split("|"):
        if nome and nome not in nomes:
            nomes.append(nome)
    partes = []
    for nome in nomes:
        n = bruto.split("|").count(nome)
        partes.append(f"{nome} x{n}" if n > 1 else nome)
    return ", ".join(partes)


def monta() -> tuple[str, dict]:
    handlers = le_handlers()
    esperados = {f"{h['formulario']}.{h['handler']}": h for h in handlers}

    # Spec orfa e erro: arquivo que nao casa com handler nenhum quer dizer
    # nome errado, e um nome errado some do indice em silencio.
    reservados = {"GABARITO.md", "INDICE.md", "README.md"}
    for arq in sorted(SPEC.glob("*.md")):
        if arq.name in reservados:
            continue
        chave = arq.name[:-3]
        if chave not in esperados:
            raise SpecError(
                f"{arq.name}: nao corresponde a nenhum dos "
                f"{len(esperados)} handlers. O nome e "
                "<formulario>.<handler>.md")

    linhas = []
    contagem = {v: 0 for v in VEREDITOS}
    com_spec = 0
    for h in handlers:
        chave = f"{h['formulario']}.{h['handler']}"
        arq = SPEC / f"{chave}.md"
        if arq.exists():
            veredito, _ = valida(arq, h)
            com_spec += 1
            alvo = f"[{h['handler']}]({chave}.md)"
        else:
            veredito = "aberto"
            alvo = h["handler"]
        contagem[veredito] += 1
        linhas.append(
            f"| `{h['endereco']}` | `{h['formulario']}` | {alvo} | "
            f"{eventos_de(h['evento'])} | {h['grupo']} | {veredito} |")

    total = len(handlers)
    cab = [
        "# `re/spec/INDICE.md` — os 96 handlers e o veredito de cada um",
        "",
        "**Gerado — não editar à mão.** Correção entra no gerador e o arquivo",
        "é regerado:",
        "",
        "```sh",
        "python3 wte/tools/spec_index.py",
        "python3 wte/tools/spec_index.py --check   # o que `make -C wte check` roda",
        "```",
        "",
        "Fonte: [`../published_methods.tsv`](../published_methods.tsv)",
        "(WTE-TASK-04) mais os `<formulario>.<handler>.md` desta pasta. O",
        "gabarito e o vocabulário de veredito estão em",
        "[`GABARITO.md`](GABARITO.md); é a",
        "[WTE-TASK-29](/docs/tasks/29-fechamento-fase-4.md) que exige nenhum",
        "`aberto`.",
        "",
        "## Contagem",
        "",
        "| Veredito | Handlers |",
        "|---|---|",
    ]
    for v in VEREDITOS:
        cab.append(f"| `{v}` | {contagem[v]} |")
    cab += [
        f"| **total** | **{total}** |",
        "",
        f"{com_spec} de {total} têm arquivo de spec.",
        "",
        "## Os 96",
        "",
        "Na ordem de endereço, como o `dump_published.py` os emite.",
        "",
        "| Endereço | Formulário | Handler | Evento | Grupo | Veredito |",
        "|---|---|---|---|---|---|",
    ]
    return "\n".join(cab + linhas) + "\n", {
        "total": total, "com spec": com_spec, **contagem}


def main(argv: list[str]) -> int:
    modo_check = "--check" in argv[1:]
    try:
        texto, contagem = monta()
    except SpecError as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2

    if modo_check:
        if not INDICE.exists():
            print(f"ERRO: {INDICE} nao existe -- rode sem --check",
                  file=sys.stderr)
            return 2
        atual = INDICE.read_text(encoding="utf-8")
        if atual != texto:
            print(f"ERRO: {INDICE.relative_to(RAIZ)} nao esta em dia com "
                  "published_methods.tsv + as specs. Rode "
                  "`python3 wte/tools/spec_index.py`.", file=sys.stderr)
            return 2
        print(f"{contagem['total']} handlers indexados, "
              f"{contagem['com spec']} com spec, "
              f"{contagem['aberto']} abertos")
        return 0

    INDICE.write_text(texto, encoding="utf-8")
    print(f">> {INDICE.relative_to(RAIZ)}")
    for chave, valor in contagem.items():
        print(f"   {valor:5} {chave}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
