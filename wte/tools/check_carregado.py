#!/usr/bin/env python3
"""Os formularios com a logica ligada: alcance, tamanho e cor de fundo real.

Gera `wte/re/carregado.md` e `wte/re/carregado.tsv` — produto da
[WTE-TASK-37](../../docs/tasks/concluidos/37-reconferencia-de-ui.md), a reconferencia de
UI que a WTE-TASK-12 nao podia fazer: ela olhou os 18 VAZIOS, com o andaime
`--show` que a WTE-TASK-25 removeu depois.

## As tres medidas, e por que estas

1. **Alcance no port.** Para cada um dos 18, quem chama `Show`/`ShowModal`
   dentro de `wte/src/`. Formulario sem chamador nenhum e formulario que o
   usuario nao ve -- e a UI mais divergente possivel, invisivel a qualquer
   regua de pixel, porque a tela que ninguem abre nunca aparece numa captura.
2. **Tamanho das duas capturas.** O oraculo desenha a moldura POR DENTRO da
   janela quando o DFM declara `ClientWidth`; o port nao. A regra sai da
   propria medida (`+6` de largura e `+32` de altura, ou nada), e o script
   RECUSA fechar se uma captura nao casar com nenhuma das duas formas: sem
   isso, comparar controle por coordenada mediria o lugar errado.
3. **Cor de fundo real, por formulario e por `TStaticText`.** O achado 3 da
   WTE-TASK-12 mediu que 13 dos 18 recebem `Color` em tempo de execucao, e o
   achado 4 decidiu nao mexer nos 37 `TStaticText` -- **com o fundo de projeto
   atras deles**. Aqui a decisao e reconferida com o fundo de execucao: a cor
   dominante do retangulo de cada `TStaticText`, nos dois lados, contra a cor
   dominante do formulario.

## O que ele NAO faz

Comparar pixel a pixel entre os dois lados. A §6 do plano manda **sem
tolerancia de pixel** e a razao e boa: `MS Sans Serif` nao esta instalada, gtk2
e Wine substituem por fontes diferentes, e todo texto difere. Cor dominante de
retangulo atravessa isso porque nao depende de glifo.

## Como refazer

    bash wte/tools/captura_ui.sh ui-01-telas ui-02-transferencia ui-03-avisos
    python3 wte/tools/check_carregado.py
    python3 wte/tools/check_carregado.py --check   # `make -C wte check`

O `--check` **nao** dirige janela nenhuma: ele remede os PNG commitados. Sai 2
quando o commitado diverge do medido.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from check_retorno import le_arvore, lfm_do_formulario

RAIZ = Path(__file__).resolve().parents[2]
DFM = RAIZ / "wte" / "re" / "dfm"
SRC = RAIZ / "wte" / "src"
FOTOS = RAIZ / "wte" / "re" / "visual" / "carregado"
SAIDA_MD = RAIZ / "wte" / "re" / "carregado.md"
SAIDA_TSV = RAIZ / "wte" / "re" / "carregado.tsv"

# A moldura que o Wine desenha POR DENTRO da janela. Medida nas capturas desta
# task, nao suposta: `ficha_error2` (cliente 376x90) sai 382x122, `ficha_salida`
# (225x90) sai 231x122, `ficha_dorsal` (129x121) sai 135x153.
MOLDURA = (6, 32)
DESLOCAMENTO = (3, 29)

RE_SHOW = re.compile(r"\b(\w+)\.(ShowModal|Show)\b")


class CarregadoError(Exception):
    pass


def cliente(objetos: list[dict], caminho: Path) -> tuple[int, int]:
    """(largura, altura) da area de cliente declarada no DFM.

    Cinco dos 18 declaram `Width`/`Height` em vez de `ClientWidth`/
    `ClientHeight` -- para esses, o cliente e o declarado menos a moldura.
    """
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    def prop(nome: str) -> int | None:
        m = re.search(rf"^  {nome} = (\d+)$", texto, re.M)
        return int(m.group(1)) if m else None
    cw, ch = prop("ClientWidth"), prop("ClientHeight")
    if cw is not None and ch is not None:
        return cw, ch
    w, h = prop("Width"), prop("Height")
    if w is None or h is None:
        raise CarregadoError(f"{caminho.name}: sem ClientWidth nem Width")
    return w - MOLDURA[0], h - MOLDURA[1]


def deslocamento(tamanho: tuple[int, int],
                 cli: tuple[int, int], onde: str) -> tuple[int, int]:
    if tamanho == cli:
        return (0, 0)
    if tamanho == (cli[0] + MOLDURA[0], cli[1] + MOLDURA[1]):
        return DESLOCAMENTO
    raise CarregadoError(
        f"{onde}: a captura mede {tamanho[0]}x{tamanho[1]} e o cliente do DFM "
        f"mede {cli[0]}x{cli[1]} -- nao e nem um nem o outro mais a moldura "
        f"{MOLDURA[0]}x{MOLDURA[1]}. Coordenada de controle sobre essa captura "
        "mediria o lugar errado.")


def dominante(img, caixa=None) -> str:
    """A cor mais frequente do recorte, em `#RRGGBB`.

    `getcolors` com o teto no numero de pixels devolve a lista inteira em vez
    de `None`, e o desempate e pelo valor da cor -- sem isso, dois recortes com
    a mesma contagem poderiam sair diferentes entre execucoes, e o `--check`
    ficaria intermitente.
    """
    recorte = img.crop(caixa) if caixa else img
    largura, altura = recorte.size
    cores = recorte.getcolors(largura * altura)
    quantas, cor = max(cores, key=lambda c: (c[0], c[1]))
    return "#%02X%02X%02X" % cor[:3]


def retangulos_de_classe(caminho: Path, classe: str):
    """`retangulos` sem o argumento de arvore, que ela nao usa."""
    return retangulos(None, caminho, classe)


def retangulos(objetos, caminho: Path,
               classe: str) -> list[tuple[str, tuple[int, int, int, int]]]:
    """Os retangulos absolutos dos objetos dessa classe, somados pelos pais."""
    pilha: list[list] = []
    fora: list[tuple[str, tuple[int, int, int, int]]] = []
    dentro_de_blob = False
    for linha in caminho.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
        ind = len(linha) - len(linha.lstrip())
        corte = linha.strip()
        if dentro_de_blob:
            if corte == "}":
                dentro_de_blob = False
            continue
        if corte.endswith("= {"):
            dentro_de_blob = True
            continue
        # O nome e OPCIONAL: os 18 formularios tem um `TStaticText` anonimo
        # (no `MainForm`), e a WTE-TASK-12 contou 37 instancias justamente
        # porque o incluiu. Regex que exige nome contaria 36.
        m = re.match(r"^object (?:(\w+): )?(\w+)$", corte)
        if m:
            while pilha and pilha[-1][0] >= ind:
                pilha.pop()
            pilha.append([ind, m.group(1) or "", m.group(2), 0, 0, 0, 0])
            continue
        if corte == "end":
            while pilha and pilha[-1][0] >= ind:
                pilha.pop()
            continue
        if not pilha:
            continue
        m2 = re.match(r"^(Left|Top|Width|Height) = (-?\d+)$", corte)
        if m2:
            pilha[-1][{"Left": 3, "Top": 4,
                       "Width": 5, "Height": 6}[m2.group(1)]] = int(m2.group(2))
            if m2.group(1) == "Height" and pilha[-1][2] == classe:
                x = sum(e[3] for e in pilha[1:])
                y = sum(e[4] for e in pilha[1:])
                fora.append((pilha[-1][1],
                             (x, y, pilha[-1][5], pilha[-1][6])))
    return fora


def retangulos_com_cor(dfm: Path, lfm: Path):
    """Rotulos que declaram `Color` no DFM, com o retangulo lido do LFM.

    O `Color` sai do DFM e a geometria do LFM de proposito: e a mesma dupla que
    o `dfm2lfm.py --check` mantem igual, e ler cada coisa da sua fonte deixa a
    conferencia dependente das duas.
    """
    declara: set[str] = set()
    atual = None
    for l in dfm.read_text(encoding="utf-8", errors="replace").splitlines():
        s = l.strip()
        m = re.match(r"^object (?:(\w+): )?(\w+)$", s)
        if m:
            atual = (m.group(1) or "", m.group(2))
            continue
        if atual and s.startswith("Color = ") and atual[1] in ("TLabel",
                                                               "TStaticText"):
            declara.add(atual[0])
    fora = []
    for classe in ("TLabel", "TStaticText"):
        for nome, rect in retangulos_de_classe(lfm, classe):
            if nome in declara:
                fora.append((nome, rect))
    return fora


def chamadores() -> dict[str, list[str]]:
    """formulario -> arquivos de `wte/src` que o abrem."""
    fora: dict[str, set[str]] = {}
    for caminho in sorted(SRC.rglob("*"), key=lambda p: p.as_posix()):
        if caminho.is_dir() or caminho.suffix not in (".pas", ".inc", ".lpr"):
            continue
        for linha in caminho.read_text(encoding="utf-8",
                                       errors="replace").splitlines():
            corte = linha.strip()
            if corte.startswith("{") or corte.startswith("//"):
                continue
            for m in RE_SHOW.finditer(corte):
                fora.setdefault(m.group(1), set()).add(caminho.name)
    return {k: sorted(v) for k, v in fora.items()}


COLUNAS = ("formulario", "alcance_port", "foto_oraculo", "foto_port",
           "fundo_oraculo", "fundo_port", "statictext",
           "statictext_no_fundo_oraculo", "statictext_no_fundo_port",
           "rotulos_com_cor", "rotulos_divergentes", "quais_divergem")


def mede() -> list[dict]:
    from PIL import Image
    quem = chamadores()
    linhas = []
    # `key=` E OBRIGATORIO, e a razao e de plataforma. `sorted()` sobre
    # `Path` compara pelo `_str_normcase`, que no Windows e MINUSCULO: la
    # `MainForm.dfm` cai depois de `estrategia.dfm`, e no Linux vem antes
    # (`M` = 0x4D < `e` = 0x65). O `carregado.tsv` sairia noutra ordem e o
    # `--check` acusaria divergencia que nao existe. Ordenar pelo `name` cru
    # e case-sensitive nos dois. Medido em 2026-08-26 no Windows.
    for caminho in sorted(DFM.glob("*.dfm"), key=lambda p: p.name):
        objetos = le_arvore(caminho)
        formulario = objetos[0]["nome"]
        cli = cliente(objetos, caminho)
        lfm = lfm_do_formulario(formulario)
        estaticos = retangulos(objetos, lfm, "TStaticText")

        # O `MainForm` nao e aberto por ninguem: ele E a janela principal, e
        # `Application.CreateForm` a mostra. Conta-lo entre os "sem chamador"
        # faria o resumo dizer tres onde o achado sao dois.
        alcance = ",".join(quem.get(formulario, []))
        if not alcance and formulario == "MainForm":
            alcance = "(principal)"
        linha = {
            "formulario": formulario,
            "alcance_port": alcance or "—",
            "statictext": str(len(estaticos)),
        }
        for lado in ("oraculo", "port"):
            png = FOTOS / lado / f"{formulario}.png"
            if not png.exists():
                linha[f"foto_{lado}"] = "—"
                linha[f"fundo_{lado}"] = "—"
                linha[f"statictext_no_fundo_{lado}"] = "—"
                continue
            img = Image.open(png).convert("RGB")
            desl = deslocamento(img.size, cli, f"{lado}/{formulario}.png")
            linha[f"foto_{lado}"] = f"{img.size[0]}x{img.size[1]}"
            fundo = dominante(img)
            linha[f"fundo_{lado}"] = fundo
            iguais = 0
            for _, (x, y, w, h) in estaticos:
                if w <= 0 or h <= 0:
                    continue
                caixa = (x + desl[0], y + desl[1],
                         x + desl[0] + w, y + desl[1] + h)
                if caixa[2] > img.size[0] or caixa[3] > img.size[1]:
                    continue
                if dominante(img, caixa) == fundo:
                    iguais += 1
            linha[f"statictext_no_fundo_{lado}"] = str(iguais)

        # Os rotulos que declaram `Color` no DFM, comparados ENTRE OS LADOS.
        #
        # E a §8.9 do plano generalizada, e a generalizacao nao e enfeite: ela
        # manda conferir os 37 `TStaticText` porque o GTK2 trata cor de fundo
        # diferente do Win32 -- e 151 `TLabel` declaram `Color` pelo mesmo
        # DFM, quatro vezes mais. Nenhum dos dois declara `Transparent`, entao
        # quem decide se a cor aparece e o DEFAULT do widgetset.
        #
        # Comparar retangulo com retangulo entre os dois lados atravessa a
        # troca de fonte: cor dominante de area chapada nao depende de glifo.
        com_cor = [(n, r) for n, r in
                   retangulos_com_cor(caminho, lfm)]
        linha["rotulos_com_cor"] = str(len(com_cor))
        if linha["foto_oraculo"] == "—" or linha["foto_port"] == "—":
            linha["rotulos_divergentes"] = "—"
            linha["quais_divergem"] = "—"
        else:
            o = Image.open(FOTOS / "oraculo" / f"{formulario}.png").convert("RGB")
            pt = Image.open(FOTOS / "port" / f"{formulario}.png").convert("RGB")
            do = deslocamento(o.size, cli, "oraculo")
            dp = deslocamento(pt.size, cli, "port")
            quais = []
            for nome, (x, y, w, h) in com_cor:
                if w <= 0 or h <= 0:
                    continue
                co = (x + do[0], y + do[1], x + do[0] + w, y + do[1] + h)
                cp = (x + dp[0], y + dp[1], x + dp[0] + w, y + dp[1] + h)
                if co[2] > o.size[0] or co[3] > o.size[1]:
                    continue
                if cp[2] > pt.size[0] or cp[3] > pt.size[1]:
                    continue
                if dominante(o, co) != dominante(pt, cp):
                    quais.append(nome or "(sem nome)")
            linha["rotulos_divergentes"] = str(len(quais))
            linha["quais_divergem"] = ",".join(quais) or "—"
        linhas.append(linha)
    return linhas


def render(linhas: list[dict]) -> tuple[str, str]:
    tsv = ["\t".join(COLUNAS)]
    for l in linhas:
        tsv.append("\t".join(l[c] for c in COLUNAS))

    sem_alcance = [l for l in linhas if l["alcance_port"] == "—"]
    com_foto_dos_dois = [l for l in linhas
                         if l["foto_oraculo"] != "—" and l["foto_port"] != "—"]
    so_oraculo = [l for l in linhas
                  if l["foto_oraculo"] != "—" and l["foto_port"] == "—"]
    sem_foto = [l for l in linhas
                if l["foto_oraculo"] == "—" and l["foto_port"] == "—"]
    fundo_igual = [l for l in com_foto_dos_dois
                   if l["fundo_oraculo"] == l["fundo_port"]]
    rotulos = sum(int(l["rotulos_com_cor"]) for l in linhas)
    divergentes = sum(int(l["rotulos_divergentes"]) for l in linhas
                      if l["rotulos_divergentes"] != "—")

    md = [
        "# `re/carregado.md` — os formulários com a lógica ligada",
        "",
        "Gerado por [`../tools/check_carregado.py`](../tools/check_carregado.py)"
        " a partir dos 18 `.dfm`, dos 18 `.lfm`, de `wte/src/` e das capturas "
        "de [`visual/carregado/`](visual/carregado). **Não editar à mão:**",
        "",
        "```sh",
        "bash wte/tools/captura_ui.sh ui-01-telas ui-02-transferencia "
        "ui-03-avisos",
        "python3 wte/tools/check_carregado.py",
        "python3 wte/tools/check_carregado.py --check",
        "```",
        "",
        "A tabela está em [`carregado.tsv`](carregado.tsv); este arquivo é a "
        "leitura dela. **Todo número daqui saiu do script.**",
        "",
        "## Resumo",
        "",
        "| Medida | Valor |",
        "|---|---:|",
        f"| Formulários | {len(linhas)} |",
        f"| Sem nenhum `Show`/`ShowModal` em `wte/src/` | {len(sem_alcance)} |",
        f"| Fotografados dos **dois** lados | {len(com_foto_dos_dois)} |",
        f"| Fotografados só do oráculo | {len(so_oraculo)} |",
        f"| Sem foto nenhuma | {len(sem_foto)} |",
        f"| Com a mesma cor de fundo dos dois lados | {len(fundo_igual)} de "
        f"{len(com_foto_dos_dois)} |",
        f"| Rótulos que declaram `Color` | {rotulos} |",
        f"| Deles, com cor diferente entre os dois lados | {divergentes} |",
        "",
        "## Por formulário",
        "",
        "| Formulário | quem abre no port | foto oráculo | foto port | "
        "fundo oráculo | fundo port | `TStaticText` | no fundo (orác./port) | "
        "rótulos com `Color` | divergentes |",
        "|---|---|---|---|---|---|---:|---|---:|---:|",
    ]
    for l in linhas:
        md.append(
            f"| `{l['formulario']}` | {l['alcance_port']} | "
            f"{l['foto_oraculo']} | {l['foto_port']} | {l['fundo_oraculo']} | "
            f"{l['fundo_port']} | {l['statictext']} | "
            f"{l['statictext_no_fundo_oraculo']}/"
            f"{l['statictext_no_fundo_port']} | {l['rotulos_com_cor']} | "
            f"{l['rotulos_divergentes']} |")
    md += [
        "",
        "## Como ler a coluna `no fundo`",
        "",
        "Quantos `TStaticText` do formulário têm, no retângulo deles, a **mesma "
        "cor dominante** do formulário inteiro. É a releitura do achado 4 da "
        "[WTE-TASK-12](../../docs/tasks/concluidos/12-comparacao-visual.md) com o fundo "
        "de execução por baixo: os que declaram `Color` próprio ficam **fora** "
        "dessa conta nos dois lados — é o que se espera, e é o que faz a "
        "medida valer alguma coisa —, e os que herdam a cor do pai entram nela "
        "nos dois. Contagem diferente entre os lados é o sintoma que a §8.9 do "
        "plano mandava procurar.",
        "",
        "## E a coluna `divergentes`",
        "",
        "Quantos rótulos que declaram `Color` no DFM têm **cor de fundo "
        "diferente entre os dois lados**. É a §8.9 generalizada: ela manda "
        "conferir os 37 `TStaticText`, e são **151 `TLabel`** que declaram "
        "`Color` pelo mesmo DFM. Nenhum dos dois grupos declara `Transparent`, "
        "então quem decide se a cor aparece é o *default* do widgetset — e os "
        "dois defaults não são o mesmo.",
        "",
    ]
    return "\n".join(md) + "\n", "\n".join(tsv) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    try:
        linhas = mede()
    except CarregadoError as e:
        print(f"check_carregado: {e}", file=sys.stderr)
        return 2
    except ModuleNotFoundError as e:
        print(f"check_carregado: sem {e.name} -- nada medido", file=sys.stderr)
        return 2

    md, tsv = render(linhas)
    if args.check:
        rc = 0
        for caminho, texto in ((SAIDA_MD, md), (SAIDA_TSV, tsv)):
            atual = (caminho.read_text(encoding="utf-8")
                     if caminho.exists() else None)
            rel = caminho.relative_to(RAIZ)
            if atual != texto:
                print(f"check_carregado: {rel}: DIVERGE -- rode sem --check",
                      file=sys.stderr)
                rc = 2
            else:
                print(f"check_carregado: {rel}: ok")
        if rc == 0:
            dois = sum(1 for l in linhas
                       if l["foto_oraculo"] != "—" and l["foto_port"] != "—")
            print(f"check_carregado: {len(linhas)} formularios, {dois} "
                  "fotografados dos dois lados")
        return rc

    SAIDA_MD.write_text(md, encoding="utf-8")
    SAIDA_TSV.write_text(tsv, encoding="utf-8")
    for caminho in (SAIDA_MD, SAIDA_TSV):
        print(f"  {caminho.relative_to(RAIZ)}: "
              f"{len(caminho.read_text(encoding='utf-8').splitlines())} linhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
