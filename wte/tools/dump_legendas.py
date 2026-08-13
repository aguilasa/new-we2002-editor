#!/usr/bin/env python3
"""As legendas enumeradas da ficha do jogador, lidas do proprio `.exe`.

Gera `wte/re/legendas.md`, `wte/re/legendas.tsv` e a unidade Pascal
`wte/src/wte_legendas.pas` -- insumo da
[WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md), grupo de edicao.

## O problema que ele resolve

Nove dos doze `flechasapa` do formulario `jugador` nao mostram numero: mostram
**palavra**. O despachante `jugador.flechasapaClick` (`0x00408088`) e o
`0x0040756c` (o que enche a ficha) buscam essa palavra numa tabela de
`AnsiString` em `0x00423798`, indexada por linha (o sufixo do controle, menos
um) e coluna (a posicao do `TUpDown`).

**Essa tabela e zero no disco.** Ela e um `AnsiString[12][8]` -- 12 linhas de 8
ponteiros, passo `0x20` --, e ponteiro de `AnsiString` nao vive no arquivo: o
inicializador da unidade constroi os 96 em tempo de execucao. Sem eles, portar
o handler produz rotulo vazio, e o port fica mostrando as legendas de projeto
do `.lfm` (`Gl`, `A`, `A1`, `Dire.`, `NO`) iguais para todo jogador -- que e
pior do que branco, porque parece dado.

## Por que ferramenta, e nao transcricao

As 96 cadeias estao no `.exe`; da para le-las com `strings` e digitar. Mas
**qual cadeia vai em qual slot** nao esta no texto -- esta na ordem das
chamadas ao construtor. Transcrever a mao acerta o conteudo e erra a posicao
sem que nada reclame: a ficha mostra "Meia" onde devia mostrar "Zagueiro", e
so quem conhece o jogo percebe.

Este script nao le a lista de cadeias: percorre o inicializador instrucao a
instrucao e emite o par (slot, cadeia) que **o binario monta**.

## O que ele decodifica

O inicializador (`0x00401da8`..`0x0040295e`) repete um trio:

    lea edx,[ebx+IMM]     ; endereco da cadeia literal
    lea eax,[esi+OFF]     ; endereco do slot de destino
    call 0x0042120c       ; AnsiString::AnsiString(const char*)

com `esi` e `ebx` carregados **uma unica vez**, logo antes: `esi` com a base
das tabelas, `ebx` com a base do blob de literais. Recarga de qualquer um dos
dois no meio invalidaria todo destino calculado a partir dali, entao o script
**aborta** se encontrar uma -- em vez de emitir 96 linhas plausiveis e erradas.

## As conferencias que abortam

1. **As duas bases.** `esi` tem de sair como `0x00423798` e `ebx` como
   `0x00424754`. Sao o que a decima setima passagem mediu; se o binario mudar,
   o resto deste arquivo fala de outra coisa.
2. **96 slots contiguos** na primeira tabela, sem buraco e sem repeticao --
   12 linhas de 8, passo `0x20`. Buraco significaria que o decodificador
   perdeu um trio.
3. **Cada literal e ASCII imprimivel terminado em NUL** dentro de uma secao
   mapeada. Cadeia que sai do fim da secao e sinal de base errada.

Uso:

    python3 wte/tools/dump_legendas.py            # regenera
    python3 wte/tools/dump_legendas.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import sys
from pathlib import Path

from dump_auxiliares import PE, DumpError, decode

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
OUT_RE = ROOT / "wte" / "re"
OUT_PAS = ROOT / "wte" / "src" / "wte_legendas.pas"

REL_EXE = "we-team-editor/we-team-editor.exe"
GERADOR = "wte/tools/dump_legendas.py"

TSV_NAME = "legendas.tsv"
MD_NAME = "legendas.md"

# O inicializador da unidade. O fim e o `ret` em 0x0040295e; o script confere
# que ele cai exatamente ali em vez de confiar na constante.
INI = 0x00401DA8
FIM = 0x0040295E

CTOR = 0x0042120C          # AnsiString::AnsiString(const char*)

BASE_TABELAS = 0x00423798  # esi
BASE_LITERAIS = 0x00424754  # ebx

# A tabela que a ficha indexa por (linha, coluna): 12 linhas de 8 ponteiros.
LINHAS = 12
COLUNAS = 8
PASSO = COLUNAS * 4        # 0x20

# A tabela propria da forma do cabelo, contigua a de cima. Ela existe porque
# `flechasapa3` tem faixa maior que COLUNAS e nao cabe numa linha.
BASE_CABELO = BASE_TABELAS + LINHAS * PASSO   # 0x00423918
CABELO = "flechasapa3"

# O arquivo de onde sai o `Max` de cada seta. E outra medicao, de outra fonte:
# a tabela acima vem do codigo, o `Max` vem do formulario. Que as duas batam e
# a conferencia que segura este arquivo.
DFM = "wte/re/dfm/jugador.dfm"

# A janela em que o trio tem de caber. Medida: o maior trio observado ocupa
# 17 bytes. 48 da folga sem deixar um `call` distante colar num load solto.
JANELA = 48


class Slot:
    __slots__ = ("destino", "literal", "texto")

    def __init__(self, destino: int, literal: int, texto: str) -> None:
        self.destino = destino
        self.literal = literal
        self.texto = texto


# ------------------------------------------------------------- decodificacao --

def _i8(b: bytes, o: int) -> int:
    v = b[o]
    return v - 256 if v >= 128 else v


def _i32(b: bytes, o: int) -> int:
    v = int.from_bytes(b[o:o + 4], "little")
    return v - (1 << 32) if v >= (1 << 31) else v


def _u32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o + 4], "little")


def _carrega(data: bytes, o: int, n: int) -> tuple[str, bool, int] | None:
    """(`'eax'`|`'edx'`, relativo?, valor) quando a instrucao em `o` e um load.

    Sao sete formas, e nenhuma outra e aceita. Quatro sao **relativas** a uma
    das duas bases -- `lea reg,[base+disp]` em disp8 ou disp32 -- e a elas se
    junta o `mov eax,esi` que o Borland emite no lugar de um `lea` de zero. As
    outras duas sao **absolutas**, `mov reg,imm32`: o inicializador tambem
    monta cadeias em globais soltas, longe das duas bases.
    """
    b = data[o:o + n]
    if len(b) >= 2 and b[0] == 0x8B and b[1] == 0xC6:      # mov eax,esi
        return ("eax", True, 0)
    if len(b) >= 3 and b[0] == 0x8D and b[1] == 0x46:      # lea eax,[esi+i8]
        return ("eax", True, _i8(b, 2))
    if len(b) >= 6 and b[0] == 0x8D and b[1] == 0x86:      # lea eax,[esi+i32]
        return ("eax", True, _i32(b, 2))
    if len(b) >= 3 and b[0] == 0x8D and b[1] == 0x53:      # lea edx,[ebx+i8]
        return ("edx", True, _i8(b, 2))
    if len(b) >= 6 and b[0] == 0x8D and b[1] == 0x93:      # lea edx,[ebx+i32]
        return ("edx", True, _i32(b, 2))
    if len(b) >= 5 and b[0] == 0xB8:                       # mov eax,imm32
        return ("eax", False, _u32(b, 1))
    if len(b) >= 5 and b[0] == 0xBA:                       # mov edx,imm32
        return ("edx", False, _u32(b, 1))
    return None


def _chamada(data: bytes, o: int, tam: int) -> int | None:
    """O offset de arquivo alvo, quando a instrucao em `o` e `call rel32`.

    O `decode` importado classifica a instrucao mas nao devolve o alvo de um
    `call`; aqui o alvo importa, e a conta e a mesma do processador.
    """
    if tam != 5 or data[o] != 0xE8:
        return None
    return o + 5 + _i32(data, o + 1)


def _base(data: bytes, o: int) -> tuple[str, int] | None:
    """(`'esi'`|`'ebx'`, imediato) quando a instrucao em `o` carrega uma base."""
    if data[o] == 0xBE:                                    # mov esi,imm32
        return ("esi", _u32(data, o + 1))
    if data[o] == 0xBB:                                    # mov ebx,imm32
        return ("ebx", _u32(data, o + 1))
    return None


def _cadeia(pe: PE, va: int) -> str:
    o = pe.off(va)
    if o is None:
        raise DumpError(
            f"{REL_EXE}: literal em {va:#010x} fora de secao mapeada -- a base "
            f"de literais ({BASE_LITERAIS:#010x}) nao pode estar certa")
    fim = pe.data.find(b"\0", o, o + 256)
    if fim < 0:
        raise DumpError(
            f"{REL_EXE}: literal em {va:#010x} sem NUL em 256 bytes")
    bruto = pe.data[o:fim]
    for c in bruto:
        if c < 0x20 or c > 0x7E:
            raise DumpError(
                f"{REL_EXE}: literal em {va:#010x} tem byte {c:#04x}, que nao "
                f"e ASCII imprimivel: {bruto!r}")
    return bruto.decode("ascii")


def varre(pe: PE) -> list[Slot]:
    """Percorre o inicializador e devolve os slots na ordem em que ele monta."""
    ini = pe.off(INI)
    fim = pe.off(FIM)
    if ini is None or fim is None:
        raise DumpError(f"{REL_EXE}: {INI:#010x}..{FIM:#010x} fora de secao")

    esi: int | None = None
    ebx: int | None = None
    pend: dict[str, tuple[int, int]] = {}   # reg -> (valor, offset da carga)
    slots: list[Slot] = []

    o = ini
    while o <= fim:
        tam, classe, alvo = decode(pe.data, o, fim + 1)

        base = _base(pe.data, o)
        if base is not None:
            reg, valor = base
            atual = esi if reg == "esi" else ebx
            if atual is not None and atual != valor:
                raise DumpError(
                    f"{REL_EXE}: {reg} recarregado com {valor:#010x} no byte "
                    f"{o:#x} do arquivo, depois de {atual:#010x}. Todo destino "
                    f"calculado a partir dai estaria errado.")
            if reg == "esi":
                esi = valor
            else:
                ebx = valor

        carga = _carrega(pe.data, o, tam)
        if carga is not None:
            reg, relativo, valor = carga
            pend[reg] = (relativo, valor, o)

        if classe == "call" and _chamada(pe.data, o, tam) == pe.off(CTOR):
            if esi is None or ebx is None:
                raise DumpError(
                    f"{REL_EXE}: construtor chamado antes de as duas bases "
                    f"serem carregadas")
            faltando = [r for r in ("eax", "edx") if r not in pend]
            if faltando:
                raise DumpError(
                    f"{REL_EXE}: construtor sem carga de {', '.join(faltando)} "
                    f"antes dele")
            for reg in ("eax", "edx"):
                if o - pend[reg][2] > JANELA:
                    raise DumpError(
                        f"{REL_EXE}: a carga de {reg} esta a "
                        f"{o - pend[reg][2]} bytes do construtor, mais que a "
                        f"janela de {JANELA}")
            destino = (esi + pend["eax"][1]) if pend["eax"][0] else pend["eax"][1]
            literal = (ebx + pend["edx"][1]) if pend["edx"][0] else pend["edx"][1]
            slots.append(Slot(destino, literal, _cadeia(pe, literal)))
            pend.clear()

        if o == fim:
            if classe != "ret":
                raise DumpError(
                    f"{REL_EXE}: {FIM:#010x} devia ser o `ret` do "
                    f"inicializador, e e `{classe or 'outra instrucao'}`")
            break
        o += tam
    else:
        raise DumpError(f"{REL_EXE}: a varredura passou de {FIM:#010x}")

    if esi != BASE_TABELAS or ebx != BASE_LITERAIS:
        raise DumpError(
            f"{REL_EXE}: bases medidas esi={esi:#010x} ebx={ebx:#010x}, "
            f"esperadas {BASE_TABELAS:#010x} e {BASE_LITERAIS:#010x}")
    return slots


def maximos() -> dict[str, int]:
    """O `Max` declarado de cada `flechasapa`, lido do formulario."""
    texto = (ROOT / DFM).read_text(encoding="latin1").splitlines()
    fora: dict[str, int] = {}
    atual: str | None = None
    for linha in texto:
        corte = linha.strip()
        if corte.startswith("object "):
            nome = corte[len("object "):].split(":")[0].strip()
            atual = nome if nome.startswith("flechasapa") else None
        elif atual and corte.startswith("Max = "):
            fora[atual] = int(corte[len("Max = "):])
            atual = None
    esperado = {f"flechasapa{i}" for i in range(1, LINHAS + 1)}
    if set(fora) != esperado:
        raise DumpError(
            f"{DFM}: os `flechasapa` com `Max` sao {sorted(fora)}, e a tabela "
            f"tem {LINHAS} linhas")
    return fora


def confere(slots: list[Slot]) -> tuple[list[Slot], list[Slot]]:
    """As duas tabelas: a da ficha em (linha, coluna), e a do cabelo em fila."""
    por_destino: dict[int, Slot] = {}
    for s in slots:
        if s.destino in por_destino:
            raise DumpError(
                f"{REL_EXE}: slot {s.destino:#010x} montado duas vezes "
                f"({por_destino[s.destino].texto!r} e {s.texto!r})")
        por_destino[s.destino] = s

    ficha: list[Slot] = []
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            va = BASE_TABELAS + linha * PASSO + coluna * 4
            if va not in por_destino:
                raise DumpError(
                    f"{REL_EXE}: a tabela da ficha tem buraco na linha "
                    f"{linha} coluna {coluna} ({va:#010x}) -- o decodificador "
                    f"perdeu um trio")
            ficha.append(por_destino[va])

    # A conferencia que segura o arquivo, e a razao de ela valer: as duas
    # medidas nao se falam. O `Max` sai do formulario, a contagem de celulas
    # com texto sai do codigo, e a coincidencia das doze e o que prova que a
    # linha `n` e mesmo o `flechasapa n+1` -- nao ha nada no binario dizendo
    # isso, so a ordem em que o inicializador constroi.
    maxs = maximos()
    cabelo: list[Slot] = []
    for linha in range(LINHAS):
        nome = f"flechasapa{linha + 1}"
        mx = maxs[nome]
        cheias = sum(1 for c in range(COLUNAS)
                     if ficha[linha * COLUNAS + c].texto.strip())
        if mx >= COLUNAS:
            if cheias:
                raise DumpError(
                    f"{REL_EXE}: {nome} tem `Max` {mx}, maior que as "
                    f"{COLUNAS} colunas, e mesmo assim a linha {linha} tem "
                    f"{cheias} celula(s) com texto")
        elif cheias != mx + 1:
            raise DumpError(
                f"{REL_EXE}: {nome} tem `Max` {mx} ({mx + 1} posicoes) e a "
                f"linha {linha} da tabela tem {cheias} celula(s) com texto")

    # A tabela do cabelo: uma fila de `Max + 1`, logo depois da primeira.
    n = maxs[CABELO] + 1
    for i in range(n):
        va = BASE_CABELO + i * 4
        if va not in por_destino:
            raise DumpError(
                f"{REL_EXE}: a tabela de {CABELO} tem buraco na posicao {i} "
                f"({va:#010x})")
        cabelo.append(por_destino[va])
    return ficha, cabelo


# ------------------------------------------------------------------- saidas --

def tsv(ficha: list[Slot], cabelo: list[Slot], slots: list[Slot]) -> str:
    linhas = ["tabela\tlinha\tcoluna\tdestino\tliteral\ttexto"]
    for i, s in enumerate(ficha):
        linhas.append(f"ficha\t{i // COLUNAS}\t{i % COLUNAS}\t"
                      f"0x{s.destino:08x}\t0x{s.literal:08x}\t{s.texto}")
    for i, s in enumerate(cabelo):
        linhas.append(f"cabelo\t\t{i}\t0x{s.destino:08x}\t"
                      f"0x{s.literal:08x}\t{s.texto}")
    conhecidos = {s.destino for s in ficha} | {s.destino for s in cabelo}
    for s in slots:
        if s.destino in conhecidos:
            continue
        linhas.append(f"resto\t\t\t0x{s.destino:08x}\t"
                      f"0x{s.literal:08x}\t{s.texto}")
    return "\n".join(linhas) + "\n"


def _pascal(texto: str) -> str:
    return "'" + texto.replace("'", "''") + "'"


def pascal(ficha: list[Slot], cabelo: list[Slot]) -> str:
    corpo = [
        "{ wte_legendas -- as legendas enumeradas da ficha do jogador.",
        "",
        "  GERADO por wte/tools/dump_legendas.py a partir de",
        "  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai",
        "  no gerador, e depois se regenera.",
        "",
        f"  LEGENDAS e o que o inicializador do original monta em "
        f"{BASE_TABELAS:#010x} --",
        f"  {LINHAS} linhas de {COLUNAS}, indexada por (sufixo do "
        f"`flechasapa` menos um,",
        "  posicao do `TUpDown`). Linha mais curta que a faixa do controle",
        "  preenche o resto com um espaco, como o original.",
        "",
        f"  CABELO e a tabela propria de {CABELO}, em {BASE_CABELO:#010x}: a",
        "  forma do cabelo tem faixa maior que uma linha e nao cabe na primeira",
        "  tabela. }",
        "unit wte_legendas;",
        "",
        "{$mode objfpc}{$H+}",
        "",
        "interface",
        "",
        "const",
        f"  LEGENDA_LINHAS = {LINHAS};",
        f"  LEGENDA_COLUNAS = {COLUNAS};",
        f"  LEGENDA_CABELO = {len(cabelo)};",
        "",
        "  LEGENDAS: array[0..LEGENDA_LINHAS - 1, 0..LEGENDA_COLUNAS - 1] "
        "of string = (",
    ]
    for linha in range(LINHAS):
        itens = [_pascal(ficha[linha * COLUNAS + c].texto)
                 for c in range(COLUNAS)]
        virgula = "," if linha < LINHAS - 1 else ""
        corpo.append(f"    ({', '.join(itens)}){virgula}")
    corpo += [
        "  );",
        "",
        "  CABELO: array[0..LEGENDA_CABELO - 1] of string = (",
    ]
    for i in range(0, len(cabelo), COLUNAS):
        itens = [_pascal(s.texto) for s in cabelo[i:i + COLUNAS]]
        virgula = "," if i + COLUNAS < len(cabelo) else ""
        corpo.append(f"    {', '.join(itens)}{virgula}")
    corpo += [
        "  );",
        "",
        "{ A legenda de um `flechasapa`, ou cadeia vazia quando o par esta fora",
        "  da tabela. Fora da tabela nao e erro: altura e idade mostram numero,",
        "  e a forma do cabelo tem a LegendaDoCabelo. }",
        "function Legenda(indice, posicao: Integer): string;",
        "",
        "{ O nome da forma do cabelo, ou cadeia vazia fora da faixa. }",
        "function LegendaDoCabelo(posicao: Integer): string;",
        "",
        "implementation",
        "",
        "function Legenda(indice, posicao: Integer): string;",
        "begin",
        "  if (indice < 1) or (indice > LEGENDA_LINHAS) or (posicao < 0)",
        "     or (posicao >= LEGENDA_COLUNAS) then",
        "    Result := ''",
        "  else",
        "    Result := LEGENDAS[indice - 1, posicao];",
        "end;",
        "",
        "function LegendaDoCabelo(posicao: Integer): string;",
        "begin",
        "  if (posicao < 0) or (posicao >= LEGENDA_CABELO) then",
        "    Result := ''",
        "  else",
        "    Result := CABELO[posicao];",
        "end;",
        "",
        "end.",
    ]
    return "\n".join(corpo) + "\n"


def md(ficha: list[Slot], cabelo: list[Slot], slots: list[Slot],
       maxs: dict[str, int]) -> str:
    usadas = sum(1 for s in ficha if s.texto.strip())
    linhas = [
        "# `re/legendas.md` — as legendas enumeradas da ficha do jogador",
        "",
        "Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md).",
        "Gerado por [`../tools/dump_legendas.py`](../tools/dump_legendas.py) a",
        f"partir de `{REL_EXE}`. **Não editar à mão.** As tabelas estão em",
        f"[`{TSV_NAME}`]({TSV_NAME}); este arquivo é a leitura delas, e a unidade",
        "Pascal correspondente é",
        "[`../src/wte_legendas.pas`](../src/wte_legendas.pas).",
        "",
        "## Por que elas não se leem do arquivo",
        "",
        f"A primeira vive em `{BASE_TABELAS:#010x}` e é um",
        f"`AnsiString[{LINHAS}][{COLUNAS}]` — {LINHAS} linhas de {COLUNAS}",
        f"ponteiros, passo `{PASSO:#04x}`. **No disco ela é zero:** ponteiro de",
        "`AnsiString` não existe em arquivo. Quem a monta é o inicializador da",
        f"unidade, `{INI:#010x}`..`{FIM:#010x}`, com {len(slots)} chamadas ao",
        "construtor de `AnsiString` a partir de literal.",
        "",
        "Por isso este dumper decodifica em vez de transcrever: as cadeias estão",
        "no `.exe` e sairiam num `strings`, mas **qual cadeia vai em qual slot**",
        "só está na ordem das chamadas.",
        "",
        "## Quem lê a tabela",
        "",
        "Os dois lados da ficha do jogador:",
        "",
        "- `jugador.flechasapaClick` (`0x00408088`) — ao mexer numa seta, indexa",
        "  `[sufixo − 1][Position]` e escreve no `valorapa` correspondente;",
        "- `0x0040756c` (o que enche a ficha) — na abertura, para os mesmos doze.",
        "",
        "## A tabela da ficha",
        "",
        f"{usadas} das {LINHAS * COLUNAS} posições têm texto. O resto é um",
        "espaço — não cadeia vazia, e é o que o original constrói para as linhas",
        "curtas.",
        "",
        "| Linha | `flechasapa` | `Max` | "
        + " | ".join(str(c) for c in range(COLUNAS)) + " |",
        "|--:|--:|--:|" + "---|" * COLUNAS,
    ]
    for linha in range(LINHAS):
        celulas = []
        for c in range(COLUNAS):
            t = ficha[linha * COLUNAS + c].texto
            celulas.append(f"`{t}`" if t.strip() else "—")
        mx = maxs[f"flechasapa{linha + 1}"]
        linhas.append(f"| {linha} | `flechasapa{linha + 1}` | {mx} | "
                      + " | ".join(celulas) + " |")
    linhas += [
        "",
        "**A coluna `Max` é a conferência, não enfeite.** Ela vem do formulário",
        f"(`{DFM}`) e a contagem de células com texto vem do código; o gerador",
        "**aborta** se as duas discordarem. Nenhuma linha da tabela diz a que",
        "controle pertence — só a ordem em que o inicializador constrói —, e é o",
        "casamento das doze faixas que sustenta a atribuição.",
        "",
        "Nas três linhas vazias o `Max` é maior que as "
        f"{COLUNAS} colunas: `flechasapa7`",
        "(altura) e `flechasapa9` (idade) mostram número, e `flechasapa3` (forma",
        "do cabelo) tem tabela própria.",
        "",
        f"## A tabela de {CABELO}",
        "",
        f"Contígua à primeira, em `{BASE_CABELO:#010x}`: {len(cabelo)} cadeias em",
        f"fila, `Max` {maxs[CABELO]} mais um.",
        "",
        "```text",
        "  " + "  ".join(s.texto for s in cabelo),
        "```",
        "",
        "As mesmas 32 da contagem de `image/pelo/pelo_<n>.bmp` — ver a §5 de",
        "[`assets.md`](assets.md).",
        "",
        "## O que mais o inicializador monta",
        "",
        f"Das {len(slots)} cadeias, {LINHAS * COLUNAS} são a tabela da ficha e",
        f"{len(cabelo)} são a do cabelo. As demais estão no TSV com a tabela",
        "`resto` — entram aqui porque saem da mesma varredura, não porque a",
        "ficha as use.",
        "",
    ]
    return "\n".join(linhas)


# -------------------------------------------------------------------- saida --

def gera() -> dict[Path, str]:
    if not EXE.exists():
        raise DumpError(
            f"{REL_EXE} nao esta no disco. A pasta e do usuario e nao entra no "
            f"repositorio -- ver o CLAUDE.md.")
    pe = PE(EXE.read_bytes(), REL_EXE)
    slots = varre(pe)
    ficha, cabelo = confere(slots)
    return {
        OUT_RE / TSV_NAME: tsv(ficha, cabelo, slots),
        OUT_RE / MD_NAME: md(ficha, cabelo, slots, maximos()),
        OUT_PAS: pascal(ficha, cabelo),
    }


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de dump_legendas.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    return 0


def do_write(files: dict[Path, str]) -> int:
    for caminho, conteudo in sorted(files.items()):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {caminho.relative_to(ROOT)}: "
              f"{conteudo.count(chr(10))} linhas")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GERADOR} [--check]", file=sys.stderr)
            return 2
    try:
        files = gera()
    except DumpError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
