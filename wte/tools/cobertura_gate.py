#!/usr/bin/env python3
"""Que handler dispara dentro de que gate golden -- CORR-WTE-089.

## Por que esta ferramenta existe

A WTE-TASK-31 pede que os 96 tenham veredito, e a razao mais comum de um
`aberto` sobreviver e a frase *"nada exercita o corpo"*. Ela foi escrita mais de
uma vez a partir do `compara_tela.sh`, que e a regua de PIXEL do grupo de carga
-- e nao a partir da bateria golden, que e a regua de BYTE e dirige a janela
bem mais fundo.

O resultado foi um erro medido em 2026-08-24: a spec do
`MainForm.lista_jugadores_1Change` afirmava zero disparos, e o
`golden-11-descarte-ml` o dispara DUAS vezes, com o gate verde. Tres vereditos
estavam nessa situacao.

O `port-trace.log` que o `golden_run_laz.sh` ja escreve responde a pergunta
sozinho. Esta ferramenta so a torna versionada e conferivel.

## O argumento de verificacao, escrito para poder ser contestado

Handler que dispara dentro de um roteiro cujo gate esta VERDE, e cujo efeito
entra nos bytes comparados, esta verificado por aquele gate. Nao e prova de que
cada ramo dele foi exercitado -- o `mostrar_jugadorClick` entra so pelo botao do
titular, e o ramo do reserva segue sem regua. Por isso o TSV guarda a CONTAGEM,
nao um booleano: 64 disparos de `lista_equipos_2Change` num roteiro que desce 64
itens dizem que a lista inteira passou; 1 disparo diz outra coisa.

## Como medir (precisa do `:98`; nao roda em `--check`)

    d=work/cobertura/golden-11-descarte-ml
    mkdir -p $d && cp roms/japanese-shift-jis.bin $d/img.bin
    bash wte/tools/golden_run_laz.sh \
         wte/tests/roteiros/golden-11-descarte-ml.port.txt $d/img.bin $d
    python3 wte/tools/cobertura_gate.py --colher work/cobertura

O `--colher` le todo `<dir>/<roteiro>/port-trace.log` e reescreve o TSV. O
modo sem argumento e o `--check` sao offline: leem o TSV versionado, como o
`check_fase4.py` faz com o `fase-4-golden.tsv`. Trace nao e versionado (e saida
de execucao); a MEDIDA e.

## A guarda, e a licao de onde ela vem

Spec que cita este TSV como evidencia TEM de ter linha nele. E a licao literal
do `check_edicao.py:106-111`: o `dorsalMouseDown` dizia
`compara_tela.sh --edicao` ate o trace mostrar que aquele modo nao clica camisa
nenhuma. Citar regua e barato; ter disparo medido nao.

E o outro lado: roteiro citado no TSV tem de existir, ter par `.port` e estar
registrado como PASSOU nos DOIS modos do `fase-4-golden.tsv`. Cobertura dentro
de gate vermelho nao verifica nada.

## Uma armadilha medida na coleta

O `jugador.flechasapaClick` emite um SEGUNDO `REMark` por sufixo
(`flechasapaClick: bitmap N sem dono`), entao `grep -c` cru conta dobrado. A
extracao aqui casa o nome qualificado ancorado no fim (`$`), o que descarta a
linha com sufixo -- e o teste guarda isso.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spec_index as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WTE = ROOT / "wte"
ROTEIROS = WTE / "tests" / "roteiros"
TSV = WTE / "re" / "fase-4-cobertura.tsv"
BATERIA = WTE / "re" / "fase-4-golden.tsv"

GENERATOR = "wte/tools/cobertura_gate.py"
CABECALHO = ("roteiro", "handler", "disparos")

# `== <formulario>.<handler>` e nada depois. O `$` e o que separa o disparo do
# `flechasapaClick` da sua linha de aviso com sufixo -- ver o cabecalho.
LINHA = re.compile(r"^\s*[0-9.]+\s+==\s+([A-Za-z_0-9]+\.[A-Za-z_0-9]+)\s*$")


class CoberturaError(RuntimeError):
    pass


def handlers_conhecidos() -> set[str]:
    return {f"{h['formulario']}.{h['handler']}" for h in S.le_handlers()}


def conta_trace(caminho: Path) -> dict[str, int]:
    """Quantas vezes cada handler disparou neste trace."""
    contagem: dict[str, int] = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        casou = LINHA.match(linha)
        if casou:
            contagem[casou.group(1)] = contagem.get(casou.group(1), 0) + 1
    return contagem


def colhe(raiz: Path) -> list[tuple[str, str, int]]:
    if not raiz.is_dir():
        raise CoberturaError(f"{raiz} nao e diretorio")
    linhas: list[tuple[str, str, int]] = []
    conhecidos = handlers_conhecidos()
    achou = False
    for sub in sorted(raiz.iterdir()):
        trace = sub / "port-trace.log"
        if not trace.is_file():
            continue
        achou = True
        for handler, n in sorted(conta_trace(trace).items()):
            if handler not in conhecidos:
                # `MainForm.FormCreate` e handler; `imagem: ...` nao e. O
                # filtro e pelo TSV dos 96, nao por heuristica de nome.
                continue
            linhas.append((sub.name, handler, n))
    if not achou:
        raise CoberturaError(
            f"nenhum port-trace.log sob {raiz} -- rode o `golden_run_laz.sh` "
            "antes; ver o cabecalho deste arquivo")
    return linhas


def le_tsv() -> list[dict]:
    if not TSV.is_file():
        raise CoberturaError(f"falta {TSV.relative_to(ROOT)}")
    linhas = TSV.read_text(encoding="utf-8").splitlines()
    if not linhas or tuple(linhas[0].split("\t")) != CABECALHO:
        raise CoberturaError(
            f"{TSV.name}: cabecalho tem de ser {'/'.join(CABECALHO)}")
    saida = []
    for i, bruto in enumerate(linhas[1:], start=2):
        if not bruto.strip():
            continue
        campos = bruto.split("\t")
        if len(campos) != 3:
            raise CoberturaError(f"{TSV.name}:{i}: esperava 3 colunas")
        saida.append({"roteiro": campos[0], "handler": campos[1],
                      "disparos": int(campos[2])})
    return saida


def roteiros_verdes() -> set[str]:
    """Roteiro com controle E golden PASSOU no registro da bateria."""
    if not BATERIA.is_file():
        raise CoberturaError(f"falta {BATERIA.relative_to(ROOT)}")
    por_roteiro: dict[str, set[str]] = {}
    linhas = BATERIA.read_text(encoding="utf-8").splitlines()[1:]
    for bruto in linhas:
        if not bruto.strip():
            continue
        campos = bruto.split("\t")
        if len(campos) < 3:
            continue
        if campos[2] == "PASSOU":
            por_roteiro.setdefault(campos[0], set()).add(campos[1])
    return {n for n, modos in por_roteiro.items()
            if {"controle", "golden"} <= modos}


def valida(linhas: list[dict]) -> None:
    conhecidos = handlers_conhecidos()
    verdes = roteiros_verdes()

    for linha in linhas:
        if linha["handler"] not in conhecidos:
            raise CoberturaError(
                f"{linha['handler']} nao esta entre os 96 do "
                "published_methods.tsv")
        if linha["disparos"] < 1:
            raise CoberturaError(
                f"{linha['roteiro']}/{linha['handler']}: disparos tem de ser "
                ">= 1 -- linha com zero e ausencia, e ausencia se escreve "
                "nao pondo a linha")
        roteiro = ROTEIROS / f"{linha['roteiro']}.txt"
        par = ROTEIROS / f"{linha['roteiro']}.port.txt"
        if not roteiro.is_file() or not par.is_file():
            raise CoberturaError(
                f"{linha['roteiro']}: falta o roteiro ou o par `.port` em "
                f"{ROTEIROS.relative_to(ROOT)}")
        if linha["roteiro"] not in verdes:
            raise CoberturaError(
                f"{linha['roteiro']} nao esta PASSOU nos dois modos do "
                f"{BATERIA.name} -- cobertura dentro de gate vermelho nao "
                "verifica nada")

    # A guarda que a licao do `check_edicao.py` pede: spec que cita este TSV
    # como evidencia tem de ter linha nele.
    cobertos = {linha["handler"] for linha in linhas}
    reclamam = []
    for arq in sorted(S.SPEC.glob("*.md")):
        if arq.name in {"GABARITO.md", "INDICE.md", "README.md"}:
            continue
        if TSV.name not in arq.read_text(encoding="utf-8"):
            continue
        chave = arq.stem
        if chave not in cobertos:
            reclamam.append(chave)
    if reclamam:
        raise CoberturaError(
            "spec cita o " + TSV.name + " como evidencia e nao tem linha "
            "nele: " + ", ".join(reclamam) + ". Citar regua e barato; ter "
            "disparo medido nao -- ver o cabecalho de " + GENERATOR)


def escreve(linhas: list[tuple[str, str, int]]) -> str:
    corpo = ["\t".join(CABECALHO)]
    corpo += [f"{r}\t{h}\t{n}" for r, h, n in sorted(linhas)]
    return "\n".join(corpo) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--colher", metavar="DIR",
                    help="le <DIR>/<roteiro>/port-trace.log e reescreve o TSV")
    ap.add_argument("--check", action="store_true",
                    help="valida o TSV versionado, offline")
    args = ap.parse_args(argv)

    try:
        if args.colher:
            linhas = colhe(Path(args.colher))
            TSV.write_text(escreve(linhas), encoding="utf-8")
            valida(le_tsv())
            print(f"  {TSV.name}: {len(linhas)} linha(s), "
                  f"{len({r for r, _h, _n in linhas})} roteiro(s)")
            return 0
        linhas = le_tsv()
        valida(linhas)
        if args.check:
            print(f"cobertura_gate: {TSV.name}: ok "
                  f"({len(linhas)} linhas, "
                  f"{len({x['handler'] for x in linhas})} handlers)")
        else:
            print(f"  {TSV.name}: {len(linhas)} linha(s) -- nada a regerar "
                  "sem `--colher` (trace nao e versionado)")
        return 0
    except (CoberturaError, S.SpecError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
