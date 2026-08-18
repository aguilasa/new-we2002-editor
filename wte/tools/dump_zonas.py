#!/usr/bin/env python3
"""As zonas do campinho tatico -- o retangulo em que cada bola pode ser solta.

Gera `wte/re/zonas.md`, `wte/re/zonas.tsv` e a unidade Pascal
`wte/src/wte_zonas.pas` -- insumo da
[WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md), grupo de edicao.

## O problema que ele resolve

Arrastar um jogador no campinho do formulario `estrategia` nao e livre: o
`bolaMouseDown` desenha um retangulo (`rectangulo`) que delimita onde aquela
bola pode ir, e o retangulo sai de uma tabela em `0x00433e5c` -- 11 registros
de 16 bytes, `(x1, y1, x2, y2)` em coordenadas do `campo`.

**Essa tabela nao existe no arquivo.** Ela mora em `.bss`, e quem a monta e o
`estrategia.FormCreate` (`0x004090fc`), escrevendo 44 imediatos um a um. Sem
ela, portar o `bolaMouseDown` desenha um retangulo de tamanho zero na origem
do campo -- e isso nao parece bug, parece um retangulo que "nao apareceu".

## Por que ferramenta, e nao transcricao

Sao 44 numeros em 11 grupos, escritos em ordem embaralhada: o compilador
intercala `lea` de ponteiro com `mov` de deslocamento, e o primeiro campo de
cada registro sai por um registrador diferente do dos outros tres. Transcrever
a olho troca um `x2` por um `y1` sem que nada reclame -- e retangulo errado so
aparece para quem conhece o jogo.

## O que ele decodifica

Dentro do corpo do `FormCreate`, apos `mov ebx,0x00433e5c`:

    mov DWORD PTR [ebx+DISP],IMM      ' campo escrito pelo deslocamento
    lea REG,[ebx+DISP]                ' ponteiro para o proximo registro
    mov DWORD PTR [REG],IMM           ' o primeiro campo, pelo ponteiro

O script segue os tres registradores auxiliares (`eax`, `ecx`, `edx`) e resolve
cada escrita para um deslocamento absoluto a partir de `ebx`.

## As conferencias que abortam

1. **A base.** `ebx` tem de sair como `0x00433e5c`.
2. **Registros completos e contiguos** -- todos os quatro campos de cada um dos
   11, sem buraco e sem escrita repetida. Buraco significaria que o
   decodificador perdeu uma forma de `mov`.
3. **Cada retangulo cabe no `campo`**, cujo tamanho vem do `.lfm` -- outra
   fonte. `x2 > x1`, `y2 > y1`, e nenhum canto fora de `0..Width/Height`.
4. **Uma zona por bola.** O formulario tem `bola0`..`bola10`; a contagem de
   registros tem de bater com a contagem de `TShape` chamados `bolaN`.

Uso:

    python3 wte/tools/dump_zonas.py            # regenera
    python3 wte/tools/dump_zonas.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from dump_auxiliares import PE, DumpError, decode

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
OUT_RE = ROOT / "wte" / "re"
OUT_PAS = ROOT / "wte" / "src" / "wte_zonas.pas"

REL_EXE = "we-team-editor/we-team-editor.exe"
GERADOR = "wte/tools/dump_zonas.py"

TSV_NAME = "zonas.tsv"
MD_NAME = "zonas.md"

# `estrategia.FormCreate`, do published_methods.tsv. O fim e o inicio do
# handler seguinte na mesma unidade (`rectanguloDragOver`).
INI = 0x004090FC
FIM = 0x00409644

BASE = 0x00433E5C          # ebx
CAMPOS = 4                 # x1, y1, x2, y2
PASSO = CAMPOS * 4         # 16 bytes por registro

LFM = "wte/forms/ep2002_estrategia.lfm"

# Os tres registradores que o compilador usa como ponteiro auxiliar, e o byte
# de ModRM de `mov DWORD PTR [reg],imm32` para cada um.
PONTEIROS = {0x00: "eax", 0x01: "ecx", 0x02: "edx"}
LEA_DISP8 = {0x43: "eax", 0x4B: "ecx", 0x53: "edx"}
LEA_DISP32 = {0x83: "eax", 0x8B: "ecx", 0x93: "edx"}


def _i8(b: int) -> int:
    return b - 256 if b >= 128 else b


def _i32(data: bytes, o: int) -> int:
    v = int.from_bytes(data[o:o + 4], "little")
    return v - (1 << 32) if v >= (1 << 31) else v


def _u32(data: bytes, o: int) -> int:
    return int.from_bytes(data[o:o + 4], "little")


def varre(pe: PE) -> dict[int, int]:
    """Deslocamento a partir de `BASE` -> valor escrito, na ordem do corpo."""
    ini, fim = pe.off(INI), pe.off(FIM)
    if ini is None or fim is None:
        raise DumpError(f"{REL_EXE}: {INI:#010x}..{FIM:#010x} fora de secao")

    ebx: int | None = None
    aponta: dict[str, int] = {}
    escrito: dict[int, int] = {}
    d = pe.data
    o = ini
    while o < fim:
        tam, _classe, _alvo = decode(d, o, fim)

        if d[o] == 0xBB:                                   # mov ebx,imm32
            valor = _u32(d, o + 1)
            if ebx is not None and ebx != valor:
                raise DumpError(
                    f"{REL_EXE}: ebx recarregado com {valor:#010x} depois de "
                    f"{ebx:#010x} -- todo deslocamento daqui em diante estaria "
                    f"errado")
            ebx = valor

        elif d[o] == 0x8D and ebx is not None:             # lea REG,[ebx+disp]
            if d[o + 1] in LEA_DISP8:
                aponta[LEA_DISP8[d[o + 1]]] = _i8(d[o + 2])
            elif d[o + 1] in LEA_DISP32:
                aponta[LEA_DISP32[d[o + 1]]] = _i32(d, o + 2)

        elif d[o] == 0xC7 and ebx is not None:             # mov [...],imm32
            m = d[o + 1]
            if m == 0x03:                                  # [ebx]
                _guarda(escrito, 0, _u32(d, o + 2))
            elif m == 0x43:                                # [ebx+disp8]
                _guarda(escrito, _i8(d[o + 2]), _u32(d, o + 3))
            elif m == 0x83:                                # [ebx+disp32]
                _guarda(escrito, _i32(d, o + 2), _u32(d, o + 6))
            elif m in PONTEIROS:                           # [reg]
                reg = PONTEIROS[m]
                if reg in aponta:
                    _guarda(escrito, aponta[reg], _u32(d, o + 2))
        o += tam

    if ebx != BASE:
        raise DumpError(
            f"{REL_EXE}: ebx medido {ebx if ebx is None else hex(ebx)}, "
            f"esperado {BASE:#010x}")
    return escrito


def _guarda(escrito: dict[int, int], disp: int, valor: int) -> None:
    if disp < 0:
        return
    if disp in escrito and escrito[disp] != valor:
        raise DumpError(
            f"{REL_EXE}: o deslocamento {disp:#x} da tabela de zonas recebeu "
            f"{escrito[disp]} e depois {valor} -- o decodificador esta "
            f"resolvendo um ponteiro para o lugar errado")
    escrito[disp] = valor


def bolas() -> int:
    """Quantas `bolaN` o formulario declara -- a segunda fonte da contagem."""
    texto = (ROOT / LFM).read_text(encoding="utf-8", errors="replace")
    return len(set(re.findall(r"^\s*object (bola\d+): TShape", texto,
                              re.MULTILINE)))


def campo() -> tuple[int, int]:
    """Largura e altura do `campo`, do `.lfm` -- a fonte da conferencia 3."""
    texto = (ROOT / LFM).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^  object campo: TImage$(.*?)^  object ", texto,
                  re.MULTILINE | re.DOTALL)
    if not m:
        raise DumpError(f"{LFM}: nao achei o objeto `campo`")
    largura = re.search(r"^\s*Width = (\d+)", m.group(1), re.MULTILINE)
    altura = re.search(r"^\s*Height = (\d+)", m.group(1), re.MULTILINE)
    if not largura or not altura:
        raise DumpError(f"{LFM}: `campo` sem Width/Height")
    return int(largura.group(1)), int(altura.group(1))


def confere(escrito: dict[int, int]) -> list[tuple[int, int, int, int]]:
    if not escrito:
        raise DumpError(f"{REL_EXE}: nenhuma escrita na tabela de zonas")
    n = max(escrito) // PASSO + 1
    quantas = bolas()
    if n != quantas:
        raise DumpError(
            f"{REL_EXE}: {n} zona(s) decodificada(s) contra {quantas} `bolaN` "
            f"no {LFM} -- as duas contagens tem de bater")
    largura, altura = campo()
    zonas = []
    for i in range(n):
        campos = []
        for c in range(CAMPOS):
            disp = i * PASSO + c * 4
            if disp not in escrito:
                raise DumpError(
                    f"{REL_EXE}: a zona {i} nao tem o campo {c} "
                    f"(deslocamento {disp:#x}) -- o decodificador perdeu uma "
                    f"forma de `mov`")
            campos.append(escrito[disp])
        x1, y1, x2, y2 = campos
        if not (0 <= x1 < x2 <= largura and 0 <= y1 < y2 <= altura):
            raise DumpError(
                f"{REL_EXE}: a zona {i} e ({x1},{y1})-({x2},{y2}) e nao cabe "
                f"no campo de {largura}x{altura} do {LFM}")
        zonas.append((x1, y1, x2, y2))
    return zonas


# ------------------------------------------------------------------- saidas --

def tsv(zonas) -> str:
    linhas = ["zona\tendereco\tx1\ty1\tx2\ty2\tlargura\taltura"]
    for i, (x1, y1, x2, y2) in enumerate(zonas):
        linhas.append(f"{i}\t0x{BASE + i * PASSO:08x}\t{x1}\t{y1}\t{x2}\t{y2}"
                      f"\t{x2 - x1 + 1}\t{y2 - y1 + 1}")
    return "\n".join(linhas) + "\n"


def pascal(zonas) -> str:
    corpo = [
        "{ wte_zonas -- os retangulos em que cada bola do campinho pode ser",
        "  solta.",
        "",
        "  GERADO por wte/tools/dump_zonas.py a partir de",
        "  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai",
        "  no gerador, e depois se regenera.",
        "",
        f"  E a tabela que o `estrategia.FormCreate` monta em {BASE:#010x} e que",
        "  o `bolaMouseDown` le para dimensionar o `rectangulo`. As coordenadas",
        "  sao relativas ao `campo`, e a largura/altura do retangulo desenhado e",
        "  `x2 - x1 + 1` por `y2 - y1 + 1` -- o `+ 1` e do original.",
        "",
        "  O indice NAO e o numero da bola: e a zona que a formacao escolhida",
        "  atribuiu aquela bola. O vetor bola->zona e outro, e quem o preenche e",
        "  o `estrategia.lista_formacionesClick`. }",
        "unit wte_zonas;",
        "",
        "{$mode objfpc}{$H+}",
        "",
        "interface",
        "",
        "type",
        "  TZona = record",
        "    x1, y1, x2, y2: Integer;",
        "  end;",
        "",
        "const",
        f"  ZONAS_TOTAL = {len(zonas)};",
        "",
        "  ZONAS: array[0..ZONAS_TOTAL - 1] of TZona = (",
    ]
    for i, (x1, y1, x2, y2) in enumerate(zonas):
        virgula = "," if i < len(zonas) - 1 else ""
        corpo.append(f"    (x1: {x1}; y1: {y1}; x2: {x2}; y2: {y2}){virgula}")
    corpo += [
        "  );",
        "",
        "implementation",
        "",
        "end.",
    ]
    return "\n".join(corpo) + "\n"


def md(zonas) -> str:
    largura, altura = campo()
    distintas = len(set(zonas))
    linhas = [
        "# `re/zonas.md` — onde cada bola do campinho pode ser solta",
        "",
        "Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md).",
        "Gerado por [`../tools/dump_zonas.py`](../tools/dump_zonas.py) a partir",
        f"de `{REL_EXE}`. **Não editar à mão.** A tabela está em",
        f"[`{TSV_NAME}`]({TSV_NAME}); a unidade Pascal é",
        "[`../src/wte_zonas.pas`](../src/wte_zonas.pas).",
        "",
        "## O que é",
        "",
        "Arrastar um jogador no campinho do formulário `estrategia` **não é**",
        "livre. O `bolaMouseDown` desenha o `rectangulo` em volta da área",
        "permitida daquela bola, e o `rectanguloDragOver` prende o movimento a",
        "uma grade dentro dela.",
        "",
        f"A tabela vive em `{BASE:#010x}`: {len(zonas)} registros de {PASSO} bytes,",
        "`(x1, y1, x2, y2)` em coordenadas do `campo`. **No arquivo ela não",
        "existe** — é `.bss`, montada em tempo de execução pelo",
        f"`estrategia.FormCreate` (`{INI:#010x}`), que escreve os",
        f"{len(zonas) * CAMPOS} imediatos um a um.",
        "",
        "> **A spec do `estrategia.FormCreate` não dizia isso.** Escrita na",
        "> WTE-TASK-25, ela descreve as cores da zebra e chama estes quatro",
        "> blocos de \"quatro laços curtos de 11 iterações\" — que é o que se vê",
        "> quando se procura pintura. O produto principal da rotina é esta",
        "> tabela, e a WTE-TASK-26 corrigiu a spec ao lê-la de novo.",
        "",
        "## A tabela",
        "",
        f"O `campo` tem {largura}×{altura} (do `.lfm`), e o gerador **aborta** se",
        "algum retângulo sair dele — as duas medidas vêm de fontes diferentes,",
        "uma do código e outra do formulário.",
        "",
        "| Zona | x1 | y1 | x2 | y2 | largura | altura |",
        "|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for i, (x1, y1, x2, y2) in enumerate(zonas):
        linhas.append(f"| {i} | {x1} | {y1} | {x2} | {y2} | {x2 - x1 + 1} | "
                      f"{y2 - y1 + 1} |")
    linhas += [
        "",
        f"São {len(zonas)} registros para {distintas} retângulos distintos: há",
        "repetição, e ela é esperada — o índice não é o número da bola, é a",
        "**zona** que a formação escolhida atribuiu àquela bola. Quem preenche o",
        "vetor bola→zona é o `estrategia.lista_formacionesClick`.",
        "",
        "A largura desenhada é `x2 - x1 + 1`, não `x2 - x1`. O `+ 1` é do",
        "original e está reproduzido.",
        "",
    ]
    return "\n".join(linhas)


def gera() -> dict[Path, str]:
    if not EXE.exists():
        raise DumpError(
            f"{REL_EXE} nao esta no disco. A pasta e do usuario e nao entra no "
            f"repositorio -- ver o CLAUDE.md.")
    pe = PE(EXE.read_bytes(), REL_EXE)
    zonas = confere(varre(pe))
    return {
        OUT_RE / TSV_NAME: tsv(zonas),
        OUT_RE / MD_NAME: md(zonas),
        OUT_PAS: pascal(zonas),
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
        print("saida de dump_zonas.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    return 0


def do_write(files: dict[Path, str]) -> int:
    for caminho, conteudo in sorted(files.items()):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {caminho.relative_to(ROOT)}: {conteudo.count(chr(10))} linhas")
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
