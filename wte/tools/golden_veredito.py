#!/usr/bin/env python3
"""Veredito do gate golden: as divergencias medidas contra as declaradas.

WTE-TASK-22. O `golden_check.sh` compara duas imagens com o
`tools/golden_compare.py` (do `newWe2002` -- ver a nota de reuso abaixo) e joga
o JSON aqui. Este script decide, e o codigo de saida e o veredito:

    0  passou -- nenhuma divergencia alem das declaradas
    1  reprovou -- divergencia que ninguem declarou
    3  reprovou -- faixa declarada que NAO apareceu

O caso 3 e o que separa este gate de um `cmp` com lista de exclusao. Faixa
declarada e afirmacao sobre o comportamento do editor; se ela para de aparecer,
ou o editor mudou, ou o roteiro deixou de exercitar o que dizia exercitar --
e nos dois casos a declaracao virou mentira silenciosa. O `newWe2002` tolera a
ausencia da dele ("nem a divergencia conhecida apareceu"); aqui nao, porque la
a excecao e comportamento indefinido do original e aqui e gravacao deliberada,
que ou acontece ou o roteiro esta quebrado.

## Reuso, e por que nao ha copia

A conversao de bytes em faixas mora em `tools/golden_compare.py`, do
`newWe2002`. Os dois projetos nao compartilham build -- e nao devem --, mas
compartilham **formato**: aquele script le o mesmo `Offsets.hpp` e a mesma
geometria MODE2/2352. Copiar as 186 linhas para ca criaria a segunda copia que
envelhece sozinha, que e o defeito que este repositorio ja pagou em quatro
correcoes.

## Faixa declarada: `INICIO..FIM`, 0-based, inclusiva

Como o `KNOWN_START`/`KNOWN_END` do `newWe2002`, e **nao** como as posicoes
1-based que o `cmp -l` imprime. A confusao ja aconteceu (CORR-WTE-025): a
mesma faixa aparece `11796..26527` medida em base 0 e `11797..26528` no
`cmp -l`.

Uso:
    python3 wte/tools/golden_veredito.py diff.json --conhecida 11796..26527
    python3 wte/tools/golden_veredito.py diff.json --nenhuma
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class FaixaInvalida(ValueError):
    pass


def ler_faixa(texto: str) -> tuple[int, int]:
    """`"a..b"` -> `(a, b)`, com o erro dizendo o que fazer."""
    if ".." not in texto:
        raise FaixaInvalida(f"faixa {texto!r} sem `..` -- a forma e INICIO..FIM, "
                            f"0-based e inclusiva")
    ini, _, fim = texto.partition("..")
    try:
        a, b = int(ini), int(fim)
    except ValueError:
        raise FaixaInvalida(f"faixa {texto!r} com limite nao numerico") from None
    if a > b:
        raise FaixaInvalida(f"faixa {texto!r} invertida")
    if a < 0:
        raise FaixaInvalida(f"faixa {texto!r} com inicio negativo")
    return a, b


def faixas_do_roteiro(caminho: Path) -> list[tuple[int, int]]:
    """As linhas `conhecida: a..b` do cabecalho de um roteiro.

    A declaracao mora NO ROTEIRO, e nao numa lista central, porque ela e
    propriedade da operacao: quem edita o roteiro ve a excecao dele na mesma
    tela, e nao ha lista central para esquecer de atualizar.
    """
    fora = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        se = linha.strip()
        if se.startswith("conhecida:"):
            fora.append(ler_faixa(se.split(":", 1)[1].strip().split()[0]))
    return fora


def julgar(relatorio: dict, conhecidas: list[tuple[int, int]]) -> tuple[int, list[str]]:
    """(codigo de saida, linhas do relatorio)."""
    faixas = relatorio.get("runs", [])
    linhas: list[str] = []

    inesperadas = []
    casadas: set[tuple[int, int]] = set()
    for r in faixas:
        alvo = (int(r["start"]), int(r["end"]))
        if alvo in conhecidas:
            casadas.add(alvo)
        else:
            inesperadas.append(r)

    ausentes = [f for f in conhecidas if f not in casadas]

    if inesperadas:
        linhas.append(f"REPROVOU: {len(inesperadas)} divergencia(s) que ninguem "
                      f"declarou:")
        for r in inesperadas:
            linhas.append(
                f"  {r['start']}..{r['end']}  {r.get('bytes', '?')} byte(s)  "
                f"{r.get('kind', '?')}  "
                f"{r.get('region', '?')}+{r.get('region_delta', '?')}")
        if conhecidas:
            linhas.append("  (declaradas: "
                          + ", ".join(f"{a}..{b}" for a, b in conhecidas) + ")")
        return 1, linhas

    if ausentes:
        linhas.append(f"REPROVOU: {len(ausentes)} faixa(s) declarada(s) que NAO "
                      f"apareceu(ram):")
        for a, b in ausentes:
            linhas.append(f"  {a}..{b}")
        linhas.append("  Declaracao que nao aparece e afirmacao que virou "
                      "mentira: ou o editor mudou, ou o roteiro deixou de "
                      "exercitar o que dizia.")
        return 3, linhas

    if conhecidas:
        linhas.append("PASSOU: so as faixas declaradas divergem — "
                      + ", ".join(f"{a}..{b}" for a, b in conhecidas))
    else:
        linhas.append("PASSOU: byte-identico")
    return 0, linhas


ROTEIROS = Path(__file__).resolve().parents[1] / "tests" / "roteiros"


def conferir_roteiros() -> int:
    """`--check`: as declaracoes dos roteiros do gate sao legiveis?

    Este script nao gera arquivo, entao nao ha saida commitada para comparar --
    e o mesmo caso do `check_lcl_props.py`. O que ele confere e a unica coisa
    que pode envelhecer em silencio aqui: uma linha `conhecida:` malformada num
    roteiro do gate so exploderia no meio de uma corrida de dez minutos, com
    duas copias de ~300 MB ja feitas.
    """
    golden = sorted(ROTEIROS.glob("golden-*.txt"))
    if not golden:
        print(f"golden_veredito: nenhum roteiro golden-*.txt em "
              f"{ROTEIROS}", file=sys.stderr)
        return 2
    total = 0
    for r in golden:
        try:
            faixas = faixas_do_roteiro(r)
        except FaixaInvalida as e:
            print(f"golden_veredito: {r.name}: {e}", file=sys.stderr)
            return 2
        total += len(faixas)
        print(f"golden_veredito: {r.name}: {len(faixas)} faixa(s) declarada(s)")
    print(f"golden_veredito: {len(golden)} roteiro(s), {total} declaracao(oes) "
          f"legivel(eis)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("json", type=Path, nargs="?",
                    help="saida de golden_compare.py --json")
    ap.add_argument("--conhecida", action="append", default=[],
                    metavar="INICIO..FIM",
                    help="faixa declarada, 0-based e inclusiva; repetivel")
    ap.add_argument("--roteiro", type=Path,
                    help="le as linhas `conhecida:` do cabecalho do roteiro")
    ap.add_argument("--nenhuma", action="store_true",
                    help="explicita que nao ha faixa declarada")
    ap.add_argument("--check", action="store_true",
                    help="confere as declaracoes dos roteiros do gate e sai")
    args = ap.parse_args(argv)

    if args.check:
        return conferir_roteiros()
    if args.json is None:
        ap.error("falta o JSON do golden_compare.py (ou use --check)")

    conhecidas: list[tuple[int, int]] = []
    try:
        conhecidas += [ler_faixa(t) for t in args.conhecida]
        if args.roteiro:
            conhecidas += faixas_do_roteiro(args.roteiro)
    except FaixaInvalida as e:
        print(f"golden_veredito: {e}", file=sys.stderr)
        return 2
    if conhecidas and args.nenhuma:
        print("golden_veredito: --nenhuma com faixa declarada nao faz sentido",
              file=sys.stderr)
        return 2

    relatorio = json.loads(args.json.read_text(encoding="utf-8"))
    codigo, linhas = julgar(relatorio, conhecidas)
    for l in linhas:
        print(l)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
