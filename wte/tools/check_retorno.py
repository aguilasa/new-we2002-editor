#!/usr/bin/env python3
"""O que a tecla `Return` alcanca em cada um dos 18 formularios, e a ordem de
tabulacao dos dois lados.

Gera `wte/re/retorno.md` e `wte/re/retorno.tsv` — produto da
[WTE-TASK-37](../../docs/tasks/37-reconferencia-de-ui.md).

## O risco que ele mede, e por que ele nao e hipotetico

O `newWe2002` levou a mordida na Fase 5 do port Qt: `PUSHBUTTON` do `.rc` nao
carrega "sou o botao default", e dentro de um `QDialog` o Qt torna TODO botao
`autoDefault` — `Return` clicava o primeiro da ordem de tabulacao, e num dos
dialogos o candidato aplicava formacao predefinida sobre o time selecionado.

Aqui o risco irmao existe pelo mesmo motivo (`estrategia.lista_formacionesClick`
e destrutivo) e a resposta e outra, porque o formato e outro: `Default` e
`Cancel` sao propriedades EXPLICITAS no `.dfm` e no `.lfm`, e o `dfm2lfm.py` as
copia verbatim. Este script prova as duas metades:

1. o botao `Default` de cada formulario e o MESMO nos dois lados, e o mesmo
   vale para o `Cancel`;
2. o handler que esse botao dispara nao grava na imagem — medido no
   `## Bytes tocados` da spec dele, nao presumido.

E de quebra confere a **ordem de tabulacao**: `TabOrder` por controle, na ordem
em que a VCL e a LCL a consomem. Ordem diferente muda para onde o `Tab` leva o
foco, que e a outra metade da pergunta da task.

## O vocabulario de `bytes`

Sai da secao `## Bytes tocados` da spec do handler, nao de palpite:

| valor | quando |
|---|---|
| `nenhum` | a secao comeca com `**Nenhum` |
| `arquivo` | a secao diz `Na imagem de CD: nenhum` — grava fora da imagem |
| `imagem` | qualquer outra coisa: a secao descreve escrita na imagem |
| `sem handler` | o botao nao tem `OnClick`; so devolve `ModalResult` |
| `sem spec` | ha handler e nao ha spec — nao deve acontecer com 96 de 96 |

## Como refazer

    python3 wte/tools/check_retorno.py
    python3 wte/tools/check_retorno.py --check   # o que `make -C wte check` roda

Sai 2 quando o commitado diverge do gerado.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DFM = RAIZ / "wte" / "re" / "dfm"
LFM = RAIZ / "wte" / "forms"
SPEC = RAIZ / "wte" / "re" / "spec"
METODOS = RAIZ / "wte" / "re" / "published_methods.tsv"
SAIDA_MD = RAIZ / "wte" / "re" / "retorno.md"
SAIDA_TSV = RAIZ / "wte" / "re" / "retorno.tsv"

# O `.lfm` de cada formulario. O nome do arquivo nao e o nome do formulario --
# o `dfm2lfm.py` emite `ep2002_<curto>.lfm`, e o mapa dele e a fonte.
RE_RAIZ = re.compile(r"^object (\w+): T\w+$")


class RetornoError(Exception):
    pass


def le_arvore(caminho: Path) -> list[dict]:
    """Os objetos do `.dfm`/`.lfm`, em ordem de arquivo.

    Parser proprio, e de proposito: o `ler_dfm` do `dfm2lfm.py` recusa o `.lfm`,
    onde o blob e hexadecimal cru e nao a referencia `{blob ...}` que ele
    conhece. O que se quer aqui e um subconjunto minusculo -- nome, classe e
    quatro propriedades --, e um parser que ATRAVESSA o bloco `{...}` sem tentar
    entende-lo serve aos dois formatos com a mesma linha.
    """
    objetos: list[dict] = []
    atual: dict | None = None
    dentro_de_blob = False
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        corte = linha.strip()
        if dentro_de_blob:
            if corte == "}":
                dentro_de_blob = False
            continue
        if corte.endswith("= {"):
            dentro_de_blob = True
            continue
        # O nome e OPCIONAL: um dos 459 objetos dos 18 formularios -- um
        # `TStaticText` do `MainForm` -- nao tem nome, e um parser que exija
        # nome o engole em silencio. A WTE-TASK-12 contou 37 `TStaticText`
        # justamente porque o incluiu.
        m = re.match(r"^object (?:(\w+): )?(\w+)$", corte)
        if m:
            atual = {"nome": m.group(1) or "", "classe": m.group(2),
                     "raiz": not objetos}
            objetos.append(atual)
            continue
        if atual is None:
            continue
        m = re.match(r"^(\w+) = (.+)$", corte)
        if m and m.group(1) in ("TabOrder", "TabStop", "Default", "Cancel",
                               "ModalResult", "Caption", "OnClick"):
            atual.setdefault(m.group(1), m.group(2))
    if not objetos:
        raise RetornoError(f"{caminho}: nenhum objeto")
    return objetos


def tabordem(objetos: list[dict]) -> str:
    """`nome:TabOrder` dos controles que a declaram, na ordem do arquivo.

    A ordem do ARQUIVO e nao a do numero: dois irmaos podem repetir `TabOrder`
    em pais diferentes, e ordenar pelo numero misturaria as duas cadeias.
    """
    return ",".join(f"{o['nome']}:{o['TabOrder']}"
                    for o in objetos if "TabOrder" in o)


def unico(objetos: list[dict], prop: str) -> dict | None:
    achados = [o for o in objetos if o.get(prop) == "True"]
    if len(achados) > 1:
        nomes = ", ".join(o["nome"] for o in achados)
        raise RetornoError(f"mais de um {prop} = True: {nomes}")
    return achados[0] if achados else None


def le_metodos() -> dict[tuple[str, str], str]:
    """(formulario, componente) -> handler de `OnClick`."""
    fora: dict[tuple[str, str], str] = {}
    linhas = METODOS.read_text(encoding="utf-8").splitlines()
    for linha in linhas[1:]:
        col = linha.split("\t")
        if len(col) < 5 or col[4] != "OnClick":
            continue
        for comp in col[3].split(","):
            fora[(col[2], comp.strip())] = col[1]
    return fora


SECAO = re.compile(r"^## Bytes tocados\s*$")


def bytes_do_handler(formulario: str, handler: str) -> tuple[str, str]:
    """(classificacao, primeira linha da secao) da spec do handler."""
    caminho = SPEC / f"{formulario}.{handler}.md"
    if not caminho.exists():
        return "sem spec", ""
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    corpo: list[str] = []
    dentro = False
    for linha in linhas:
        if SECAO.match(linha):
            dentro = True
            continue
        if dentro and linha.startswith("## "):
            break
        if dentro and linha.strip():
            corpo.append(linha.strip())
    if not corpo:
        return "sem spec", ""
    texto = " ".join(corpo)
    primeira = corpo[0]
    if primeira.startswith("**Nenhum"):
        return "nenhum", primeira
    if "imagem de CD: nenhum" in texto:
        return "arquivo", primeira
    return "imagem", primeira


def lfm_do_formulario(nome: str) -> Path:
    """O `.lfm` cujo objeto raiz tem esse nome."""
    for caminho in sorted(LFM.glob("*.lfm"), key=lambda p: p.as_posix()):
        primeira = caminho.read_text(encoding="utf-8",
                                     errors="replace").splitlines()[0]
        m = RE_RAIZ.match(primeira.strip())
        if m and m.group(1) == nome:
            return caminho
    raise RetornoError(f"nenhum .lfm com o formulario {nome}")


COLUNAS = ("formulario", "default", "default_evento", "default_modalresult",
           "bytes", "cancel", "cancel_modalresult", "controles_tabordem",
           "tabordem_igual")


def mede() -> list[dict]:
    metodos = le_metodos()
    linhas = []
    for caminho in sorted(DFM.glob("*.dfm"), key=lambda p: p.as_posix()):
        objetos = le_arvore(caminho)
        formulario = objetos[0]["nome"]
        objetos_lfm = le_arvore(lfm_do_formulario(formulario))

        d = unico(objetos, "Default")
        d_lfm = unico(objetos_lfm, "Default")
        c = unico(objetos, "Cancel")
        c_lfm = unico(objetos_lfm, "Cancel")
        for lado, a, b in (("Default", d, d_lfm), ("Cancel", c, c_lfm)):
            na = a["nome"] if a else None
            nb = b["nome"] if b else None
            if na != nb:
                raise RetornoError(
                    f"{formulario}: {lado} e {na} no DFM e {nb} no LFM -- o "
                    "dfm2lfm.py deixou de copiar a propriedade")

        evento = metodos.get((formulario, d["nome"])) if d else None
        if d and not evento and d.get("OnClick"):
            evento = d["OnClick"]
        if evento:
            classe, primeira = bytes_do_handler(formulario, evento)
        else:
            classe, primeira = ("sem handler", "")

        linhas.append({
            "formulario": formulario,
            "default": d["nome"] if d else "—",
            "default_evento": evento or "—",
            "default_modalresult": (d.get("ModalResult", "—") if d else "—"),
            "bytes": classe,
            "cancel": c["nome"] if c else "—",
            "cancel_modalresult": (c.get("ModalResult", "—") if c else "—"),
            "controles_tabordem": str(sum(1 for o in objetos
                                          if "TabOrder" in o)),
            "tabordem_igual": ("sim" if tabordem(objetos) ==
                               tabordem(objetos_lfm) else "NAO"),
            "_evidencia": primeira,
        })
    return linhas


def render(linhas: list[dict]) -> tuple[str, str]:
    tsv = ["\t".join(COLUNAS)]
    for l in linhas:
        tsv.append("\t".join(l[c] for c in COLUNAS))

    destrutivos = [l for l in linhas if l["bytes"] == "imagem"]
    diferentes = [l for l in linhas if l["tabordem_igual"] != "sim"]
    com_default = [l for l in linhas if l["default"] != "—"]

    md = [
        "# `re/retorno.md` — o que o `Return` alcança, e a ordem de tabulação",
        "",
        "Gerado por [`../tools/check_retorno.py`](../tools/check_retorno.py) a "
        "partir dos 18 `.dfm`, dos 18 `.lfm`, de "
        "[`published_methods.tsv`](published_methods.tsv) e das specs de "
        "[`spec/`](spec). **Não editar à mão:**",
        "",
        "```sh",
        "python3 wte/tools/check_retorno.py",
        "python3 wte/tools/check_retorno.py --check",
        "```",
        "",
        "A tabela está em [`retorno.tsv`](retorno.tsv); este arquivo é a "
        "leitura dela. **Todo número daqui saiu do script.**",
        "",
        "## Resumo",
        "",
        "| Medida | Valor |",
        "|---|---:|",
        f"| Formulários | {len(linhas)} |",
        f"| Com botão `Default` | {len(com_default)} |",
        f"| Cujo `Default` grava na imagem | {len(destrutivos)} |",
        f"| Ordem de tabulação divergente entre DFM e LFM | {len(diferentes)} |",
        "",
        "## Por formulário",
        "",
        "| Formulário | `Default` | handler | `ModalResult` | bytes | "
        "`Cancel` | controles com `TabOrder` | ordem igual |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for l in linhas:
        md.append(
            f"| `{l['formulario']}` | "
            + (f"`{l['default']}`" if l["default"] != "—" else "—") + " | "
            + (f"`{l['default_evento']}`" if l["default_evento"] != "—" else "—")
            + f" | {l['default_modalresult']} | {l['bytes']} | "
            + (f"`{l['cancel']}`" if l["cancel"] != "—" else "—")
            + f" | {l['controles_tabordem']} | {l['tabordem_igual']} |")
    md += [
        "",
        "## A evidência de cada `bytes`",
        "",
        "A primeira linha da seção `## Bytes tocados` da spec do handler — é "
        "dela que a classificação sai.",
        "",
    ]
    for l in linhas:
        if l["default_evento"] == "—":
            continue
        md.append(f"- **`{l['formulario']}.{l['default_evento']}`** "
                  f"(`{l['bytes']}`): {l['_evidencia']}")
    md.append("")
    return "\n".join(md) + "\n", "\n".join(tsv) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    try:
        linhas = mede()
    except RetornoError as e:
        print(f"check_retorno: {e}", file=sys.stderr)
        return 2

    md, tsv = render(linhas)
    if args.check:
        rc = 0
        for caminho, texto in ((SAIDA_MD, md), (SAIDA_TSV, tsv)):
            atual = (caminho.read_text(encoding="utf-8")
                     if caminho.exists() else None)
            rel = caminho.relative_to(RAIZ)
            if atual != texto:
                print(f"check_retorno: {rel}: DIVERGE -- rode sem --check",
                      file=sys.stderr)
                rc = 2
            else:
                print(f"check_retorno: {rel}: ok")
        if rc == 0:
            destrutivos = sum(1 for l in linhas if l["bytes"] == "imagem")
            print(f"check_retorno: {len(linhas)} formularios, "
                  f"{destrutivos} com Default que grava na imagem")
        return rc

    SAIDA_MD.write_text(md, encoding="utf-8")
    SAIDA_TSV.write_text(tsv, encoding="utf-8")
    for caminho in (SAIDA_MD, SAIDA_TSV):
        rel = caminho.relative_to(RAIZ)
        print(f"  {rel}: "
              f"{len(caminho.read_text(encoding='utf-8').splitlines())} linhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
