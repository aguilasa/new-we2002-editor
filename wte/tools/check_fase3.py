#!/usr/bin/env python3
"""Fechamento da fase 3: a camada de dados e 100% gerada, e o app ja le o jogo?

Gera `wte/re/fase-3-fechamento.md` -- o produto da WTE-TASK-21. Irmao do
`check_fase1.py` e do `check_fase2.py`, e pela mesma razao: o fechamento de fase
so vale se os numeros dele sairem de ferramenta versionada. Contagem a mao em
doc ja se propagou neste repositorio (CORR-WTE-012, -014, -023).

## Por que o nome do arquivo nao e `fase-3.md`

Porque `fase-3.md` ja existe, e e de outra task: o **aceite da camada de dados**
da WTE-TASK-20, gerado pelo `compare_dumps.py`. Dois geradores escrevendo o
mesmo arquivo seria a duplicacao sem guarda que o `README.md` deste diretorio
manda evitar. Um mede *os valores batem?*; o outro, aqui, mede *quem escreveu o
codigo que os produz, e quem o consome*.

## O que ele mede

| Mede | Como |
|---|---|
| fracao gerada da camada de dados | linhas emitidas menos as linhas de porte a mao que moram DENTRO do gerador |
| entrada x saida | as 11 unidades de `src/core/` que o `UNITS` reivindica, contra os `.pas` emitidos |
| quem consome a camada | `uses` de `we2002_database` em `wte/src`, `wte/tests` e no `.lpr` |
| Ghidra na fase 3 | ocorrencias de `ghidra` nos artefatos que a fase produziu |

## A medida que importa, e por que ela nao e "100%"

Todo `.pas` da camada e saida de gerador -- nenhum foi editado a mao, e o
`port_database_pas.py --check` prova isso na bateria. Mas **nem toda linha
emitida e transpilacao**: as pecas da rota 3 (`CdImage`, `SquadNumbers`, o
sidecar, o `Reporter`) sao Pascal escrito a mao que mora nas constantes
`MANUAIS` / `TRECHOS_MANUAIS` do gerador. Chamar isso de "100% gerado" seria
verdade de arquivo e mentira de conteudo -- e a tese da §4.5 do plano fala de
conteudo.

Entao a conta separa as duas coisas, e cada bloco manual e **conferido dentro
da saida**: se o texto de um deles nao aparece mais no `.pas` que deveria
carrega-lo, isto aqui aborta em vez de publicar uma fracao inventada.

Uso:

    python3 wte/tools/check_fase3.py            # regenera
    python3 wte/tools/check_fase3.py --check    # confere contra o commitado
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_tables_pas as G  # noqa: E402  (a fonte das entradas de tabela)
import port_database_pas as P  # noqa: E402  (o gerador e a fonte dos manuais)

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "wte" / "src"
TESTS = ROOT / "wte" / "tests"
LPR = ROOT / "wte" / "wte.lpr"
RE_DIR = ROOT / "wte" / "re"
OUT = RE_DIR / "fase-3-fechamento.md"

GENERATOR = "wte/tools/check_fase3.py"
MARCA_GERADO = "NAO editar a mao"

# Os `.pas` da camada de dados, e quem emite cada um. A lista e fixa de
# proposito: unidade nova aqui e decisao, nao efeito colateral de glob.
DA_CAMADA: dict[str, str] = {
    "we2002_types.pas": "port_database_pas.py",
    "we2002_team.pas": "port_database_pas.py",
    "we2002_cdimage.pas": "port_database_pas.py",
    "we2002_textcodec.pas": "port_database_pas.py",
    "we2002_player.pas": "port_database_pas.py",
    "we2002_database.pas": "port_database_pas.py",
    "we2002_offsets.pas": "gen_tables_pas.py",
    "we2002_tables.pas": "gen_tables_pas.py",
}

# Artefatos que a fase 3 produziu, e onde a pergunta do Ghidra e feita. Nao
# entram aqui os produtos das fases 1, 2 e 4 -- `vmt.md` e da WTE-TASK-24, que
# e fase 4 e usa Ghidra por desenho.
ARTEFATOS_FASE_3 = [
    "tipos.md", "transpilador.md", "recusas.md", "fase-3.md",
    "offsets-novos.md", "crash.md", "crash-causa.md",
]

UNIDADE_DE_USES = re.compile(r"^\s*uses\b(.*?);", re.S | re.M)


class CheckError(Exception):
    pass


def linhas(texto: str) -> int:
    return len(texto.splitlines())


# ------------------------------------------------------- 1. fracao gerada --

def blocos_manuais() -> dict[str, list[tuple[str, str]]]:
    """Unidade -> [(rotulo, texto Pascal escrito a mao)], lido do gerador.

    A fonte e o proprio `port_database_pas.py`, e nao uma copia: se um bloco
    for reescrito la, o numero daqui muda junto. Copiar o texto para ca criaria
    a segunda copia que envelhece sozinha.
    """
    bruto: list[tuple[str, str, str]] = []
    for unidade, manual in P.MANUAIS.items():
        for rotulo, texto in (("interface", manual.interface),
                              ("implementacao", manual.implementacao),
                              ("corpos", manual.corpos)):
            bruto.append((unidade, rotulo, texto))
        for metodo, corpo in manual.metodos.items():
            bruto.append((unidade, f"metodo {metodo}", "\n".join(corpo)))
    for unidade, texto in P.MANUAL_TIPOS.items():
        bruto.append((unidade, "tipo", texto))
    for unidade, texto in P.MANUAL_DECLS.items():
        bruto.append((unidade, "declaracao", texto))

    # DEDUPE, e ele nao e zelo: `MANUAL_TIPOS["we2002_types"]` **e**
    # `MANUAL_TYPES.interface` -- o mesmo objeto, alcancado por dois caminhos,
    # porque o gerador reusa a constante em vez de copiar o texto. Somar os
    # dois inflava `we2002_types` de 54 para 97 linhas a mao, e a fracao
    # publicada sairia pessimista sem que nada acusasse.
    fora: dict[str, list[tuple[str, str]]] = {}
    vistos: set[tuple[str, str]] = set()
    for unidade, rotulo, texto in bruto:
        if not texto.strip() or (unidade, texto) in vistos:
            continue
        vistos.add((unidade, texto))
        fora.setdefault(unidade, []).append((rotulo, texto))
    return fora


def confere_bloco(alvo: Path, texto: str, rotulo: str) -> int:
    """Linhas do bloco, depois de provar que ele esta MESMO na saida.

    **Casa por linha util e CONTA todas.** As duas reguas sao de proposito, e
    a separacao delas e a CORR-WTE-051:

    - o casamento ignora linha em branco porque ela casaria com qualquer
      coisa, e ignora indentacao porque o gerador reindenta o que poe dentro
      de `implementation`;
    - a contagem inclui a linha em branco porque ela **e** parte do bloco
      escrito a mao, foi emitida junto, e o total do arquivo (`linhas()`)
      tambem a conta. Devolver o numero do casamento como se fosse contagem
      subtraia 277 linhas uteis de um total de 3692 com brancos, e as 26
      linhas em branco dos blocos manuais eram creditadas a coluna
      **por regra** -- transpilacao de linha vazia que veio de constante.

    Uma linha do bloco que sumiu da saida significa que o bloco deixou de ser
    emitido -- e a fracao publicada estaria contando codigo que nao existe.
    """
    saida = {l.strip() for l in alvo.read_text(encoding="utf-8").splitlines()}
    uteis = [l.strip() for l in texto.splitlines() if l.strip()]
    faltando = [l for l in uteis if l not in saida]
    if faltando:
        raise CheckError(
            f"{alvo.name}: o bloco manual {rotulo!r} nao aparece na saida "
            f"({len(faltando)} de {len(uteis)} linhas ausentes; a primeira e "
            f"{faltando[0]!r}) -- o gerador mudou de forma e a fracao ficaria "
            f"errada")
    return linhas(texto)


def fracao_gerada() -> dict:
    por_arquivo = []
    manuais = blocos_manuais()
    total = mao = 0
    for nome, gerador in DA_CAMADA.items():
        alvo = SRC / nome
        if not alvo.exists():
            raise CheckError(f"falta {alvo.relative_to(ROOT)} -- a fase 3 nao "
                             f"esta completa")
        texto = alvo.read_text(encoding="utf-8")
        if MARCA_GERADO not in texto:
            raise CheckError(f"{nome}: sem a marca {MARCA_GERADO!r} no "
                             f"cabecalho -- ou nao e gerado, ou o gerador "
                             f"mudou o cabecalho")
        n = linhas(texto)
        unidade = alvo.stem
        m = sum(confere_bloco(alvo, t, r)
                for r, t in manuais.get(unidade, []))
        por_arquivo.append((nome, gerador, n, m))
        total += n
        mao += m
    return {"por_arquivo": por_arquivo, "total": total, "mao": mao,
            "regra": total - mao}


# ------------------------------------------------------ 2. entrada x saida --

def entrada_de_tabelas() -> list[Path]:
    """As entradas do `gen_tables_pas.py`, lidas DELE.

    Nao ha lista equivalente ao `UNITS` naquele gerador, mas ha as tres
    constantes -- e le-las e o que impede a segunda copia que envelhece
    sozinha, pelo mesmo motivo que `blocos_manuais()` le o `port_database_pas`
    em vez de transcrever os blocos.
    """
    return [G.TABLES_CPP, G.TABLES_HPP, G.OFFSETS_HPP]


def entrada_por_gerador() -> dict[str, list[tuple[str, int]]]:
    """Gerador -> [(arquivo de entrada, linhas)].

    Existe separado porque a razao entrada x saida so diz alguma coisa quando
    os dois lados sao do MESMO gerador. A versao anterior dividia a saida dos
    dois (3692) pela entrada de um so (2504, o `UNITS` do transpilador), o que
    creditava ao transpilador 708 linhas que o `gen_tables_pas.py` emitiu
    (CORR-WTE-050).
    """
    fora: dict[str, list[tuple[str, int]]] = {}
    for _, arquivos in P.UNITS:
        for rel in arquivos:
            caminho = P.CORE / rel
            if not caminho.exists():
                raise CheckError(f"o UNITS reivindica {rel}, que nao existe")
            fora.setdefault("port_database_pas.py", []).append(
                (rel, linhas(caminho.read_text(encoding="utf-8"))))
    for caminho in entrada_de_tabelas():
        if not caminho.exists():
            raise CheckError(f"o gen_tables_pas reivindica {caminho}, que nao "
                             f"existe")
        fora.setdefault("gen_tables_pas.py", []).append(
            (caminho.relative_to(P.CORE).as_posix(),
             linhas(caminho.read_text(encoding="utf-8"))))
    return fora


def conferir_entradas(entrada: dict[str, list[tuple[str, int]]]) -> None:
    """Todo gerador que aparece em `DA_CAMADA` tem entrada no denominador.

    Sem isto, acrescentar um terceiro gerador a `DA_CAMADA` voltaria a inflar
    a razao em silencio -- que e exatamente o que aconteceu quando o
    `gen_tables_pas.py` entrou.
    """
    faltando = sorted(set(DA_CAMADA.values()) - set(entrada))
    if faltando:
        raise CheckError(
            f"a saida conta {', '.join(faltando)}, e a entrada desse(s) "
            f"gerador(es) nao esta no denominador -- a razao compararia "
            f"populacoes diferentes")


def entrada_do_transpilador() -> tuple[list[tuple[str, int]], int]:
    fora = entrada_por_gerador()["port_database_pas.py"]
    return fora, sum(n for _, n in fora)


# --------------------------------------------------------- 3. consumidores --

def consumidores() -> tuple[list[str], list[str]]:
    """Quem da `uses` na camada de dados, separado em casca e teste.

    E a medida que responde "o app ja le o jogo?" sem depender de opiniao: se
    nenhuma unidade de `wte/src` que nao seja a propria camada a importa, o
    app **nao** le, por mais que a camada compile.
    """
    casca, teste = [], []
    alvos = ([(p, "casca") for p in sorted(SRC.glob("*.pas"), key=lambda p: p.as_posix())]
             + [(p, "teste") for p in sorted(TESTS.glob("*.pas"), key=lambda p: p.as_posix())]
             + [(LPR, "casca")])
    for caminho, especie in alvos:
        if caminho.name in DA_CAMADA:
            continue
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        usa = any("we2002_database" in m.group(1)
                  for m in UNIDADE_DE_USES.finditer(texto))
        if usa:
            rel = caminho.relative_to(ROOT / "wte").as_posix()
            (casca if especie == "casca" else teste).append(rel)
    if not teste:
        raise CheckError("nenhum teste da `uses we2002_database` -- os dumps "
                         "da WTE-TASK-20 nao teriam como existir")
    return casca, teste


# -------------------------------------------------------------- 4. Ghidra --

def ghidra_na_fase_3() -> list[tuple[str, int, str]]:
    """(artefato, ocorrencias, primeira linha que cita) -- vazio e o esperado."""
    fora = []
    for nome in ARTEFATOS_FASE_3:
        caminho = RE_DIR / nome
        if not caminho.exists():
            raise CheckError(f"falta {caminho.relative_to(ROOT)} -- artefato "
                             f"de fase 3 que o fechamento conta")
        citando = [l.strip() for l in
                   caminho.read_text(encoding="utf-8").splitlines()
                   if "ghidra" in l.lower()]
        if citando:
            fora.append((nome, len(citando), citando[0]))
    return fora


# --------------------------------------------------------------- markdown --

def gerar() -> str:
    frac = fracao_gerada()
    entrada_ger = entrada_por_gerador()
    conferir_entradas(entrada_ger)
    saida_ger: dict[str, int] = {}
    for nome, gerador, n, _ in frac["por_arquivo"]:
        saida_ger[gerador] = saida_ger.get(gerador, 0) + n
    casca, teste = consumidores()
    ghidra = ghidra_na_fase_3()

    L: list[str] = []
    w = L.append
    w("# `re/fase-3-fechamento.md` — o aceite da fase 3")
    w("")
    w(f"**Gerado por [`{GENERATOR}`](../tools/check_fase3.py) — não editar à "
      f"mão.**")
    w("")
    w("Produto da [WTE-TASK-21](../../docs/tasks/concluidos/21-fechamento-fase-3.md). O")
    w("irmão é [`fase-3.md`](fase-3.md), da WTE-TASK-20, e a divisão é de")
    w("pergunta: lá se mede se **os valores batem**; aqui, **quem escreveu o**")
    w("**código que os produz** e **quem o consome**.")
    w("")
    w("---")
    w("")
    w("## 1. A camada de dados é gerada — e quanto dela é transpilação")
    w("")
    w("Os oito `.pas` são saída de gerador, sem exceção: nenhum foi editado à")
    w("mão, e quem prova isso é o `--check` dos dois geradores, na bateria.")
    w("Mas **arquivo gerado não quer dizer conteúdo transpilado**: as peças da")
    w("rota 3 ([`recusas.md`](recusas.md)) são Pascal escrito à mão que mora")
    w("nas constantes `MANUAIS` e `TRECHOS_MANUAIS` do gerador, e sai emitido")
    w("junto. A coluna **à mão** conta essas linhas, e cada bloco é conferido")
    w("dentro da própria saída antes de entrar na conta.")
    w("")
    w("**A régua é a mesma nas três colunas: linha física, branco incluído.**")
    w("Dizer isso importa porque as duas primeiras já foram contadas por réguas")
    w("diferentes — total com branco menos manual sem branco —, e as 26 linhas")
    w("em branco dos blocos manuais acabavam creditadas a *por regra*")
    w("([CORR-WTE-051](../../docs/tasks/concluidos/CORR-WTE-051.md)). O casamento de cada")
    w("bloco contra a saída continua ignorando branco e indentação, que é outra")
    w("pergunta: *este bloco ainda é emitido?*")
    w("")
    w("| arquivo | gerador | linhas | à mão | por regra |")
    w("|---|---|---:|---:|---:|")
    for nome, gerador, n, m in frac["por_arquivo"]:
        w(f"| `wte/src/{nome}` | `{gerador}` | {n} | {m} | {n - m} |")
    w(f"| **total** | | **{frac['total']}** | **{frac['mao']}** "
      f"| **{frac['regra']}** |")
    w("")
    pct = 100.0 * frac["regra"] / frac["total"]
    w(f"**{pct:.1f}% da camada de dados é transpilação por regra** — "
      f"{frac['regra']} linhas")
    w(f"contra {frac['mao']} escritas à mão, e as")
    w("escritas à mão são as quatro peças que o")
    w("[`tipos.md`](tipos.md) já tinha decidido que **não são** transpiláveis:")
    w("`CdImage` (`std::fstream`), `SquadNumbers` (bitfield), o sidecar")
    w("`_url.txt` e o `Reporter` (`std::function`).")
    w("")
    w("A tese da §4.5 do plano — *a Fase 3 deixa de ser porte manual e vira")
    w("execução de gerador mais conferência* — se sustenta com essa ressalva")
    w("escrita: o que sobrou de manual não foi porte de lógica do editor, foi")
    w("o encontro com a biblioteca padrão de outra linguagem.")
    w("")
    w("---")
    w("")
    w("## 2. Entrada × saída")
    w("")
    w("**A razão é por gerador.** Os oito `.pas` saem de *dois*, e dividir a")
    w("soma dos dois pela entrada de um só creditava ao transpilador linhas que")
    w("o `gen_tables_pas.py` emitiu")
    w("([CORR-WTE-050](../../docs/tasks/concluidos/CORR-WTE-050.md)).")
    w("")
    w("| entrada | gerador | linhas |")
    w("|---|---|---:|")
    for gerador in sorted(entrada_ger):
        for rel, n in entrada_ger[gerador]:
            w(f"| `src/core/{rel}` | `{gerador}` | {n} |")
    w("")
    w("| gerador | entrada | saída | razão |")
    w("|---|---:|---:|---:|")
    for gerador in sorted(entrada_ger):
        ent = sum(n for _, n in entrada_ger[gerador])
        sai = saida_ger[gerador]
        w(f"| `{gerador}` | {ent} | {sai} | {sai / ent:.2f} |")
    tot_ent = sum(n for lista in entrada_ger.values() for _, n in lista)
    w(f"| **total** | **{tot_ent}** | **{frac['total']}** "
      f"| **{frac['total'] / tot_ent:.2f}** |")
    w("")
    r_transp = (saida_ger["port_database_pas.py"]
                / sum(n for _, n in entrada_ger["port_database_pas.py"]))
    r_tab = (saida_ger["gen_tables_pas.py"]
             / sum(n for _, n in entrada_ger["gen_tables_pas.py"]))
    w(f"O transpilador **infla** ({r_transp:.2f}): Pascal quer `begin` e `end`")
    w("onde o C++ tem chave, e declaração de variável no topo do corpo. O")
    w(f"gerador de tabelas **encolhe** ({r_tab:.2f}): a mesma tabela cabe em")
    w("menos linha de Pascal do que de inicializador C++. Uma razão só, sobre")
    w("a soma, esconderia os dois efeitos e não descreveria nenhum dos dois")
    w("geradores.")
    w("")
    w("As duas contagens saem de ferramenta: a entrada do transpilador é o")
    w("`UNITS` dele, a do outro são as três constantes do")
    w("`gen_tables_pas.py`, e o `test_nenhuma_entrada_do_core_fica_de_fora`")
    w("reprova arquivo de `src/core/` que ninguém reivindicou.")
    w("")
    w("---")
    w("")
    w("## 3. O app já lê o jogo?" if casca
      else "## 3. O app ainda não lê o jogo")
    w("")
    w("A pergunta que a task manda responder, medida por `uses`:")
    w("")
    w(f"- **{len(casca)}** unidade(s) da casca (`wte/src`, `wte.lpr`) importam"
      f" a camada de dados"
      + (": " + ", ".join(f"`{c}`" for c in casca) if casca else ";"))
    w(f"- **{len(teste)}** de teste importam: "
      + ", ".join(f"`{t}`" for t in teste) + ".")
    w("")
    if casca:
        w("A integração mínima **já existe** — e este documento precisa ser")
        w("relido, porque ele foi escrito quando ela não existia.")
    else:
        w("Ou seja: a camada compila, é exercitada por dois programas de")
        w("console e **nenhum formulário a consome**. Abrir a imagem pelo")
        w("`TOpenDialog` do `MainForm` e popular o combo de times é trabalho")
        w("de **handler**, e handler tem gate próprio — a")
        w("[WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md) antes da")
        w("[WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md). Fazer a")
        w("integração aqui seria implementar `boton_dialogo_weClick` e")
        w("`lista_equiposChange` sem o gate que os julga, que é exatamente o")
        w("que o `progresso.md` chama de *cada implementação é opinião*.")
    w("")
    w("---")
    w("")
    w("## 4. Ghidra: não foi necessário")
    w("")
    w("A fase 3 fecha **sem decompilador**, que é o cenário bom previsto pelo")
    w("plano. Medido nos artefatos que a fase produziu:")
    w("")
    w("| artefato | linhas citando `ghidra` |")
    w("|---|---:|")
    for nome in ARTEFATOS_FASE_3:
        achado = next((o for o in ghidra if o[0] == nome), None)
        w(f"| [`{nome}`]({nome}) | {achado[1] if achado else 0} |")
    w("")
    if ghidra:
        w("As citações existentes são **negativas ou de contexto**, e ficam"
          " transcritas:")
        w("")
        for nome, _, primeira in ghidra:
            w(f"- `{nome}`: {primeira}")
        w("")
    w("O único uso real de Ghidra no projeto é a")
    w("[WTE-TASK-24](../../docs/tasks/concluidos/24-ghidra-convencao-borland.md), que é")
    w("**fase 4** e existe para isso. Consequência para a estimativa: a fase 4")
    w("não herda dívida de decompilação da 3 — começa com o Ghidra já")
    w("configurado e nenhum trecho de fase 3 dependendo dele.")
    w("")
    w("---")
    w("")
    w("## 5. O que a fase 3 **não** prova")
    w("")
    w("- **Gravar pela janela.** A fase prova leitura e prova gravação")
    w("  headless, com os dois lados byte a byte iguais. Gravação dirigida por")
    w("  clique é a WTE-TASK-22 em diante.")
    w("- **Comportamento.** Os 96 handlers continuam stubs que logam. A camada")
    w("  de dados não sabe nada sobre eles.")
    w("- **Os `OFS_*` que o `we2002_core` não nomeia.** As faixas sem dono que")
    w("  a [WTE-TASK-19](../../docs/tasks/concluidos/19-os-50-offsets-restantes.md)")
    w("  mediu — a maior é a região do uniforme — não têm lado C++, então")
    w("  nenhum diff Pascal × C++ as alcança. Nomeá-las é fase 4 e 5.")
    w("- **Que o `Load` do sidecar funcione.** Nenhum dos dois lados lê")
    w("  `_url.txt` no `Load`; isso é do app.")
    w("")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    checando = "--check" in argv
    try:
        texto = gerar()
    except CheckError as e:
        print(f"check_fase3: {e}", file=sys.stderr)
        return 2
    rel = OUT.relative_to(ROOT)
    if checando:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texto:
            print(f"check_fase3: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"check_fase3: {rel}: ok")
        return 0
    OUT.write_text(texto, encoding="utf-8")
    print(f"check_fase3: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
