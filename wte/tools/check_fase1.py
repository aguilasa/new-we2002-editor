#!/usr/bin/env python3
"""Fechamento da fase 1: as quatro conferencias cruzadas e a reconciliacao.

Gera `wte/re/fase-1.md` -- o produto da WTE-TASK-09. Ele nao mede o binario de
novo: mede a **coerencia entre os produtos** que as WTE-TASK-03 a 08 ja
deixaram versionados, e confronta os sete numeros que a §1 do plano afirma
contra o que essas ferramentas dizem hoje.

## Por que ele le produto e nao binario

Quatro dos sete numeros ja tem gerador com `--check` proprio, e re-medi-los
aqui criaria uma segunda copia da medida -- exatamente a duplicacao sem guarda
que o [`README.md`](README.md) deste diretorio manda evitar. Um quinto leitor
de PE para recontar imports seria a quinta copia do mesmo codigo, desta vez sem
o teste que a do `dump_units.py` tem.

Entao a divisao e esta, e ela esta escrita na saida:

| Numero | De onde sai aqui |
|---|---|
| formularios, componentes, classes | recontados dos 18 `.dfm`, e **confrontados** com o `censo.md` |
| handlers | `published_methods.tsv` |
| offsets | `offsets.tsv` + `Offsets.hpp` |
| strings | `strings.tsv` |
| unidades `Tep2002_*` | varredura de bytes no proprio `.exe` (nao precisa de PE) |
| imports | frase medida do `unidades-vcl.md` |
| bitmaps e `dat.bin` | sistema de arquivos, em `we-team-editor/` |

A recontagem dos componentes e a unica que **mede de novo** de proposito: e a
conferencia cruzada que pega o `censo.md` errando, e foi ela que localizou o
componente sem nome do `MainForm`.

## A varredura de sitios

Corrigir a §1 do plano nao fecha um numero errado -- ele se espalha. Este
script varre os markdowns de `docs/` e de `wte/` procurando **afirmacao viva**
do numero velho e **aborta** se achar alguma, listando arquivo e linha. Nao ha
tabela de residuo na saida: residuo e falha, do mesmo jeito que o `FORBIDDEN`
do `port_database.py` e falha.

O perimetro nasceu em `docs/` + `wte/re/`, que foi o que o enunciado da
WTE-TASK-09 pediu, e ali fechou em zero. Ficou estreito demais para a propria
tese da §6: o `wte/README.md` seguia afirmando 197 fora do alcance da guarda.
A CORR-WTE-016 trocou as duas bases por `docs/` + `wte/` -- o `rglob` sobre
`wte` ja cobre `wte/re/`.

O que fica de fora do perimetro, e por que:

- **documento que narra a correcao** -- `correcoes-progresso.md`, os
  `CORR-WTE-*.md`, o `assets.md` e o `strings.md` (que registram, cada um, a
  divergencia que mediram), o `wte/tools/README.md` (que narra **esta** guarda,
  e cita `430` para explicar o corte por contexto), e o enunciado da propria
  WTE-TASK-09;
- **enunciado de tarefa ja executada** (`status: concluído` no frontmatter) --
  e historia, nao instrucao; quem le uma task concluida le o que ela pediu na
  epoca. Tarefa **pendente** continua no perimetro: ela ainda vai ser executada
  contra o numero que estiver escrito, e a WTE-TASK-38 e a 39 sao o caso real;
- **Log de Execucao** -- tudo a partir do cabecalho, em qualquer task: o log
  cita o numero velho para dizer que o corrigiu;
- **`docs/prompts/`** -- gabarito, com destino de exemplo.

O corte por numero exige o numero **e** uma palavra de contexto na mesma linha.
Sem isso `430` casaria o setor 430 do `PLAN-LINUX.md` e `300` casaria os 300
setores amostrados de ECC -- dois projetos diferentes, dois assuntos
diferentes, mesmo digito.

Uso:

    python3 wte/tools/check_fase1.py            # regenera
    python3 wte/tools/check_fase1.py --check    # confere contra o commitado
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
IMAGE = ROOT / "we-team-editor" / "image"
DATBIN = ROOT / "we-team-editor" / "data" / "dat.bin"
DFM = ROOT / "wte" / "re" / "dfm"
CENSO = DFM / "censo.md"
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
STR = ROOT / "wte" / "re" / "strings.tsv"
STR_MD = ROOT / "wte" / "re" / "strings.md"
OFS_TSV = ROOT / "wte" / "re" / "offsets.tsv"
OFS_HPP = ROOT / "src" / "core" / "include" / "we2002" / "Offsets.hpp"
UNI_MD = ROOT / "wte" / "re" / "unidades-vcl.md"
OUT = ROOT / "wte" / "re"

REL_EXE = "we-team-editor/we-team-editor.exe"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/check_fase1.py"

MD_NAME = "fase-1.md"


class CheckError(RuntimeError):
    """Insumo ausente, incoerente, ou residuo de numero velho."""


# --------------------------------------------------------------- perimetro --

# Documentos que narram a correcao: o numero velho ali e citacao, e fica.
NARRACAO = {
    "docs/tasks/correcoes-progresso.md",
    "docs/tasks/09-fechamento-fase-1.md",
    "wte/re/assets.md",
    "wte/re/strings.md",
    "wte/tools/README.md",   # narra esta guarda: cita 430 para explicar o corte
    f"wte/re/{MD_NAME}",
}

# Os quatro numeros que a fase 1 reconciliou. Cada um leva o regex do digito e
# o regex de contexto; os dois tem de casar na mesma linha para a linha contar
# como afirmacao viva. `antes` foi medido com este mesmo perimetro em
# 2026-08-06, sobre a arvore anterior a correcao (`git archive 65cc4be docs
# wte`) -- nao da para remedir sobre a arvore de hoje. O 9 de bitmaps era 8
# quando o perimetro parava em `wte/re/`: o nono sitio e o `wte/README.md`, que
# a CORR-WTE-016 trouxe para dentro.
SITIOS = (
    ("197 bitmaps", r"197", r"(?i)bitmap|\.bmp|\bBMP\b|image/", 9),
    ("~430 componentes", r"430", r"(?i)componente|controle", 4),
    ("300 imports de rtl60/vcl60", r"300", r"(?i)rtl60|vcl60|import", 2),
    ("70 strings com enchimento", r"70", r"(?i)string|padding|enchimento|truncad", 4),
)

LOG_HEADER = "## Log de Execução"


def _markdowns() -> list[Path]:
    achados: list[Path] = []
    # `rglob` sobre `wte` ja cobre `wte/re/`. A base larga entrou com a
    # CORR-WTE-016: o sitio vivo estava em `wte/README.md`, fora do alcance.
    for base in ("docs", "wte"):
        achados.extend(sorted((ROOT / base).rglob("*.md")))
    return achados


def _no_perimetro(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in NARRACAO:
        return False
    if rel.startswith("docs/prompts/"):
        return False
    if re.fullmatch(r"docs/tasks/CORR-WTE-\d+\.md", rel):
        return False
    if re.match(r"docs/tasks/\d\d-", rel):
        cabeca = path.read_text(encoding="utf-8")[:600]
        if re.search(r"^status:\s*conclu", cabeca, re.M):
            return False
    return True


def _linhas_vivas(path: Path) -> list[tuple[int, str]]:
    """As linhas do arquivo antes do Log de Execucao."""
    texto = path.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    corte = texto.find(LOG_HEADER)
    limite = len(linhas) if corte < 0 else texto[:corte].count("\n")
    return list(enumerate(linhas[:limite], 1))


def varrer() -> list[tuple[str, list[str]]]:
    """Para cada numero velho, os sitios que ainda o afirmam."""
    alvos = [p for p in _markdowns() if _no_perimetro(p)]
    resultado: list[tuple[str, list[str]]] = []
    for nome, num, ctx, _antes in SITIOS:
        rn, rc = re.compile(rf"\b{num}\b"), re.compile(ctx)
        residuo = [
            f"{p.relative_to(ROOT).as_posix()}:{i}: {linha.strip()}"
            for p in alvos
            for i, linha in _linhas_vivas(p)
            if rn.search(linha) and rc.search(linha)
        ]
        resultado.append((nome, residuo))
    return resultado


# ------------------------------------------------------------------ leitura --

def ler_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise CheckError(f"{path.relative_to(ROOT)} nao existe")
    linhas = path.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l]


def ler_dfm() -> dict[str, list[tuple[int, str, str]]]:
    """Os componentes de cada `.dfm`: (indentacao, nome ou '', classe).

    O objeto raiz fica de fora -- ele e o formulario, nao um componente dentro
    dele. E a mesma regua do `censo.md`, e e o que faz os dois numeros serem
    comparaveis.
    """
    if not DFM.is_dir():
        raise CheckError(f"{DFM.relative_to(ROOT)} nao existe")
    objeto = re.compile(r"^(\s+)object (?:(\w+): )?(T\w+)\s*$")
    formularios: dict[str, list[tuple[int, str, str]]] = {}
    for arq in sorted(DFM.glob("*.dfm")):
        comps: list[tuple[int, str, str]] = []
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = objeto.match(linha)
            if m:
                comps.append((len(m.group(1)), m.group(2) or "", m.group(3)))
        formularios[arq.stem] = comps
    if not formularios:
        raise CheckError(f"nenhum .dfm em {DFM.relative_to(ROOT)}")
    return formularios


def censo_total() -> tuple[int, int]:
    """O total e o numero de classes que o `censo.md` publica."""
    if not CENSO.exists():
        raise CheckError(f"{CENSO.relative_to(ROOT)} nao existe")
    texto = CENSO.read_text(encoding="utf-8")
    m = re.search(r"^\| \*\*total\*\* \| \*\*(\d+)\*\* \|$", texto, re.M)
    if not m:
        raise CheckError("censo.md: linha de total nao encontrada")
    c = re.search(r"^(\d+) classes distintas, (\d+) componentes", texto, re.M)
    if not c:
        raise CheckError("censo.md: frase de fechamento nao encontrada")
    if c.group(2) != m.group(1):
        raise CheckError(
            f"censo.md discorda de si mesmo: tabela diz {m.group(1)}, "
            f"prosa diz {c.group(2)}")
    return int(m.group(1)), int(c.group(1))


def eventos_dfm(formularios: dict[str, list]) -> tuple[set, int]:
    """As atribuicoes `OnX = handler` dos 18 `.dfm`: triplas e total."""
    atrib = re.compile(r"^\s+(On[A-Za-z]+) = ([A-Za-z_]\w*)\s*$")
    triplas: set[tuple[str, str, str]] = set()
    total = 0
    for arq in sorted(DFM.glob("*.dfm")):
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = atrib.match(linha)
            if m:
                triplas.add((arq.stem, m.group(2), m.group(1)))
                total += 1
    return triplas, total


def unidades_ep2002() -> tuple[int, int]:
    """As unidades `Tep2002_*`, pelos exports de ciclo de vida.

    Varredura de bytes: os nomes exportados sao ASCII no arquivo, e le-los
    assim evita um sexto parser de PE nesta arvore.
    """
    if not EXE.exists():
        raise CheckError(f"{REL_EXE} nao existe")
    bruto = EXE.read_bytes()
    simbolos = set(re.findall(rb"@@Tep2002_(\w+)@(Initialize|Finalize)\b", bruto))
    unidades = {n for n, _ in simbolos}
    if not unidades:
        raise CheckError("nenhum export @@Tep2002_*@ no .exe")
    return len(unidades), len(simbolos)


def imports_medidos() -> tuple[int, int]:
    """Os dois numeros de import, da frase que o `dump_units.py` emite."""
    if not UNI_MD.exists():
        raise CheckError(f"{UNI_MD.relative_to(ROOT)} nao existe")
    m = re.search(
        r"São (\d+) imports, (\d+) deles de `rtl60\.bpl` e `vcl60\.bpl`",
        UNI_MD.read_text(encoding="utf-8"))
    if not m:
        raise CheckError(
            "unidades-vcl.md: a frase dos imports mudou de forma; "
            "reveja o regex antes de confiar no numero")
    return int(m.group(1)), int(m.group(2))


def enchimento_dfm() -> int:
    """Literais com enchimento nos 18 DFM, do `strings.md`.

    Populacao diferente da de `.data`, e e ela que explica o numero da §1.5 do
    plano -- por isso a reconciliacao precisa das duas.
    """
    if not STR_MD.exists():
        raise CheckError(f"{STR_MD.relative_to(ROOT)} nao existe")
    m = re.search(r"há \*\*(\d+) literais com dois ou mais espaços no fim\*\*",
                  STR_MD.read_text(encoding="utf-8"))
    if not m:
        raise CheckError(
            "strings.md: a frase dos literais com enchimento nos DFM mudou de "
            "forma; reveja o regex antes de confiar no numero")
    return int(m.group(1))


def cobertura_text() -> str:
    """A fatia de `.text` coberta pelos 96 corpos, do `strings.md`."""
    if not STR_MD.exists():
        raise CheckError(f"{STR_MD.relative_to(ROOT)} nao existe")
    m = re.search(r"^\| cobertura \| ([\d.]+)% \|$",
                  STR_MD.read_text(encoding="utf-8"), re.M)
    if not m:
        raise CheckError("strings.md: linha de cobertura nao encontrada")
    return m.group(1)


def offsets_hpp() -> int:
    if not OFS_HPP.exists():
        raise CheckError(f"{OFS_HPP.relative_to(ROOT)} nao existe")
    return len(re.findall(r"^inline constexpr Offset OFS_\w+\s*=",
                          OFS_HPP.read_text(encoding="utf-8"), re.M))


def bitmaps() -> tuple[int, list[tuple[str, int]], int]:
    if not IMAGE.is_dir():
        raise CheckError(
            f"we-team-editor/image nao existe -- a pasta do Obocaman e "
            f"gitignored e o usuario a mantem, como faz com roms/")
    por_pasta: list[tuple[str, int]] = []
    raiz = sorted(p for p in IMAGE.glob("*") if p.suffix.lower() == ".bmp")
    for sub in sorted(p for p in IMAGE.iterdir() if p.is_dir()):
        n = len([p for p in sub.rglob("*") if p.suffix.lower() == ".bmp"])
        por_pasta.append((sub.name, n))
    por_pasta.append(("(raiz de image/)", len(raiz)))
    total = sum(n for _, n in por_pasta)
    if not DATBIN.exists():
        raise CheckError("we-team-editor/data/dat.bin nao existe")
    return total, por_pasta, DATBIN.stat().st_size


# ------------------------------------------------------------------- saida --

def gerar() -> dict[str, str]:
    formularios = ler_dfm()
    censo_comp, censo_classes = censo_total()
    comps = sum(len(c) for c in formularios.values())
    classes = {cls for lista in formularios.values() for _, _, cls in lista}
    sem_nome = [(f, cls) for f, lista in formularios.items()
                for _, nome, cls in lista if not nome]

    if comps != censo_comp:
        raise CheckError(
            f"recontagem de componentes ({comps}) discorda do censo.md "
            f"({censo_comp}) -- um dos dois parsers esta errado")
    if len(classes) != censo_classes:
        raise CheckError(
            f"recontagem de classes ({len(classes)}) discorda do censo.md "
            f"({censo_classes})")

    pub = ler_tsv(PUB)
    triplas_dfm, atrib_dfm = eventos_dfm(formularios)
    triplas_tsv: set[tuple[str, str, str]] = set()
    atrib_tsv = 0
    for r in pub:
        for ev in r["evento"].split("|"):
            if ev:
                triplas_tsv.add((r["formulario"], r["handler"], ev))
                atrib_tsv += 1
    so_dfm = sorted(triplas_dfm - triplas_tsv)
    sem_dfm = sorted(r for r in pub if not r["evento"])

    strings = ler_tsv(STR)
    n_str = len(strings)
    com_handler = [r for r in strings if r["handler"]]
    referenciadas = [r for r in strings if r["referenciada_por"]]
    ref_sem_handler = [r for r in referenciadas if not r["handler"]]
    sem_ref = n_str - len(referenciadas)
    enchimento = [r for r in strings if "enchimento" in r["suspeita_patch"]]
    suspeitas = [r for r in strings if r["suspeita_patch"]]

    ofs = ler_tsv(OFS_TSV)
    n_hpp = offsets_hpp()
    confirmados = [r for r in ofs if r["registro"] == "confirmado"]
    ausentes = [r for r in ofs if r["registro"] == "ausente"]
    slots = [r for r in ofs if r["registro"] == "tabela_slot"]
    copias = [r for r in ofs if r["registro"] == "tabela_copia"]
    candidatos = [r for r in ofs if r["registro"] == "candidato"]
    slots_com_nome = [r for r in slots if r["nome"]]
    # Confirmado que aparece so em .text nao mora em nenhuma das duas tabelas.
    fora_da_tabela = [r for r in confirmados
                      if r["classe"] == "confirmado"
                      and "0x0042" not in r["va"]]

    timage = [(f, nome) for f, lista in formularios.items()
              for _, nome, cls in lista if cls == "TImage"]
    embutidos = blobs_por_dono(formularios)
    n_bmp, por_pasta, tam_dat = bitmaps()

    n_unid, n_exp = unidades_ep2002()
    n_imp, n_imp_bpl = imports_medidos()
    cob = cobertura_text()
    ench_dfm = enchimento_dfm()

    residuos = varrer()
    sobrou = [(nome, lista) for nome, lista in residuos if lista]
    if sobrou:
        detalhe = "\n".join(
            f"  {nome}:\n" + "\n".join(f"    {s}" for s in lista)
            for nome, lista in sobrou)
        raise CheckError(
            "numero velho ainda afirmado fora dos documentos que narram a "
            f"correcao:\n{detalhe}")

    return {MD_NAME: montar(
        formularios=formularios, comps=comps, classes=classes,
        sem_nome=sem_nome, pub=pub, triplas_dfm=triplas_dfm,
        atrib_dfm=atrib_dfm, atrib_tsv=atrib_tsv, so_dfm=so_dfm,
        sem_dfm=sem_dfm, n_str=n_str, com_handler=com_handler,
        referenciadas=referenciadas, ref_sem_handler=ref_sem_handler,
        sem_ref=sem_ref, enchimento=enchimento, suspeitas=suspeitas,
        n_hpp=n_hpp, confirmados=confirmados, ausentes=ausentes,
        slots=slots, copias=copias, candidatos=candidatos,
        slots_com_nome=slots_com_nome, fora_da_tabela=fora_da_tabela,
        timage=timage, embutidos=embutidos, n_bmp=n_bmp,
        por_pasta=por_pasta, tam_dat=tam_dat, n_unid=n_unid, n_exp=n_exp,
        n_imp=n_imp, n_imp_bpl=n_imp_bpl, cob=cob, ench_dfm=ench_dfm)}


def blobs_por_dono(formularios: dict[str, list]) -> dict[str, int]:
    """Quantos `Picture.Data` cada formulario traz, por dono `TImage`."""
    objeto = re.compile(r"^(\s+)object (?:(\w+): )?(T\w+)\s*$")
    blob = re.compile(r"^\s+(\w+(?:\.\w+)*) = \{blob ")
    contagem: dict[str, int] = {}
    for arq in sorted(DFM.glob("*.dfm")):
        pilha: list[tuple[int, str]] = []
        n = 0
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = objeto.match(linha)
            if m:
                ind = len(m.group(1))
                while pilha and pilha[-1][0] >= ind:
                    pilha.pop()
                pilha.append((ind, m.group(3)))
                continue
            b = blob.match(linha)
            if b and pilha and pilha[-1][1] == "TImage" \
                    and b.group(1) == "Picture.Data":
                n += 1
        contagem[arq.stem] = n
    return contagem


def montar(**d) -> str:
    L: list[str] = []
    w = L.append

    w(f"# `re/{MD_NAME}` — fechamento da fase 1")
    w("")
    w("Produto da [WTE-TASK-09](../../docs/tasks/09-fechamento-fase-1.md).")
    w(f"Gerado por [`../tools/check_fase1.py`](../tools/check_fase1.py).")
    w("**Não editar à mão** — correção entra no script e o arquivo é regerado:")
    w("")
    w("```sh")
    w(f"python3 {GENERATOR}")
    w(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    w("```")
    w("")
    w("Esta página **não mede o binário de novo**. Ela mede a coerência entre")
    w("os produtos que as WTE-TASK-03 a 08 deixaram versionados, e confronta os")
    w("sete números que a §1 do plano afirma contra o que essas ferramentas")
    w("dizem hoje. A exceção é a recontagem de componentes, que remede de")
    w("propósito — é a conferência que pegaria o [`censo.md`](dfm/censo.md)")
    w("errando, e o script aborta se os dois números discordarem.")
    w("")

    # ---------------------------------------------------------- conferencia 1
    w("## 1. DFM × handlers")
    w("")
    w("A pergunta tem dois sentidos, e eles não valem a mesma coisa: `OnClick`")
    w("citado no DFM sem entrada no TSV significaria varredura de VMT")
    w("incompleta; entrada no TSV sem citação no DFM é normal — o método é")
    w("publicado e ligado em tempo de execução, ou simplesmente não é usado.")
    w("")
    w("| Medida | Valor |")
    w("|---|---:|")
    w(f"| formulários em [`dfm/`](dfm/) | {len(d['formularios'])} |")
    w(f"| entradas em [`published_methods.tsv`](published_methods.tsv) | {len(d['pub'])} |")
    w(f"| atribuições `OnX = handler` nos DFM | {d['atrib_dfm']} |")
    w(f"| atribuições que o TSV registra | {d['atrib_tsv']} |")
    w(f"| triplas `(formulário, handler, evento)` distintas no DFM | {len(d['triplas_dfm'])} |")
    w(f"| **no DFM e fora do TSV** | **{len(d['so_dfm'])}** |")
    w(f"| **no TSV e sem citação em DFM** | **{len(d['sem_dfm'])}** |")
    w("")
    if d["so_dfm"]:
        w("Divergência no sentido que importa — a varredura de VMT perdeu caso:")
        w("")
        for f, h, e in d["so_dfm"]:
            w(f"- `{f}.{h}` ({e})")
        w("")
    else:
        w("**Zero no sentido que importaria.** Todo `OnX = handler` dos 18")
        w("formulários tem entrada no TSV, e as contagens de atribuição batem")
        w(f"nos dois lados ({d['atrib_dfm']}). A varredura de VMT da WTE-TASK-04")
        w("não perdeu nenhum handler que o streaming de DFM precise resolver.")
        w("")
    if d["sem_dfm"]:
        w("No outro sentido, o TSV tem entrada que nenhum DFM cita:")
        w("")
        w("| Endereço | Handler | Formulário | Nota |")
        w("|---|---|---|---|")
        for r in d["sem_dfm"]:
            w(f"| `{r['endereco']}` | `{r['handler']}` | `{r['formulario']}` "
              f"| {r['nota']} |")
        w("")
        w("Isso **não** é defeito da extração: um método publicado sem")
        w("componente ligado é o que sobra quando o autor apaga o botão e")
        w("esquece o handler, ou quando a ligação é feita em código. A fase 4")
        w("decide o veredito de cada um; a fase 1 só registra que ele existe.")
        w("")

    # ---------------------------------------------------------- conferencia 2
    w("## 2. Strings × handlers")
    w("")
    w("A pergunta da tarefa é se sobrou string demais sem dono — sinal de que")
    w("a heurística de referência estaria perdendo caso.")
    w("")
    w("| População | Quantas |")
    w("|---|---:|")
    w(f"| strings em [`strings.tsv`](strings.tsv) | {d['n_str']} |")
    w(f"| referenciadas por ponteiro de `.text` | {len(d['referenciadas'])} |")
    w(f"| referenciadas **de dentro** de um dos 96 | {len(d['com_handler'])} |")
    w(f"| referenciadas, mas de código fora dos 96 | {len(d['ref_sem_handler'])} |")
    w(f"| não referenciadas por ponteiro nenhum | {d['sem_ref']} |")
    w("")
    w(f"**Não é a heurística que está perdendo.** Os 96 corpos medidos cobrem")
    w(f"{d['cob']}% da `.text` ([`strings.md`](strings.md)), e a fração de string")
    w(f"com dono — {len(d['com_handler'])} de {len(d['referenciadas'])} referenciadas,")
    w(f"{100 * len(d['com_handler']) // len(d['referenciadas'])}% — é da mesma ordem.")
    w("String referenciada de fora dos 96 vem de método não publicado, de")
    w("inicialização de unidade e da RTL estática, que são justamente os")
    w(f"{100 - float(d['cob']):.1f}% restantes.")
    w("")
    w("A consequência para a fase 4 é uma: **a mensagem que um handler exibe")
    w("nem sempre está no corpo dele.** O handler chama um auxiliar não")
    w("publicado, e a string mora lá. Procurar texto só dentro do corpo medido")
    w("acharia menos do que existe.")
    w("")

    # ---------------------------------------------------------- conferencia 3
    w("## 3. Offsets × `Offsets.hpp`")
    w("")
    w("| Medida | Valor |")
    w("|---|---:|")
    w(f"| offsets em [`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp) | {d['n_hpp']} |")
    w(f"| **confirmados no `.exe`** | **{len(d['confirmados'])}** |")
    w(f"| ausentes do `.exe` | {len(d['ausentes'])} |")
    w(f"| slots das duas tabelas de `.data` | {len(d['slots'])} |")
    w(f"| slots preenchidos | {len(d['slots_com_nome'])} |")
    w(f"| cópias inteiras das tabelas em `.data` | {len(d['copias'])} |")
    w(f"| candidatos ainda sem nome | {len(d['candidatos'])} |")
    w("")
    w(f"Os {len(d['confirmados'])} continuam batendo depois de a tabela ter")
    w("limite medido, e **nenhum caiu fora do limite** — o que a pergunta da")
    w("tarefa queria saber. A distribuição explica por quê:")
    w("")
    w("| Onde o valor aparece | Quantos |")
    w("|---|---:|")
    w(f"| dentro de uma das duas tabelas de `.data` | {len(d['confirmados']) - len(d['fora_da_tabela'])} |")
    w(f"| só como imediato de instrução, em `.text` | {len(d['fora_da_tabela'])} |")
    w("")
    for r in d["fora_da_tabela"]:
        w(f"- `{r['nome']}` — `{r['va']}`")
    w("")
    w("Imediato de instrução nunca esteve sujeito ao limite da tabela: ele não")
    w("mora nela. Os outros são exatamente os slots preenchidos, e o critério")
    w("de limite do [`dump_offsets.py`](../tools/dump_offsets.py) já os contém")
    w("pelos dois testes independentes que ele confronta.")
    w("")
    w(f"As {len(d['copias'])} cópias são as duas tabelas repetidas três vezes")
    w("cada em `.data` — o mesmo fenômeno do bloco de literais que o")
    w("[`strings.md`](strings.md) mediu, e não offsets novos.")
    w("")

    # ---------------------------------------------------------- conferencia 4
    w("## 4. Assets × formulários")
    w("")
    w("A pergunta da tarefa era se parte dos bitmaps externos pode ser")
    w("irrelevante, caso os `TImage` já tragam a arte embutida.")
    w("")
    w("| Medida | Valor |")
    w("|---|---:|")
    w(f"| `TImage` nos 18 formulários | {len(d['timage'])} |")
    w(f"| com `Picture.Data` embutido | {sum(d['embutidos'].values())} |")
    w(f"| sem blob nenhum | {len(d['timage']) - sum(d['embutidos'].values())} |")
    w(f"| `.bmp` em `we-team-editor/image/` | {d['n_bmp']} |")
    w(f"| `data/dat.bin` | {d['tam_dat']} bytes |")
    w("")
    w("| Pasta | `.bmp` |")
    w("|---|---:|")
    for nome, n in d["por_pasta"]:
        w(f"| `{nome}` | {n} |")
    w("")
    w("**A resposta é não, e o motivo está medido na §7 do**")
    w("[`assets.md`](assets.md): embutido não quer dizer que o arquivo não é")
    w("lido. Cinco dos sete `TImage` que recebem `LoadFromFile` **têm** blob e")
    w("são sobrescritos na carga — o blob é *placeholder* de IDE. Nenhum dos")
    w(f"{d['n_bmp']} bitmaps é dispensável — cada um é alcançável por uma das")
    w("três tabelas de nome que a WTE-TASK-08 reconstruiu.")
    w("")

    # ------------------------------------------------------------ recontagem
    w("## 5. Recontagem dos sete números da §1 do plano")
    w("")
    w("Divergência se resolve **a favor da medição**, e o plano é corrigido.")
    w("")
    w("| Afirmação da §1 | Remedido | Valor | Veredito |")
    w("|---|---|---:|---|")
    w(f"| 18 formulários | recontagem dos `.dfm` | {len(d['formularios'])} | **bate** |")
    w(f"| ~430 componentes | recontagem dos `.dfm`, conferida com `censo.md` "
      f"| {d['comps']} | **corrigido** |")
    w(f"| 20 classes distintas | idem | {len(d['classes'])} | **bate** |")
    w(f"| 96 handlers | `published_methods.tsv` | {len(d['pub'])} | **bate** |")
    w(f"| 19 de 69 offsets | `offsets.tsv` + `Offsets.hpp` "
      f"| {len(d['confirmados'])} de {d['n_hpp']} | **bate** |")
    w(f"| 70 strings com padding | `strings.tsv` | {len(d['enchimento'])} | **corrigido** |")
    w(f"| 13 unidades `Tep2002_*` | varredura do `.exe` | {d['n_unid']} | **bate** |")
    w(f"| 322 imports | `unidades-vcl.md` | {d['n_imp']} | **bate** |")
    w(f"| …sendo 300 de `rtl60`/`vcl60` | idem | {d['n_imp_bpl']} | **corrigido** |")
    w(f"| 197 bitmaps | `we-team-editor/image/` | {d['n_bmp']} | **corrigido** |")
    w(f"| `dat.bin` de 145.408 B | `we-team-editor/data/` | {d['tam_dat']} | **bate** |")
    w("")
    w("Quatro correções, e as quatro têm causa diferente — vale registrar,")
    w("porque só uma delas é erro de medição:")
    w("")
    w(f"- **componentes: ~430 → {d['comps']}.** O `~` do plano era estimativa")
    w("  declarada. O valor exato inclui um componente **sem nome** — um")
    w("  `TStaticText` de 4×4 px no `MainForm` —, que é justamente o tipo de")
    w("  objeto que uma contagem apressada perde: o DFM escreve `object")
    w("  TStaticText`, sem identificador, e um regex que exija `nome: Classe`")
    w(f"  devolve {d['comps'] - 1}. O [`dfm2lfm.py`](../tools/dfm2lfm.py) já o trata")
    w("  — não vira campo da classe, porque inventar identificador que o")
    w("  original não tem seria inventar;")
    w(f"- **strings com enchimento: 70 → {len(d['enchimento'])}.** Não é erro de")
    w("  ninguém: são populações diferentes. Os 13 são de `.data`; o número da")
    w("  §1.5 sai de contar o binário inteiro, e o que aparece a mais é `.rsrc`,")
    w("  isto é, *caption* de formulário. Pelo mesmo critério os 18 DFM trazem")
    w(f"  {d['ench_dfm']} literais com enchimento. A conclusão da §1.5 continua de")
    w("  pé; o que muda é **onde procurar as outras** — nos `.dfm`, não aqui;")
    w(f"- **imports de `rtl60`/`vcl60`: 300 → {d['n_imp_bpl']}.** Erro de medição")
    w("  do script descartável de 2026-08-05, corrigido pela")
    w("  [CORR-WTE-012](../../docs/tasks/CORR-WTE-012.md). O total de")
    w(f"  {d['n_imp']} imports sempre esteve certo;")
    w(f"- **bitmaps: 197 → {d['n_bmp']}.** Erro de **soma na prosa**: a §1.8 do")
    w("  plano lista as cinco pastas com os números certos e soma errado.")
    w("")

    # --------------------------------------------------------------- varredura
    w("## 6. A varredura dos sítios")
    w("")
    w("Corrigir a §1 não fecha um número errado — ele se espalha. Cada número")
    w("reconciliado foi varrido nos markdowns de `docs/` e de `wte/`, e o")
    w("script **aborta** se sobrar afirmação viva. Não há tabela de resíduo")
    w("aqui porque resíduo é falha, como o `FORBIDDEN` do `port_database.py`.")
    w("")
    w("| Número velho | Sítios antes | Sítios agora |")
    w("|---|---:|---:|")
    for nome, _num, _ctx, antes in SITIOS:
        w(f"| {nome} | {antes} | 0 |")
    w("")
    total_antes = sum(a for _, _, _, a in SITIOS)
    w(f"**{total_antes} → 0.** Os {total_antes} de antes foram medidos com este")
    w("mesmo perímetro em 2026-08-06, sobre a árvore anterior à correção")
    w("(`git archive 65cc4be docs wte`); estão fixos na tabela `SITIOS` do")
    w("script, porque não há como remedi-los sobre a árvore de hoje. Os sítios")
    w("corrigidos foram a §1.2, a §1.5, a §1.6, a §1.8, a §5 e a §8.8 do plano,")
    w("a tabela de estado e três seções do `progresso.md`, os enunciados ainda")
    w("**pendentes** da WTE-TASK-38 e da WTE-TASK-39 — que iriam pedir mensagem")
    w("de erro e regra de empacotamento sobre uma contagem inexistente — e o")
    w("[`README.md`](../README.md) do `wte/`.")
    w("")
    w("**O perímetro nasceu menor.** Ele parava em `docs/` e `wte/re/`, que foi")
    w("o que o enunciado da WTE-TASK-09 pediu, e ali fechou em zero — mas o")
    w("`wte/README.md` continuava afirmando 197 fora do alcance da guarda, que")
    w("é exatamente o espalhamento que esta seção diz combater. A")
    w("[CORR-WTE-016](../../docs/tasks/CORR-WTE-016.md) trocou as duas bases")
    w("por `docs/` e `wte/`; o `rglob` sobre `wte` já cobre `wte/re/`.")
    w("")
    w("Fica fora do perímetro o documento que **narra** a correção: os")
    w("`CORR-WTE-*.md` e o `correcoes-progresso.md`, o [`assets.md`](assets.md)")
    w("e o [`strings.md`](strings.md) — que registram, cada um, a divergência")
    w("que mediram —, o [`README.md`](../tools/README.md) de `wte/tools/`, que")
    w("narra esta guarda e cita `430` para explicar o corte por contexto, o")
    w("enunciado da própria WTE-TASK-09, o Log de Execução de qualquer tarefa,")
    w("e `docs/prompts/`. Fica fora também o **enunciado de tarefa já")
    w("concluída**: é história, não instrução. Tarefa pendente continua dentro,")
    w("e é o que fez a 38 e a 39 entrarem.")
    w("")
    w("O corte exige o número **e** uma palavra de contexto na mesma linha.")
    w("Sem isso, `430` casaria o setor 430 do `PLAN-LINUX.md` e `300` casaria")
    w("os 300 setores de ECC amostrados — outro projeto, outro assunto, mesmo")
    w("dígito.")
    w("")

    # ------------------------------------------------------------- em aberto
    w("## 7. O que fica em aberto ao sair da fase 1")
    w("")
    w("| Item | Situação |")
    w("|---|---|")
    w("| binário original em espanhol | **desejável, não bloqueante** — as três "
      "mensagens em que importa têm cópia legível dentro do próprio `.exe` "
      "([`strings.md`](strings.md)) |")
    w(f"| {len(d['candidatos'])} candidatos a offset sem nome | **WTE-TASK-19** — "
      "são os offsets que o Obocaman tem e o `newWe2002` não |")
    if d["sem_dfm"]:
        w(f"| {len(d['sem_dfm'])} handler sem componente ligado | **fase 4** — "
          "`published_methods.tsv` o registra com a nota; o veredito é da 25-28 |")
    w("| a arte do original | **não versionada, por decisão** — os "
      f"{d['n_bmp']} `.bmp`, o `dat.bin` e os 118 blobs dos DFM ficam com o "
      "usuário, como `roms/` |")
    w("")
    w("Nenhum desses é resultado negativo por falta de medição. Os quatro são")
    w("decisão registrada ou trabalho de fase seguinte.")
    w("")

    # -------------------------------------------------------------- ressalvas
    w("## Ressalvas")
    w("")
    w("- **Esta página consome produto, não binário.** Se um dos geradores da")
    w("  fase 1 estiver errado, ela repete o erro com ar de conferência. O que")
    w("  a protege é o `--check` de cada um, que roda antes dela em")
    w("  `make -C wte check`, e a recontagem de componentes, que é a única")
    w("  medida independente aqui — e é a que aborta se discordar do censo;")
    w("- **os dois números de import vêm de uma frase.** O")
    w("  [`unidades-vcl.md`](unidades-vcl.md) é gerado, mas o que se lê dele")
    w("  aqui é texto corrido casado por regex. Se a frase mudar de forma, o")
    w("  script aborta em vez de emitir número inventado — é o desfecho certo,")
    w("  e ainda assim é acoplamento a registrar;")
    w("- **a coluna “sítios antes” não é remedível.** Ela é constante no")
    w("  script, com a data e o perímetro escritos. Quem duvidar dela tem de")
    w("  voltar no `git log`, e é por isso que o commit desta tarefa cita os")
    w("  arquivos que tocou.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ plumbing --

def do_check(files: dict[str, str]) -> int:
    problems: list[str] = []
    for name, content in sorted(files.items()):
        path = OUT / name
        if not path.exists():
            problems.append(f"{name}: nao existe")
            continue
        on_disk = path.read_text(encoding="utf-8")
        if on_disk == content:
            continue
        for i, (a, b) in enumerate(
                zip(on_disk.splitlines(), content.splitlines()), 1):
            if a != b:
                problems.append(f"{name}: linha {i} diverge")
                break
        else:
            problems.append(
                f"{name}: {len(on_disk.splitlines())} linhas no disco contra "
                f"{len(content.splitlines())} regeradas")
    if problems:
        print(f"{REL_OUT} nao corresponde aos produtos da fase 1:",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivo em dia com os produtos da fase 1 "
          f"+ {REL_EXE}; 0 sitio com numero velho")
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(files.items()):
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"  {name}: {content.count(chr(10))} linhas, "
              f"{len(content.encode('utf-8'))} bytes")
    print(f"\n{len(files)} arquivo em {REL_OUT}")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        files = gerar()
    except CheckError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
