#!/usr/bin/env python3
"""Remede a tabela `PROPRIEDADES` do `dfm2lfm.py` contra a LCL instalada.

O cabecalho do `dfm2lfm.py` afirma que `ACEITA`/`DESCARTA` "nao e palpite:
saiu das fontes da LCL 3.0 [...] varrendo as secoes `published`". A varredura
foi feita de verdade e o resultado esta certo -- mas foi um script
descartavel. Nada em `make -C wte check` tocava `/usr/lib/lazarus`, nenhum
teste do `test_dfm2lfm.py` mencionava a LCL, e `LCL_VERSAO` era um pino de
versao que ninguem lia. Este script e o varredor virando ferramenta
(CORR-WTE-020).

Por que importa. `ACEITA` e a lista do que sai **verbatim** para o `.lfm`.
Propriedade que entre ali por engano -- ou que a LCL perca numa versao nova --
nao aborta e nao vira descarte: e emitida, o `--check` do `dfm2lfm.py` fica
verde porque compara a saida consigo mesma, o `lazbuild` compila porque `{$R}`
so embute bytes, e a **janela explode ao abrir**. Contra isso o gerador nao
tinha guarda nenhuma.

O que e conferido:

1. **A versao.** `laz_major`/`laz_minor` de `components/lazutils/lazversion.pas`
   tem de bater com `LCL_VERSAO`. Divergiu, aborta antes de varrer -- e o que
   faz o pino pinar. Remedir noutra versao e trabalho, nao acidente.
2. **`ACEITA`** -- toda entrada tem `published` correspondente na classe ou em
   algum ancestral, com a excecao **nomeada** das oito `Left`/`Top` de
   componente nao visual (lista fechada em `EXCECOES_DESIGNINFO`, nao um `if`
   generico).
3. **`DESCARTA`** -- nenhuma entrada tem.
4. **`IDENTIFICADORES` e `ELEMENTOS_DE_CONJUNTO`** -- todo nome ocorre nas
   fontes da LCL.

A tabela continua tendo **um dono so**: este script a le importando o
`dfm2lfm.py`, nunca a duplica.

Sobre `Left`/`Top` em componente nao visual (`TTimer`, `TActionList`,
`TOpenDialog`, `TSaveDialog`): nao aparecem em secao `published` nenhuma e
ainda assim sao validos -- o `TComponent.DefineProperties` da FCL os define
sobre o `DesignInfo`, e o `.lfm` do proprio Lazarus os escreve assim. Sao
excecao de verdade, e por isso estao nomeadas uma a uma.

Uso:

    python3 wte/tools/check_lcl_props.py            # relatorio
    python3 wte/tools/check_lcl_props.py --check    # so o veredito; 2 se falha
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dfm2lfm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
# Onde a arvore do Lazarus mora, e por que sao duas variaveis.
#
# `/usr/lib/lazarus/<versao>/` e o layout da distribuicao: a versao e um nivel
# de diretorio, e por isso `LCL_BASE` e so a raiz. Nem toda instalacao tem esse
# nivel -- a do Windows poe a arvore inteira em `C:\lazarus`, e a do
# fpcupdeluxe num diretorio escolhido pelo usuario. Para essas, `WTE_LAZARUS_DIR`
# aponta a ARVORE (a que contem `lcl/` e `components/lazutils/lazversion.pas`)
# e o nivel de versao sai do caminho.
#
# A CONFERENCIA DE VERSAO CONTINUA VALENDO nos dois casos: o `lazversion.pas`
# e que decide, nao o nome do diretorio. Apontar `WTE_LAZARUS_DIR` para uma
# arvore que nao seja a `LCL_VERSAO` pinada faz o script recusar -- e deve, e o
# ponto dele.
LCL_BASE = Path(os.environ.get("WTE_LAZARUS_BASE", "/usr/lib/lazarus"))
GENERATOR = "wte/tools/check_lcl_props.py"

# A chave que o dfm2lfm usa para o formulario raiz mapeia para a classe real.
CLASSE_DO_FORM = "TForm"

# `Left`/`Top` de componente nao visual: vem do `TComponent.DefineProperties`
# sobre o `DesignInfo`, nao de secao `published`. Lista fechada de proposito --
# um `if prop in ("Left", "Top")` generico deixaria passar `Left` numa classe
# visual que a LCL viesse a perder.
EXCECOES_DESIGNINFO = frozenset({
    ("TActionList", "Left"), ("TActionList", "Top"),
    ("TOpenDialog", "Left"), ("TOpenDialog", "Top"),
    ("TSaveDialog", "Left"), ("TSaveDialog", "Top"),
    ("TTimer", "Left"), ("TTimer", "Top"),
})


class CheckError(RuntimeError):
    """LCL ausente, versao divergente, ou tabela em desacordo com o disco."""


# ------------------------------------------------------------------ versao --

def caminho_da_lcl(versao: str) -> Path:
    """A arvore da LCL da versao pinada, conferida contra o `lazversion.pas`."""
    arvore = os.environ.get("WTE_LAZARUS_DIR")
    raiz = Path(arvore) if arvore else LCL_BASE / versao
    lcl = raiz / "lcl"
    if not lcl.is_dir():
        raise CheckError(
            f"LCL nao encontrada em {lcl} -- LCL_VERSAO do dfm2lfm.py diz "
            f"{versao!r}. Instale a versao pinada ou remeda a tabela na que "
            f"estiver no disco (nao edite a tabela a mao)")
    no_disco = versao_no_disco(raiz)
    if no_disco != versao:
        raise CheckError(
            f"LCL_VERSAO = {versao!r} mas {raiz} declara {no_disco!r} -- "
            f"a tabela PROPRIEDADES foi medida noutra versao. Remedir e "
            f"trabalho: rode este script contra a nova e concilie")
    return lcl


def versao_no_disco(raiz: Path) -> str:
    """`<major>.<minor>` lido do `lazversion.pas` da arvore."""
    fonte = raiz / "components" / "lazutils" / "lazversion.pas"
    if not fonte.is_file():
        raise CheckError(f"{fonte} nao existe -- arvore da LCL incompleta")
    texto = fonte.read_text(encoding="utf-8", errors="replace")
    partes = []
    for campo in ("laz_major", "laz_minor"):
        m = re.search(rf"^\s*{campo}\s*=\s*(\d+)\s*;", texto, re.M)
        if not m:
            raise CheckError(f"{fonte.name} nao declara {campo}")
        partes.append(m.group(1))
    return ".".join(partes)


# ----------------------------------------------------------------- parsing --

_DECL = re.compile(
    r"^\s{2,4}(T\w+)\s*=\s*class\s*\(\s*(T\w+)\s*\)", re.M)
_DECL_SEM_PAI = re.compile(r"^\s{2,4}(T\w+)\s*=\s*class\s*;?\s*$", re.M)
_PROP = re.compile(r"^\s*property\s+(\w+)", re.M | re.I)
_SECAO = re.compile(r"^\s*(published|public|protected|private|end)\b",
                    re.M | re.I)


def fontes(lcl: Path) -> list[Path]:
    """Os `.pp`/`.pas` da LCL, inclusive os do widgetset GTK2."""
    achados: list[Path] = []
    for sufixo in ("*.pp", "*.pas", "*.inc"):
        achados.extend(sorted(lcl.rglob(sufixo), key=lambda p: p.as_posix()))
    return achados


def indexar(lcl: Path) -> tuple[dict[str, str], dict[str, set[str]], str]:
    """Para cada classe: o ancestral e as propriedades `published` proprias.

    Devolve tambem o texto concatenado das fontes, que serve a conferencia dos
    identificadores.
    """
    pai: dict[str, str] = {}
    props: dict[str, set[str]] = {}
    pedacos: list[str] = []
    for f in fontes(lcl):
        texto = f.read_text(encoding="utf-8", errors="replace")
        pedacos.append(texto)
        for m in _DECL.finditer(texto):
            classe, ancestral = m.group(1), m.group(2)
            # Redeclaracao (classe com o mesmo nome em outro widgetset): a
            # primeira ganha, e as propriedades sao acumuladas nas duas.
            pai.setdefault(classe, ancestral)
            props.setdefault(classe, set()).update(
                _published_do_corpo(texto, m.end()))
        for m in _DECL_SEM_PAI.finditer(texto):
            pai.setdefault(m.group(1), "")
            props.setdefault(m.group(1), set())
    return pai, props, "\n".join(pedacos)


def _published_do_corpo(texto: str, inicio: int) -> set[str]:
    """As propriedades declaradas nas secoes `published` de uma classe.

    Anda do fim do cabecalho da classe ate o `end;` que a fecha, ligando e
    desligando a coleta a cada palavra de visibilidade. Nao e um parser de
    Pascal -- e o suficiente para a forma que a LCL usa, que e uma declaracao
    por linha.
    """
    coletando = False
    achadas: set[str] = set()
    for linha in texto[inicio:].splitlines():
        m = _SECAO.match(linha)
        if m:
            palavra = m.group(1).lower()
            if palavra == "end":
                break
            coletando = palavra == "published"
            continue
        if coletando:
            p = _PROP.match(linha)
            if p:
                achadas.add(p.group(1))
    return achadas


def herdadas(classe: str, pai: dict[str, str],
             props: dict[str, set[str]]) -> set[str]:
    """As `published` da classe mais as de toda a cadeia de ancestrais."""
    vistas: set[str] = set()
    atual, guarda = classe, 0
    while atual and atual in props and guarda < 64:
        vistas |= props[atual]
        atual = pai.get(atual, "")
        guarda += 1
    return vistas


# ------------------------------------------------------------ conferencias --

def raiz_da_prop(prop: str) -> str:
    """`Font.Charset` e a subpropriedade de `Font`; a LCL publica `Font`."""
    return prop.split(".", 1)[0]


def classe_real(chave: str) -> str:
    return CLASSE_DO_FORM if chave == dfm2lfm.FORM else chave


def conferir_aceita(pai, props) -> list[str]:
    faltando: list[str] = []
    for chave, propriedades in sorted(dfm2lfm.ACEITA.items()):
        classe = classe_real(chave)
        if classe not in props:
            faltando.append(f"{classe}: classe ausente das fontes da LCL")
            continue
        disponiveis = herdadas(classe, pai, props)
        for prop in sorted(propriedades):
            if (classe, prop) in EXCECOES_DESIGNINFO:
                continue
            if raiz_da_prop(prop) not in disponiveis:
                faltando.append(
                    f"{classe}.{prop}: em ACEITA e sem published "
                    f"correspondente na LCL")
    return faltando


def conferir_descarta(pai, props) -> list[str]:
    sobrando: list[str] = []
    for chave, propriedades in sorted(dfm2lfm.DESCARTA.items()):
        classe = classe_real(chave)
        if classe not in props:
            sobrando.append(f"{classe}: classe ausente das fontes da LCL")
            continue
        disponiveis = herdadas(classe, pai, props)
        for prop in sorted(propriedades):
            if raiz_da_prop(prop) in disponiveis:
                sobrando.append(
                    f"{classe}.{prop}: em DESCARTA e a LCL **tem** -- "
                    f"descartar propriedade existente perde dado do formulario")
    return sobrando


def conferir_identificadores(texto: str) -> list[str]:
    ausentes: list[str] = []
    nomes = sorted(dfm2lfm.IDENTIFICADORES | dfm2lfm.ELEMENTOS_DE_CONJUNTO)
    for nome in nomes:
        if nome in ("True", "False"):
            continue          # palavras do FPC, nao da LCL
        if not re.search(rf"\b{re.escape(nome)}\b", texto):
            ausentes.append(f"{nome}: nao ocorre nas fontes da LCL")
    return ausentes


def conferir(lcl: Path) -> tuple[list[str], dict[str, int]]:
    pai, props, texto = indexar(lcl)
    problemas = (conferir_aceita(pai, props)
                 + conferir_descarta(pai, props)
                 + conferir_identificadores(texto))
    contagem = {
        "classes na LCL": len(props),
        "classes em ACEITA": len(dfm2lfm.ACEITA),
        "propriedades em ACEITA": sum(len(v) for v in dfm2lfm.ACEITA.values()),
        "propriedades em DESCARTA": sum(
            len(v) for v in dfm2lfm.DESCARTA.values()),
        "identificadores": len(dfm2lfm.IDENTIFICADORES),
        "elementos de conjunto": len(dfm2lfm.ELEMENTOS_DE_CONJUNTO),
        "excecoes DesignInfo": len(EXCECOES_DESIGNINFO),
    }
    return problemas, contagem


# --------------------------------------------------------------------- cli --

def main(argv: list[str]) -> int:
    modo_check = "--check" in argv[1:]
    try:
        lcl = caminho_da_lcl(dfm2lfm.LCL_VERSAO)
        problemas, contagem = conferir(lcl)
    except CheckError as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    if problemas:
        print("ERRO: a tabela PROPRIEDADES do dfm2lfm.py nao bate com a "
              f"LCL {dfm2lfm.LCL_VERSAO} instalada:", file=sys.stderr)
        for p in problemas:
            print(f"  {p}", file=sys.stderr)
        return 2
    if modo_check:
        print(f"{contagem['propriedades em ACEITA']} propriedades de ACEITA e "
              f"{contagem['propriedades em DESCARTA']} de DESCARTA conferidas "
              f"contra a LCL {dfm2lfm.LCL_VERSAO} em {lcl}")
        return 0
    print(f"LCL {dfm2lfm.LCL_VERSAO} em {lcl}")
    for chave, valor in contagem.items():
        print(f"  {valor:5} {chave}")
    print("\nsem divergencia")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
