#!/usr/bin/env python3
"""O `TComboBox` da LCL dispara `OnChange` quando o codigo mexe nele?

Da [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md), criterio
"comportamento de `OnChange` na carga decidido e testado". **Nao escreve
arquivo** -- mesmo contrato do [`check_lcl_props.py`](check_lcl_props.py) e do
[`check_barras.py`](check_barras.py): confere e sai 2 quando diverge.

## Por que isso e conferencia de build e nao nota de rodape

O Win32 nao dispara `CBN_SELCHANGE` em `SetCurSel`, entao o
`lista_equiposChange` do original pode mexer em combo sem se auto-chamar. Se a
LCL disparar `OnChange` em `ItemIndex :=`, o mesmo corpo no port recarrega duas
vezes ou entra em recursao -- e o sintoma nao e travamento, e uma carga a mais
que ninguem ve.

O `newWe2002` pagou essa exata armadilha do outro lado: o Qt **dispara**
`currentIndexChanged` em `setCurrentIndex` enquanto o MFC nao disparava, e as
cargas de time precisaram de `QSignalBlocker`. gtk2 nao e Qt e nao e Win32, e a
resposta e propriedade do **widgetset instalado** -- pode mudar num upgrade de
Lazarus sem que uma linha deste repositorio mude. Por isso ela e remedida a
cada `make -C wte check`, e nao lida de um documento.

## O que ele faz

Compila e roda [`../tests/test_lcl_combo.pas`](../tests/test_lcl_combo.pas),
que exercita cinco situacoes, e confronta a saida com o `ESPERADO` abaixo.
Divergencia reprova com o caso nomeado.

**Sem `fpc`, sem a LCL ou sem `DISPLAY` o script PULA e diz o que deixou de
medir**, como o `test_gen_tables_pas.py` faz sem `fpc`/`g++`. Verde sem nada
medido seria pior que vermelho.

Uso:

    python3 wte/tools/check_lcl_combo.py
    python3 wte/tools/check_lcl_combo.py --check   # o que `make -C wte check` roda
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_lcl_props  # noqa: E402  -- caminho_da_lcl e LCL_BASE
import dfm2lfm  # noqa: E402  -- LCL_VERSAO, o pino de versao

ROOT = Path(__file__).resolve().parent.parent.parent
FONTE = ROOT / "wte" / "tests" / "test_lcl_combo.pas"
REL_FONTE = "wte/tests/test_lcl_combo.pas"
GENERATOR = "wte/tools/check_lcl_combo.py"

# O resultado medido em 2026-08-11, gtk2, Lazarus 3.0 / FPC 3.2.2.
#
# `nao-disparou` nos cinco: a LCL se comporta como o Win32 do original, e NAO
# como o Qt do newWe2002. Consequencia direta -- os corpos da fase 4 mexem em
# `ItemIndex` sem bloquear sinal, e o codigo fica igual ao que a spec descreve.
# Se um upgrade inverter qualquer linha disto, o corpo dos handlers de carga
# precisa de revisao, e e o que este script existe para avisar.
ESPERADO = {
    "ItemIndex-atribuido": "nao-disparou",
    "ItemIndex-igual-ao-atual": "nao-disparou",
    "Items-Clear-com-selecao": "nao-disparou",
    "ItemIndex-apos-reencher": "nao-disparou",
    "ItemIndex-menos-um": "nao-disparou",
    # Medido na decima sexta passagem da WTE-TASK-26, e a resposta e OPOSTA a
    # do combo: `TScrollBar.Position :=` DISPARA `OnChange`, e so quando o
    # valor muda de verdade. Consequencia direta: o `PreencheFicha` reentra nos
    # dezesseis `barrhabScroll` ao encher a ficha, e cada reentrada reescreve
    # o rotulo, a largura e a cor que o preenchimento acabou de escrever --
    # com o mesmo valor, entao a tela nao muda, mas uma contagem de trace muda.
    # E a mesma resposta que o `TTrackBar` deu na segunda passagem.
    "ScrollBar-Position-atribuida": "disparou",
    "ScrollBar-Position-igual-a-atual": "nao-disparou",
    # O `TUpDown` NAO dispara o `OnClick` por atribuicao, entao os doze
    # `flechasapa` do segundo laco nao reentram.
    "UpDown-Position-atribuida": "nao-disparou",
}

WIDGETSET = "gtk2"

# O display onde a medicao roda. Uma variavel por ferramenta, com `:98` de
# default, e a forma que o repositorio adotou quando saiu do `:99` -- a mesma
# do `roteiro.sh` e do `compara_tela.sh`. O numero mora aqui, e so aqui.
ALVO = os.environ.get("WTE_DISPLAY", ":98")


class ComboError(Exception):
    """Divergencia medida, sempre com o caso nomeado."""


def caminhos_de_unidade(lcl: Path) -> list[str]:
    """Os `-Fu` que um programa LCL de console precisa."""
    raiz = lcl.parent
    alvo = "x86_64-linux"
    candidatos = [
        lcl / "units" / alvo / WIDGETSET,
        lcl / "units" / alvo,
        raiz / "components" / "lazutils" / "lib" / alvo,
        raiz / "packager" / "units" / alvo,
    ]
    faltando = [c for c in candidatos if not c.is_dir()]
    if faltando:
        raise ComboError(
            "a LCL instalada nao tem " + ", ".join(str(c) for c in faltando)
            + f" -- o widgetset `{WIDGETSET}` esta compilado?")
    return [f"-Fu{c}" for c in candidatos]


def display() -> tuple[str, str] | None:
    """`(DISPLAY, XAUTHORITY)` do Xvfb `ALVO`, ou `None` se ele nao esta de pe.

    A regra do repositorio e dura: toda execucao com GUI acontece no `ALVO`
    (`:98` de default, `WTE_DISPLAY` para mover), e o `:1` e a sessao real do
    usuario. Este script **nunca** cai para o `DISPLAY` do shell -- sem o
    servidor ele pula.

    O `-auth` e OPCIONAL de proposito. Subido por `xvfb-run`, o servidor tem
    cookie proprio e sem apontar o `XAUTHORITY` para ele o gtk2 morre com
    `Invalid MIT-MAGIC-COOKIE-1 key`; subido a mao, nao ha cookie nenhum e
    exigir um faria o script PULAR dizendo que nao ha servidor -- diagnostico
    que manda procurar no lugar errado. Devolve cadeia vazia quando nao ha.
    """
    try:
        saida = subprocess.run(["ps", "-o", "args=", "-C", "Xvfb"],
                               capture_output=True, text=True).stdout
    except OSError:
        return None
    linha = next((l for l in saida.splitlines()
                  if f"Xvfb {ALVO} " in l), None)
    if linha is None:
        return None
    m = re.search(r"-auth (\S+)", linha)
    return ALVO, (m.group(1) if m else "")


def medir() -> dict[str, str]:
    lcl = check_lcl_props.caminho_da_lcl(dfm2lfm.LCL_VERSAO)
    fpc = shutil.which("fpc")
    if not fpc:
        raise FileNotFoundError("fpc")
    tela = display()
    if tela is None:
        raise FileNotFoundError(f"Xvfb {ALVO}")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [fpc, "-MObjFPC", "-Sh", *caminhos_de_unidade(lcl),
             f"-FE{tmp}", f"-FU{tmp}", str(FONTE)],
            check=True, capture_output=True)
        ambiente = dict(os.environ)
        ambiente["DISPLAY"], xauth = tela
        if xauth:
            ambiente["XAUTHORITY"] = xauth
        else:
            ambiente.pop("XAUTHORITY", None)
        saida = subprocess.run([str(Path(tmp) / FONTE.stem)], check=True,
                               capture_output=True, text=True,
                               env=ambiente).stdout
    lido: dict[str, str] = {}
    for linha in saida.splitlines():
        if not linha.strip():
            continue
        partes = linha.split("\t")
        if len(partes) != 2:
            raise ComboError(f"{REL_FONTE}: linha ilegivel {linha!r}")
        lido[partes[0]] = partes[1]
    return lido


def confere(lido: dict[str, str]) -> list[str]:
    problemas = []
    for caso, esperado in ESPERADO.items():
        if caso not in lido:
            problemas.append(f"{caso}: ausente da saida do programa")
        elif lido[caso] != esperado:
            problemas.append(
                f"{caso}: a LCL {lido[caso]}, e o codigo da fase 4 foi escrito "
                f"contando que ela {esperado}")
    sobrando = sorted(set(lido) - set(ESPERADO))
    if sobrando:
        problemas.append(
            "casos no programa sem veredito aqui: " + ", ".join(sobrando)
            + " -- caso novo sem esperado e caso nao medido")
    return problemas


def main(argv: list[str]) -> int:
    for arg in argv:
        if arg != "--check":
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        lido = medir()
    except FileNotFoundError as exc:
        print(f"check_lcl_combo: PULADO (sem {exc}) -- o disparo de "
              f"`OnChange` da LCL nao foi medido nesta rodada")
        return 0
    except check_lcl_props.CheckError as exc:
        print(f"check_lcl_combo: PULADO ({exc})")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"ERRO: {REL_FONTE} nao compilou ou nao rodou", file=sys.stderr)
        print((exc.stderr or b"").decode("utf-8", "replace")[-2000:],
              file=sys.stderr)
        return 2
    except ComboError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    problemas = confere(lido)
    if problemas:
        print(f"{REL_FONTE}: a LCL mudou de comportamento", file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        print("os corpos de wte/src/impl/ dos handlers de carga precisam de "
              "revisao antes de isto virar verde de novo", file=sys.stderr)
        return 2
    print(f"check_lcl_combo: {len(ESPERADO)} casos, LCL {dfm2lfm.LCL_VERSAO}/"
          f"{WIDGETSET}: `TComboBox` e `TUpDown` nao disparam por "
          "atribuicao; `TScrollBar.Position :=` DISPARA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
