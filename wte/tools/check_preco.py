#!/usr/bin/env python3
"""A formula de preco bate com o oraculo, jogador a jogador? -- WTE-TASK-32.

A task pede *"acerto em 100% de uma amostra grande, nao numa amostra
escolhida"*, e essa frase e o motivo desta ferramenta existir: um gate golden
prova um TIME, e a formula tem de valer para a populacao.

## Como a amostra e colhida

O `MainForm.base_teamClick` do ORACULO grava um byte de preco por jogador na
imagem. Entao uma corrida dele sobre um time deixa 22 respostas do oraculo
gravadas -- legiveis com `cmp`, sem OCR e sem ler tela. Cada time e uma corrida.

O `wte/tests/dump_preco` calcula o preco de cada jogador pela formula do port e
imprime, na mesma linha, o byte que ESTA na imagem. Sobre uma imagem por onde o
oraculo passou, `preco` e a previsao e `custo` e a resposta -- e a conferencia e
uma comparacao de colunas.

## O que o `--check` mede, e o que ele NAO mede

Ele le o TSV versionado (`wte/re/preco.tsv`), escrito pela corrida, e confere:

1. toda linha com `medido` tem `previsto == medido`;
2. a amostra tem pelo menos `MINIMO_AMOSTRA` jogadores medidos, para "100%" nao
   ser dito sobre tres linhas;
3. o slot 22 NUNCA aparece medido -- e a regra que a WTE-TASK-32 mediu e a
   CORR-WTE-095 explicou: o original calcula o preco do 23o jogador certo e o
   perde na saida bufferizada, abaixo do `fputc`. Bug do original, reproduzido
   de proposito (WTE-TASK-35). Se um dia aparecer medido, a regra caiu e o
   `ULTIMO_SLOT_PRECADO` do handler esta errado.

Ele NAO reroda o oraculo: isso precisa de Wine e do `:98`, e `--check` roda em
qualquer clone. A medida e versionada; a corrida nao.

## Uma armadilha desta ferramenta

O byte de preco de uma imagem VIRGEM nao e resposta de ninguem -- e o que o
jogo trouxe de fabrica. Comparar contra ele daria divergencia em quase toda
linha e nao significaria nada. Por isso o TSV so aceita linha `medido` para
(time, slot) que o oraculo de fato gravou, e a coluna existe separada da
`custo_virgem` justamente para os dois numeros nao se confundirem.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TSV = ROOT / "wte" / "re" / "preco.tsv"
CABECALHO = ("rom", "time", "slot", "soma", "posicao", "previsto", "medido")

GENERATOR = "wte/tools/check_preco.py"

# Abaixo disto, "100% de acerto" nao e afirmacao sobre populacao nenhuma.
MINIMO_AMOSTRA = 40

# O slot que o oraculo nunca preca -- ver o cabecalho do
# `impl/ep2002_mainform.base_teamClick.inc` e a CORR-WTE-095.
SLOT_NUNCA_PRECADO = 22


class PrecoError(RuntimeError):
    pass


def le() -> list[dict]:
    if not TSV.is_file():
        raise PrecoError(f"falta {TSV.relative_to(ROOT)}")
    linhas = TSV.read_text(encoding="utf-8").splitlines()
    if not linhas or tuple(linhas[0].split("\t")) != CABECALHO:
        raise PrecoError(f"{TSV.name}: cabecalho tem de ser "
                         + "/".join(CABECALHO))
    saida = []
    for i, bruto in enumerate(linhas[1:], start=2):
        if not bruto.strip():
            continue
        campos = bruto.split("\t")
        if len(campos) != len(CABECALHO):
            raise PrecoError(f"{TSV.name}:{i}: esperava "
                             f"{len(CABECALHO)} colunas")
        d = dict(zip(CABECALHO, campos))
        for c in ("time", "slot", "soma", "posicao", "previsto"):
            d[c] = int(d[c])
        d["medido"] = None if d["medido"] == "-" else int(d["medido"])
        saida.append(d)
    return saida


def valida(linhas: list[dict]) -> tuple[int, int]:
    medidos = [x for x in linhas if x["medido"] is not None]
    if len(medidos) < MINIMO_AMOSTRA:
        raise PrecoError(
            f"amostra medida tem {len(medidos)} jogador(es), minimo "
            f"{MINIMO_AMOSTRA} -- 'acerto em 100%' sobre menos que isso nao e "
            "afirmacao sobre populacao nenhuma")

    erram = [x for x in medidos if x["previsto"] != x["medido"]]
    if erram:
        amostra = "; ".join(
            f"{x['rom']} time {x['time']} slot {x['slot']} soma {x['soma']}: "
            f"previsto {x['previsto']}, oraculo {x['medido']}"
            for x in erram[:5])
        raise PrecoError(
            f"{len(erram)} de {len(medidos)} divergem. {amostra}"
            + (" ..." if len(erram) > 5 else "")
            + ". A coluna `soma` diz onde procurar: soma igual e preco "
              "diferente e erro de formula; soma diferente e erro na leitura "
              "dos atributos.")

    intrusos = [x for x in medidos if x["slot"] == SLOT_NUNCA_PRECADO]
    if intrusos:
        raise PrecoError(
            f"o slot {SLOT_NUNCA_PRECADO} aparece medido em "
            f"{len(intrusos)} linha(s), e o oraculo nunca o preca. Se a regra "
            f"caiu, o `ULTIMO_SLOT_PRECADO` do handler esta errado -- ver a "
            f"CORR-WTE-095 e o cabecalho de {GENERATOR}.")

    return len(medidos), len({(x["rom"], x["time"]) for x in medidos})


# O ultimo slot que o oraculo grava. Estabelecido de dois jeitos independentes,
# e nenhum deles e o limite do laco: o laco vai ate 22 (`cmp [ebp-0x2c],0x17`),
# e para o slot 22 o oraculo LE o byte condicional e nao o grava -- medido por
# `strace` na CORR-WTE-095. O que sustenta o 21 e (1) a FAIXA de bytes que
# mudou, em seis times, e (2) o plantio: `0xFF` posto em 3067472 antes da
# corrida continua `0xFF` depois.
ULTIMO_SLOT_PRECADO = 21

DUMP = ROOT / "wte" / "tests" / "dump_preco"

# Onde mora o byte de preco do slot 0 do time 0, e o passo entre times. Sao os
# mesmos numeros do `OffsetsDoJogador` do `wte_ficha.pas`; ficam aqui para o
# coletor poder olhar a faixa certa sem carregar a imagem inteira.
CONDICIONAL_BASE = 3067404
SLOTS_POR_TIME = 23


def gravou(virgem: Path, depois: Path, time_: int) -> bool:
    """Algum byte da faixa de preco deste time mudou?"""
    inicio = CONDICIONAL_BASE + SLOTS_POR_TIME * time_ + 2 * (time_ // 56)
    with virgem.open("rb") as a, depois.open("rb") as b:
        a.seek(inicio); b.seek(inicio)
        return a.read(SLOTS_POR_TIME) != b.read(SLOTS_POR_TIME)


def colhe(diretorio: Path) -> list[str]:
    """Le `amostra-<rom>-<time>.bin` e monta as linhas do TSV.

    Cada arquivo e uma imagem por onde o `base_teamClick` do ORACULO passou,
    sobre UM time. O `dump_preco` diz, por jogador, o preco que o port preve e
    o byte que ficou na imagem.
    """
    import re
    import subprocess
    if not DUMP.is_file():
        raise PrecoError(
            f"falta {DUMP.relative_to(ROOT)} -- compile com "
            "`fpc -Mobjfpc -Fusrc -FUbuild/units -otests/dump_preco "
            "tests/dump_preco.pas`")
    saida: list[str] = []
    achou = False
    for arq in sorted(diretorio.glob("amostra-*-*.bin")):
        m = re.fullmatch(r"amostra-(.+)-([0-9]+)", arq.stem)
        if not m:
            continue
        rom, time_ = m.group(1), int(m.group(2))
        achou = True
        # O ORACULO RODOU NESTA IMAGEM? Sem essa pergunta o coletor credita ao
        # oraculo os bytes DE FABRICA, que e a armadilha descrita no cabecalho
        # -- e ela nao e hipotetica: a ROM europeia nao hospeda este oraculo (o
        # `wte.exe` morre na troca de time, CORR-WTE-044), a corrida sobre ela
        # gravou ZERO bytes, e a primeira versao deste coletor comparou a
        # formula contra os precos de fabrica e acusou 21 divergencias.
        virgem = ROOT / "roms" / f"{rom}.bin"
        if not virgem.is_file():
            raise PrecoError(
                f"{arq.name}: falta a ROM virgem {virgem.relative_to(ROOT)} "
                "-- sem ela nao da para saber se o oraculo gravou")
        if not gravou(virgem, arq, time_):
            print(f"  {arq.name}: o oraculo nao gravou nada -- linhas sem "
                  f"`medido`", file=sys.stderr)
            escrever_medido = False
        else:
            escrever_medido = True
        p = subprocess.run([str(DUMP), str(arq), str(time_), str(time_)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise PrecoError(f"{arq.name}: dump_preco saiu {p.returncode}: "
                             f"{p.stderr.strip()[:200]}")
        for linha in p.stdout.splitlines()[1:]:
            t_, slot, soma, pos, previsto, custo = linha.split("\t")
            medido = (custo if escrever_medido
                      and int(slot) <= ULTIMO_SLOT_PRECADO else "-")
            saida.append("\t".join((rom, t_, slot, soma, pos, previsto,
                                     medido)))
    if not achou:
        raise PrecoError(f"nenhum amostra-<rom>-<time>.bin em {diretorio}")
    return saida


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--colher", metavar="DIR",
                    help="le as imagens do oraculo e reescreve o TSV")
    args = ap.parse_args(argv)
    try:
        if args.colher:
            corpo = ["\t".join(CABECALHO)] + colhe(Path(args.colher))
            TSV.write_text("\n".join(corpo) + "\n", encoding="utf-8")
        linhas = le()
        n, times = valida(linhas)
    except PrecoError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(f"check_preco: {TSV.name}: ok ({n} jogadores medidos em {times} "
          f"time(s), 100% de acerto; {len(linhas)} linhas no total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
