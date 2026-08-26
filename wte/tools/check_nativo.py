#!/usr/bin/env python3
"""O `nativo.md` confere com o `nativo.tsv`? -- CORR-WTE-119.

    python3 wte/tools/check_nativo.py            # relata
    python3 wte/tools/check_nativo.py --check    # o que `make -C wte check` roda

## Por que este script existe, e por que ele nao gera o markdown

A condicao 3 da definicao de pronto (plano, secao 0) e medida pelo
[`nativo_check.sh`](nativo_check.sh), que escreve sete linhas em
[`../re/nativo.tsv`](../re/nativo.tsv). O [`../re/nativo.md`](../re/nativo.md) e
escrito A MAO -- e deve continuar sendo, pelo mesmo motivo do
`divergencias.md`: metade dele e *decisao* (por que a medida `carga` existe, o
que a afirmacao nao e), e prosa nao se gera.

O que ele NAO podia continuar sendo e nao conferido. O `.md` REPETE os sete
valores numa tabela propria, e ate esta correcao nada comparava as duas. Uma
corrida futura que mudasse um valor -- 56 bibliotecas viram 58 ao trocar de
GTK, a janela muda de tamanho -- atualizaria o TSV e deixaria o `.md`
afirmando o valor velho, EM VERDE, num documento que sustenta uma das tres
condicoes.

O `nativo.md` era o unico documento de fechamento sem `--check` nem conferidor:
os `fase-1..4.md`, o `golden.md`, o `buffers.md`, o `carregado.md` e o
`retorno.md` nascem de gerador; o `divergencias.md` e a mao mais o
`check_divergencias.py`. Este e o par que faltava.

## A comparacao e NORMALIZADA, e isso e escolha

O TSV e saida de shell, em ASCII: `522x475, titulo conferido`. O `.md` e para
ler: `522×475, título conferido`, com crases em volta dos nomes de binario.
Exigir igualdade crua reprovaria a arvore de hoje e empurraria o `.md` para a
feiura do TSV -- o que nao e o objetivo.

Entao: tira crase, troca `×` por `x`, tira acento, e exige que o valor do TSV
seja SUBSTRING do valor do `.md`. Assim o `.md` pode acrescentar contexto (`...
ausentes no namespace`) e nao pode contradizer: trocar 56 por 58 no TSV derruba
o gate na hora.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TSV = RAIZ / "wte" / "re" / "nativo.tsv"
MD = RAIZ / "wte" / "re" / "nativo.md"


class NativoError(Exception):
    pass


def normaliza(s: str) -> str:
    """Sem crase, sem `×`, sem acento, sem espaco duplo, em caixa baixa."""
    s = s.replace("`", "").replace("×", "x").replace("**", "")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()


def le_tsv(caminho: Path) -> list[dict]:
    if not caminho.exists():
        raise NativoError(f"falta {caminho.name}")
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    if not linhas or linhas[0].split("\t") != ["medida", "valor", "veredito"]:
        raise NativoError(f"{caminho.name}: cabecalho inesperado")
    medidas = []
    for n, linha in enumerate(linhas[1:], start=2):
        if not linha.strip():
            continue
        campos = linha.split("\t")
        if len(campos) != 3:
            raise NativoError(f"{caminho.name}:{n}: esperava 3 campos")
        medidas.append(dict(zip(("medida", "valor", "veredito"), campos)))
    return medidas


def le_md(caminho: Path) -> list[dict]:
    """As linhas da tabela cujo primeiro campo e uma medida entre crases.

    O `.md` tem OUTRA tabela antes desta -- a dos caminhos mascarados, cujo
    primeiro campo tambem vem entre crases (`/var/lib/flatpak`). O que separa as
    duas e o numero de colunas: a de medidas tem tres.
    """
    if not caminho.exists():
        raise NativoError(f"falta {caminho.name}")
    achados = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([a-z0-9-]+)` \| (.+?) \| (.+?) \|$", linha)
        if m:
            achados.append({"medida": m.group(1), "valor": m.group(2),
                            "veredito": m.group(3)})
    return achados


def mede() -> dict:
    tsv = le_tsv(TSV)
    md = le_md(MD)
    problemas: list[str] = []

    por_nome = {x["medida"]: x for x in md}
    for linha in tsv:
        nome = linha["medida"]

        # (3) veredito que nao e `ok` derruba o gate, e nao espera leitura.
        # A condicao 3 e de FECHAMENTO: um `reprovou` que ficou no arquivo
        # significa que ela nao esta cumprida, e o `make -C wte check` tem de
        # dizer isso.
        if linha["veredito"] != "ok":
            problemas.append(
                f"{nome}: o veredito no TSV e `{linha['veredito']}`, nao `ok`. "
                "A condicao 3 da definicao de pronto nao esta cumprida -- "
                "isso e resultado, e o gate nao pode ficar verde por cima dele.")

        # (1) medida do TSV ausente do `.md`, ou com valor que o contradiz.
        if nome not in por_nome:
            problemas.append(
                f"{nome}: esta no {TSV.name} e NAO na tabela do {MD.name}. O "
                "documento publica sete medidas; uma que so existe no TSV nao "
                "chega a quem le.")
            continue

        alvo = por_nome[nome]
        if normaliza(linha["valor"]) not in normaliza(alvo["valor"]):
            problemas.append(
                f"{nome}: o TSV mede `{linha['valor']}` e o {MD.name} publica "
                f"`{alvo['valor']}`. O `.md` promete que todo numero dele vem "
                "de ferramenta; numero que a ferramenta nao mede mais e prosa "
                "vencida em documento de fechamento.")
        if normaliza(linha["veredito"]) != normaliza(alvo["veredito"]):
            problemas.append(
                f"{nome}: veredito `{linha['veredito']}` no TSV e "
                f"`{alvo['veredito']}` no {MD.name}")

    # (2) o `.md` citando medida que o TSV nao tem.
    nomes_tsv = {x["medida"] for x in tsv}
    for linha in md:
        if linha["medida"] not in nomes_tsv:
            problemas.append(
                f"{linha['medida']}: esta na tabela do {MD.name} e NAO no "
                f"{TSV.name}. Medida publicada que ferramenta nenhuma produz e "
                "afirmacao sem fonte.")

    return {"tsv": tsv, "md": md, "problemas": problemas}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.parse_args(argv)

    try:
        m = mede()
    except NativoError as e:
        print(f"check_nativo: {e}", file=sys.stderr)
        return 2
    if m["problemas"]:
        for p in m["problemas"]:
            print(f"check_nativo: {p}", file=sys.stderr)
        return 2
    print(f"check_nativo: {MD.relative_to(RAIZ)}: ok -- "
          f"{len(m['tsv'])} medida(s) do TSV publicadas, "
          f"{sum(1 for x in m['tsv'] if x['veredito'] == 'ok')} com veredito `ok`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
