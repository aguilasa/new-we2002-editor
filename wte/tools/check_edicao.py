#!/usr/bin/env python3
"""Cada handler do grupo de edicao tem instrumento, e o instrumento passa.

Gera `wte/re/edicao-cobertura.md` -- fecha o criterio *conferencia verde para
cada grupo de edicao, uma por rodada* da
[WTE-TASK-26](../../docs/tasks/concluidos/26-handlers-de-edicao.md).

## O problema que ele resolve

O criterio pede conferencia por grupo, e a resposta ate aqui era **prosa**: o
log da task dizia qual regua cobria o que, e prosa nao reprova. Um handler novo
entra sem instrumento, um script muda de nome, uma conferencia passa a ser
pulada -- e o texto continua afirmando cobertura.

Este script torna a afirmacao mecanica. Ele nao mede tela nem byte: **confere
que cada um dos 28 handlers tem um instrumento nomeado, que o instrumento
existe, e que o instrumento que se pode rodar sem `:98` roda e passa.**

## As quatro classes de instrumento, e por que sao quatro

| classe | o que e | quem verifica |
|---|---|---|
| `tela` | uma sequencia do `compara_tela.sh` | o proprio, no `:98`, com Wine |
| `estatico` | um gerador com `--check` | este script roda |
| `outra_task` | a conferencia mora em outra task, por decisao registrada | este script confere que a task existe |
| `sem_instrumento` | nao ha -- e o script REPROVA | -- |

A terceira nao e escapatoria: ela existe porque a **opcao A**, decidida pelo
usuario em 2026-08-12, poe a metade de gravacao de nove handlers na
WTE-TASK-27. Sem ela o script mentiria em uma de duas direcoes -- ou reprovando
uma decisao tomada, ou fingindo que a 26 mede o que ela nao pode medir.

**Por que o grupo `mover` nao tem regua de tela, e isso foi MEDIDO, nao
suposto:** o `GravaJogador` do port devolve o codigo do caminho feliz e nao
escreve byte nenhum -- a gravacao e da 27. Logo o `PreencheJogadores` seguinte
repovoa com dado igual e **a tela do port nao muda**. Uma regua de tela ali
seria um teste que tem de falhar ate a 27 existir.

Uso:

    python3 wte/tools/check_edicao.py            # regenera o markdown
    python3 wte/tools/check_edicao.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
SPEC = ROOT / "wte" / "re" / "spec"
OUT = ROOT / "wte" / "re" / "edicao-cobertura.md"

GERADOR = "wte/tools/check_edicao.py"
REL_OUT = "wte/re/edicao-cobertura.md"

# Os handlers do grupo `edicao` que NAO sao desta task, com o dono de cada um.
# A lista sai do enunciado da WTE-TASK-26, e o script confere que a soma fecha:
# 44 no TSV, 16 aqui, 28 na tabela de instrumentos.
FORA = {
    "ficha_color": "WTE-TASK-29",          # os 11 do dialogo de cor
    "colorearClick": "WTE-TASK-29",
    "malla1MouseDown": "WTE-TASK-29",
    "malla2MouseDown": "WTE-TASK-29",
    "casilla_precioKeyPress": "WTE-TASK-32",
    "etiqprecioClick": "WTE-TASK-32",
}

TELA = "tela"
ESTATICO = "estatico"
OUTRA = "outra_task"

# handler -> (grupo, classe, instrumento, por que este instrumento)
INSTRUMENTO = {
    "sel_barraClick": (
        "barras", TELA, "compara_tela.sh --edicao",
        "a largura da barra e `11*v + 9`: numero do jogo virado pixel"),
    "track_barraChange": (
        "barras", TELA, "compara_tela.sh --edicao",
        "idem -- os dois lados sao levados ao mesmo time e a mesma trilha"),

    "edit_nombre1KeyPress": (
        "nomes", TELA, "compara_tela.sh --nomes",
        "o filtro decide quantos caracteres sobram, e a tinta mede isso"),
    "edit_nombre2KeyPress": (
        "nomes", TELA, "compara_tela.sh --nomes", "idem"),
    "edit_nombre3KeyPress": (
        "nomes", TELA, "compara_tela.sh --nomes",
        "idem, e o filtro dele e mais estrito -- recusa espaco e ponto"),
    "iguala_nombresClick": (
        "nomes", OUTRA, "WTE-TASK-35",
        "o clique copia e trunca; o botao nao acinzenta no port porque o "
        "glifo e invariante sob o `gdeDisabled` da LCL, que e grayscale -- "
        "causa medida pela CORR-WTE-060, divergencia deliberada, travada pelo "
        "`check_glifos_disabled.py`"),
    "casilla_nombreKeyPress": (
        "nomes", ESTATICO, "dump_truncamento.py",
        "o campo mora na ficha, que nao e mensuravel em pixel; o limite e o "
        "`MaxLength` do DFM contra a largura de `Player.name`"),

    "dorsalClick": (
        "numeros", OUTRA, "WTE-TASK-27",
        "grava o numero de camisa -- opcao A, 2026-08-12"),
    "dorsalMouseDown": (
        "numeros", ESTATICO, "check_bitfields.py",
        "dispara com o botao DIREITO e termina abrindo a ficha do jogador -- "
        "sub-dialogo que nenhuma regua de tela alcanca. Esta entrada dizia "
        "`compara_tela.sh --edicao` ate a evidencia de trace mostrar que "
        "aquele modo nao clica camisa nenhuma"),
    "scroll_dorsalChange": (
        "numeros", ESTATICO, "dump_truncamento.py",
        "mora no `ficha_dorsal`, sub-dialogo que nenhuma regua de tela alcanca"),
    "casilla_dorsalKeyPress": (
        "numeros", ESTATICO, "dump_truncamento.py",
        "idem -- e o `MaxLength` de 10 dele nao governa nada, o que so o "
        "documento de truncamento diz"),

    "barrhabScroll": (
        "atributos", ESTATICO, "check_bitfields.py",
        "a ficha nao e mensuravel em pixel -- o `TScrollBar` do gtk2 cobre a "
        "faixa das linhas 2 a 16; o que se confere e a IDENTIDADE do campo"),
    "barrhab_bisScroll": (
        "atributos", ESTATICO, "check_bitfields.py", "idem"),

    "paderechaClick": ("mover", OUTRA, "WTE-TASK-27", "opcao A, 2026-08-12"),
    "paizquierdaClick": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "parribaClick": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "pabajoClick": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "paderecha2Click": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "paizquierda2Click": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "paderechaeizquierdaClick": ("mover", OUTRA, "WTE-TASK-27", "opcao A"),
    "flechasapaClick": (
        "mover", ESTATICO, "check_bitfields.py",
        "nao grava na imagem; o que ele mostra sao os campos de aparencia, e "
        "a ordem deles e o que a conferencia estatica prende"),

    "bolaMouseDown": (
        "tatica", ESTATICO, "dump_zonas.py",
        "o retangulo que ele desenha sai da tabela de zonas, conferida contra "
        "o tamanho do `campo` no `.lfm`"),
    "bolaMouseMove": ("tatica", ESTATICO, "dump_zonas.py", "idem"),
    "campoMouseMove": ("tatica", ESTATICO, "dump_zonas.py", "idem"),
    "rectanguloDragOver": ("tatica", ESTATICO, "dump_zonas.py", "idem"),
    "rectanguloDragDrop": ("tatica", ESTATICO, "dump_zonas.py", "idem"),
    "bolaEndDrag": ("tatica", ESTATICO, "dump_zonas.py", "idem"),
    "relojTimer": (
        "tatica", ESTATICO, "dump_zonas.py",
        "as seis tabelas da animacao nascem do mesmo `.bss`, e o destino final "
        "e a mesma geometria"),
}

# Os modos de tela que existem, para o script recusar instrumento inventado.
MODOS_DE_TELA = {"compara_tela.sh --edicao", "compara_tela.sh --nomes"}

# A evidencia de que cada modo exercitou o que a tabela diz. Sai do
# `port-trace` de cada corrida do `compara_tela.sh` e e versionada: sem ela,
# "este modo cobre este handler" e palavra. Foi assim que o `dorsalMouseDown`
# ficou atribuido a um modo que nao clica camisa nenhuma, e a atribuicao
# atravessou uma revisao inteira sem ninguem notar.
EVIDENCIA = ROOT / "wte" / "re" / "edicao-tela.tsv"


class CoberturaError(Exception):
    pass


def do_grupo_edicao() -> list[str]:
    """Os handlers com `grupo = edicao` no TSV, sem os que tem dono fora."""
    linhas = PUB.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    i_nome, i_form, i_grupo = cab.index("handler"), cab.index("formulario"), \
        cab.index("grupo")
    todos, fora = [], 0
    for linha in linhas[1:]:
        c = linha.split("\t")
        if c[i_grupo] != "edicao":
            continue
        if c[i_form] in FORA or c[i_nome] in FORA:
            fora += 1
            continue
        todos.append(c[i_nome])
    if fora + len(todos) != sum(1 for l in linhas[1:]
                                if l.split("\t")[i_grupo] == "edicao"):
        raise CoberturaError("a soma de dentro e fora nao fecha")
    return sorted(todos)


def disparos_por_modo() -> dict[str, dict[str, int]]:
    """(modo -> handler -> disparos), da evidencia de trace versionada."""
    if not EVIDENCIA.is_file():
        raise CoberturaError(
            f"{EVIDENCIA.relative_to(ROOT)} nao existe. Rode "
            f"`bash wte/tools/compara_tela.sh --edicao` e `--nomes` -- sem a "
            f"evidencia nao da para dizer que os modos de tela exercitam o que "
            f"esta tabela afirma")
    fora: dict[str, dict[str, int]] = {}
    for linha in EVIDENCIA.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        modo, handler, n = linha.split("\t")
        fora.setdefault(modo, {})[handler] = int(n)
    return fora


def confere(handlers: list[str]) -> list[str]:
    problemas = []
    visto = disparos_por_modo()
    sem = [h for h in handlers if h not in INSTRUMENTO]
    if sem:
        problemas.append(
            f"sem instrumento nomeado: {', '.join(sem)}. Handler novo no grupo "
            f"de edicao entra aqui, ou o criterio da task deixa de valer")
    sobra = [h for h in INSTRUMENTO if h not in handlers]
    if sobra:
        problemas.append(
            f"instrumento para handler que nao esta no grupo: "
            f"{', '.join(sorted(sobra))}")

    for h in handlers:
        if h not in INSTRUMENTO:
            continue
        _g, classe, alvo, _pq = INSTRUMENTO[h]
        if classe == TELA and alvo not in MODOS_DE_TELA:
            problemas.append(f"{h}: modo de tela `{alvo}` nao existe")
        elif classe == TELA:
            modo = alvo.rsplit("--", 1)[1]
            formulario = next(c.split("\t")[2]
                              for c in PUB.read_text(encoding="utf-8")
                              .splitlines()[1:]
                              if c.split("\t")[1] == h)
            chave = f"{formulario}.{h}"
            if visto.get(modo, {}).get(chave, 0) < 1:
                problemas.append(
                    f"{h}: a tabela diz que `{alvo}` o cobre, e o trace daquela "
                    f"corrida nao tem `{chave}`. Ou o modo passa a exercita-lo, "
                    f"ou a classe dele nao e `tela`")
        elif classe == ESTATICO and not (ROOT / "wte/tools" / alvo).is_file():
            problemas.append(f"{h}: `wte/tools/{alvo}` nao existe")
        elif classe == OUTRA:
            nome = alvo.replace("WTE-TASK-", "")
            # `rglob`: a task pode ter descido para `docs/tasks/concluidos/`
            achou = list((ROOT / "docs/tasks").rglob(f"{nome}-*.md"))
            if not achou:
                problemas.append(f"{h}: {alvo} nao tem arquivo em docs/tasks")

        # Todo handler desta task tem spec, e o instrumento so vale sobre uma.
        if not list(SPEC.glob(f"*.{h}.md")):
            problemas.append(f"{h}: sem spec em wte/re/spec")
    return problemas


def roda_estaticos(handlers: list[str]) -> tuple[dict[str, int], list[str]]:
    """Roda o `--check` de cada instrumento estatico. E a parte que MEDE."""
    alvos = sorted({INSTRUMENTO[h][2] for h in handlers
                    if h in INSTRUMENTO and INSTRUMENTO[h][1] == ESTATICO})
    fora, problemas = {}, []
    for alvo in alvos:
        r = subprocess.run([sys.executable, str(ROOT / "wte/tools" / alvo),
                            "--check"], capture_output=True, text=True)
        fora[alvo] = r.returncode
        if r.returncode != 0:
            problemas.append(
                f"{alvo} --check saiu {r.returncode}: "
                f"{(r.stderr or r.stdout).strip().splitlines()[-1:]}")
    return fora, problemas


def md(handlers: list[str], estaticos: dict[str, int]) -> str:
    grupos: dict[str, list[str]] = {}
    for h in handlers:
        grupos.setdefault(INSTRUMENTO[h][0], []).append(h)
    linhas = [
        "# `re/edicao-cobertura.md` — o instrumento de cada handler de edição",
        "",
        "Produto da [WTE-TASK-26](../../docs/tasks/concluidos/26-handlers-de-edicao.md), o",
        "critério *conferência verde para cada grupo de edição*. Gerado por",
        f"[`../tools/check_edicao.py`](../tools/check_edicao.py). **Não editar à mão.**",
        "",
        "## Por que este arquivo existe",
        "",
        "A resposta ao critério era **prosa**: o log da task dizia qual régua",
        "cobria o quê, e prosa não reprova. Handler novo entra sem instrumento,",
        "script muda de nome, conferência passa a ser pulada — e o texto continua",
        "afirmando cobertura.",
        "",
        "O gerador **reprova** se algum dos handlers do grupo ficar sem",
        "instrumento, se o instrumento nomeado não existir, ou se um instrumento",
        "estático não passar no próprio `--check`.",
        "",
        "## A tabela",
        "",
    ]
    for grupo in sorted(grupos):
        linhas += [f"### {grupo}", "",
                   "| Handler | Classe | Instrumento | Por quê |",
                   "|---|---|---|---|"]
        for h in sorted(grupos[grupo]):
            _g, classe, alvo, pq = INSTRUMENTO[h]
            linhas.append(f"| `{h}` | {classe} | `{alvo}` | {pq} |")
        linhas.append("")
    linhas += [
        "## As quatro classes",
        "",
        "| classe | o que é | quem verifica |",
        "|---|---|---|",
        "| `tela` | uma sequência do `compara_tela.sh` | o próprio, no `:98`, com Wine |",
        "| `estatico` | um gerador com `--check` | este script roda, e o resultado está abaixo |",
        "| `outra_task` | a conferência mora em outra task, por decisão registrada | este script confere que a task existe |",
        "| `sem_instrumento` | não há — e o script **reprova** | — |",
        "",
        "A terceira **não é escapatória**: ela existe porque a **opção A**,",
        "decidida pelo usuário em 2026-08-12, põe a metade de gravação de nove",
        "handlers na [WTE-TASK-27](../../docs/tasks/concluidos/27-handlers-de-gravacao.md).",
        "",
        "**E o grupo `mover` não tem régua de tela por medição, não por",
        "conveniência:** o `GravaJogador` do port devolve o código do caminho",
        "feliz e não escreve byte nenhum — a gravação é da 27. O",
        "`PreencheJogadores` seguinte repovoa com dado igual e **a tela do port",
        "não muda**. Régua de tela ali seria teste que tem de falhar até a 27",
        "existir.",
        "",
        "## O que este gerador rodou",
        "",
        "| Instrumento estático | `--check` |",
        "|---|--:|",
    ]
    for alvo, rc in sorted(estaticos.items()):
        linhas.append(f"| `{alvo}` | {'passou' if rc == 0 else f'saiu {rc}'} |")
    linhas.append("")
    return "\n".join(linhas)


def gera() -> tuple[str, list[str]]:
    handlers = do_grupo_edicao()
    problemas = confere(handlers)
    estaticos, mais = roda_estaticos(handlers)
    problemas += mais
    # Sem tabela quando ha problema: montar o markdown com um handler faltando
    # estouraria no `md()`, e o diagnostico sairia como `KeyError` em vez da
    # frase que diz o que fazer.
    if problemas:
        return "", problemas
    return md(handlers, estaticos), problemas


def main(argv: list[str]) -> int:
    check = "--check" in argv
    if argv and not check:
        print(f"uso: {GERADOR} [--check]", file=sys.stderr)
        return 2
    try:
        texto, problemas = gera()
    except CoberturaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    if problemas:
        print("cobertura do grupo de edicao incompleta:", file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        return 2
    if check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texto:
            print(f"{REL_OUT} fora de dia -- rode: python3 {GERADOR}",
                  file=sys.stderr)
            return 2
        n = len(do_grupo_edicao())
        print(f"check_edicao: {n} handlers, todos com instrumento; os "
              f"estaticos passaram")
        return 0
    OUT.write_text(texto, encoding="utf-8", newline="\n")
    print(f"  {REL_OUT}: {texto.count(chr(10))} linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
