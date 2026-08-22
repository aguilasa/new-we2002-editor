#!/usr/bin/env python3
"""Onde na imagem mora o bloco de cor de cada time.

Gera `wte/src/wte_blococor.pas` -- insumo da
[CORR-WTE-081](../../docs/tasks/CORR-WTE-081.md), segunda das tres gravacoes
orfas (`ficha_color.BitBtn3Click`).

    python3 wte/tools/dump_blococor.py           # regera
    python3 wte/tools/dump_blococor.py --check   # o que `make -C wte check` roda

## Por que ele existe

O `0x004050D0` (carga) e o `0x004051A4` (gravacao) sao espelhos: os dois
percorrem SETE regioes por time e usam as MESMAS sete globais de offset. Quem
enche essas globais e o `0x00404E70`, e ele nao le tabela de offset nenhuma da
`.data` -- ele **calcula** seis das sete e le a setima de uma tabela de 95
bytes.

Essa tabela e a unica coisa aqui que nao e formula, e ela e o motivo do script:
os 95 bytes de `0x00423247` NAO sao identidade -- 86 valores distintos para 95
times, ou seja, times COMPARTILHAM paleta de bandeira. Escrever isso a mao
seria copiar 95 numeros sem quem os confira.

## O que ele emite, e o que ele deliberadamente NAO emite

Emite **dado**: a tabela de 95 bytes, as cinco bases da forma de bandeira
(`0x00423634`) e as constantes das formulas. A LOGICA -- as sete regioes, os
tamanhos, o `30` contra `32` -- fica no `wte_cor.pas`, escrito a mao, junto de
quem a usa. E a mesma divisao do `wte_uniformes` contra a `wte_render2d`.

## A aritmetica logico -> absoluto

O `0x00404E70` faz, para cinco das sete regioes:

    absoluto = logico + 304 * (logico div 2048) + base

que e a geometria MODE2/2352 do resto do formato -- 304 = 280 de EDC/ECC mais
os 24 de cabecalho do setor seguinte, 2048 de dados por setor. A diferenca
contra o `EnderecoDeDados` do `we2002_estado` e que aqui a base NAO cai numa
fronteira de setor: `0x0025AEF8` nao e multiplo de 2352 mais 24. Por isso a
formula fica escrita como o original a escreve, com a base crua, em vez de
espremida no helper.

## As quatro conferencias que abortam

Elas existem porque as seis formulas calculadas nao tem tabela que as prove --
so o resultado. Cada uma bate contra um `OFS_*` que o `we2002_core` ja
versionava, medido por caminho independente:

1. time 0, cores da bandeira  = `OFS_FLAG_COLOURS`
2. time 36, idem              = `OFS_FLAG_COLOURS_SENEGAL` -- o `cmp eax,0x24`
   do original, que e o unico time com ramo proprio (a tabela guarda 255 nele)
3. as cinco bases da forma    = `OFS_FLAG_SHAPE_COPY_1..5`
4. time 0, uniforme de casa   = `OFS_KIT_PREVIEW + 2`

A quarta merece nota: o `+ 2` e medido, nao ajuste. A regiao de uniforme comeca
em `OFS_KIT_PREVIEW` e o editor de cor grava a partir do terceiro byte dela.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GERADOR = "wte/tools/dump_blococor.py"

EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
REL_EXE = "we-team-editor/we-team-editor.exe"
OFFSETS = ROOT / "wte" / "src" / "we2002_offsets.pas"
REL_OFFSETS = "wte/src/we2002_offsets.pas"
OUT_PAS = ROOT / "wte" / "src" / "wte_blococor.pas"

TIMES_N = 95

# As duas tabelas de `.data`, lidas do corpo do `0x00404E70`.
VA_TAB_PALETA = 0x00423247   # 95 bytes: qual paleta de bandeira cada time usa
VA_TAB_FORMA = 0x00423634    # 5 dwords: as cinco copias da forma de bandeira

# Os imediatos do `0x00404E70`, na ordem em que ele os usa.
SALTO_SETOR = 304            # 280 de EDC/ECC + 24 do cabecalho seguinte
DADOS_POR_SETOR = 2048

BASE_PALETA = 0x00BE35D8     # bandeira, chuteira e quarta paleta
BASE_UNIFORME = 0x0025AEF8   # os dois jogos de uniforme

LOGICO_BANDEIRA = 0x00011E26     # + 32 * TAB_PALETA[time]
LOGICO_BANDEIRA_SENEGAL = 0x000110A6   # o ramo `cmp eax,0x24`
TIME_SENEGAL = 36

LOGICO_UNIFORME_0 = 0x0002A042   # + 64 * time
LOGICO_UNIFORME_1 = 0x0002A062   # + 64 * time
UNIFORME_PASSO = 64

LOGICO_CHUTEIRA = 0x00010964     # + 32 * n, n de 0 a 7
CHUTEIRAS_N = 8

ABS_QUARTA_PALETA = 0x00BF690C   # imediato, sem conversao
ABS_PADRAO_CAMISA = 0x00DB3F7C   # idem


class BlocoCorError(Exception):
    pass


class PE:
    def __init__(self, data: bytes) -> None:
        if data[:2] != b"MZ":
            raise BlocoCorError(f"{REL_EXE}: nao comeca com MZ")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise BlocoCorError(f"{REL_EXE}: assinatura PE ausente")
        nsec = struct.unpack_from("<H", data, pe + 6)[0]
        szopt = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        self.data = data
        self.base = struct.unpack_from("<I", data, opt + 28)[0]
        self.sections = []
        for i in range(nsec):
            o = pe + 24 + szopt + i * 40
            self.sections.append((
                struct.unpack_from("<I", data, o + 12)[0],   # vaddr
                struct.unpack_from("<I", data, o + 8)[0],    # vsize
                struct.unpack_from("<I", data, o + 20)[0],   # raddr
                struct.unpack_from("<I", data, o + 16)[0]))  # rsize

    def off(self, va: int) -> int:
        rva = va - self.base
        for vaddr, vsize, raddr, rsize in self.sections:
            if vaddr <= rva < vaddr + max(vsize, rsize) and rva - vaddr < rsize:
                return raddr + (rva - vaddr)
        raise BlocoCorError(f"{REL_EXE}: {va:#010x} fora das secoes")


def absoluto(logico: int, base: int) -> int:
    """A conta do `0x00404E70`: logico -> offset absoluto no `.bin`."""
    return logico + SALTO_SETOR * (logico // DADOS_POR_SETOR) + base


def tabelas(pe: PE) -> tuple[list[int], list[int]]:
    o = pe.off(VA_TAB_PALETA)
    paleta = list(pe.data[o:o + TIMES_N])
    o = pe.off(VA_TAB_FORMA)
    forma = list(struct.unpack_from("<5I", pe.data, o))
    return paleta, forma


def offsets_do_pascal() -> dict[str, int]:
    if not OFFSETS.is_file():
        raise BlocoCorError(f"{REL_OFFSETS} nao existe")
    achados: dict[str, int] = {}
    for linha in OFFSETS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(OFS_[A-Z0-9_]+)\s*=\s*(\d+)\s*;", linha)
        if m:
            achados.setdefault(m.group(1), int(m.group(2)))
    return achados


def confere(paleta: list[int], forma: list[int]) -> list[str]:
    """As quatro ancoras. Devolve a lista de provas, ou aborta."""
    ofs = offsets_do_pascal()
    ruins = []
    provas = []

    def exige(nome: str, medido: int, rotulo: str) -> None:
        esperado = ofs.get(nome)
        if esperado is None:
            ruins.append(f"{REL_OFFSETS} nao tem {nome}")
        elif esperado != medido:
            ruins.append(f"{rotulo}: medido {medido}, {nome} diz {esperado}")
        else:
            provas.append(f"{rotulo} = {nome} = {medido}")

    exige("OFS_FLAG_COLOURS",
          absoluto(LOGICO_BANDEIRA + 32 * paleta[0], BASE_PALETA),
          "time 0, cores da bandeira")
    exige("OFS_FLAG_COLOURS_SENEGAL",
          absoluto(LOGICO_BANDEIRA_SENEGAL, BASE_PALETA),
          f"time {TIME_SENEGAL}, cores da bandeira")
    for i, base in enumerate(forma):
        exige(f"OFS_FLAG_SHAPE_COPY_{i + 1}", base,
              f"forma da bandeira, copia {i + 1}")
    medido = absoluto(LOGICO_UNIFORME_0, BASE_UNIFORME)
    esperado = ofs.get("OFS_KIT_PREVIEW")
    if esperado is None:
        ruins.append(f"{REL_OFFSETS} nao tem OFS_KIT_PREVIEW")
    elif esperado + 2 != medido:
        ruins.append(f"time 0, uniforme de casa: medido {medido}, "
                     f"OFS_KIT_PREVIEW + 2 diz {esperado + 2}")
    else:
        provas.append(f"time 0, uniforme de casa = OFS_KIT_PREVIEW + 2 = {medido}")

    if paleta[TIME_SENEGAL] == TIME_SENEGAL:
        ruins.append("a tabela de paleta guarda o proprio indice no time "
                     f"{TIME_SENEGAL}: o ramo `cmp eax,0x24` do original "
                     "deixou de fazer sentido")
    if len(paleta) != TIMES_N:
        ruins.append(f"a tabela de paleta tem {len(paleta)} bytes, "
                     f"esperado {TIMES_N}")
    if ruins:
        raise BlocoCorError(
            "o bloco de cor do `.exe` e o Pascal divergem:\n     "
            + "\n     ".join(ruins))
    return provas


def pascal(paleta: list[int], forma: list[int]) -> str:
    linhas = [
        "{ wte_blococor -- onde na imagem mora o bloco de cor de cada time.",
        "",
        "  GERADO por wte/tools/dump_blococor.py a partir de",
        "  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai",
        "  no gerador, e depois se regenera.",
        "",
        "  So DADO mora aqui. As sete regioes, os tamanhos e o `30` contra o",
        "  `32` sao logica, e ficam no `wte_cor.pas` junto de quem os usa --",
        "  a mesma divisao que a `wte_render2d` tem contra o `wte_uniformes`.",
        "",
        "  A CONTA E DO `0x00404E70`, e ela e a geometria MODE2/2352 escrita a",
        "  mao:",
        "",
        "      absoluto = logico + 304 * (logico div 2048) + base",
        "",
        "  Ela NAO passa pelo `EnderecoDeDados` do `we2002_estado` porque a",
        "  base nao cai em fronteira de setor: `$0025AEF8` nao e multiplo de",
        "  2352 mais 24. Fica como o original a escreve, com a base crua.",
        "",
        f"  PALETA_DA_BANDEIRA ({VA_TAB_PALETA:#010x}) e a unica coisa aqui que",
        "  nao e formula, e por isso este gerador existe: os 95 bytes NAO sao",
        "  identidade -- times compartilham paleta de bandeira. O time 36 vale",
        "  255 nela e tem ramo proprio no original (`cmp eax,0x24`), com",
        "  logico fixo.",
        "",
        f"  FORMA_DA_BANDEIRA ({VA_TAB_FORMA:#010x}) sao as CINCO copias do",
        "  byte de forma. O carregador le so a do meio; o gravador escreve as",
        "  cinco. Cada uma e offset absoluto, somado ao indice do time. }",
        "unit wte_blococor;",
        "",
        "{$mode objfpc}{$H+}",
        "",
        "interface",
        "",
        "uses",
        "  we2002_offsets;",
        "",
        "const",
        f"  BLOCOCOR_TIMES = {TIMES_N};",
        f"  BLOCOCOR_CHUTEIRAS = {CHUTEIRAS_N};",
        f"  BLOCOCOR_TIME_SENEGAL = {TIME_SENEGAL};",
        "",
        "  { Os imediatos do `0x00404E70`, na ordem em que ele os usa. }",
        f"  BLOCOCOR_SALTO = {SALTO_SETOR};",
        f"  BLOCOCOR_DADOS = {DADOS_POR_SETOR};",
        f"  BLOCOCOR_BASE_PALETA   = ${BASE_PALETA:08X};",
        f"  BLOCOCOR_BASE_UNIFORME = ${BASE_UNIFORME:08X};",
        f"  BLOCOCOR_LOG_BANDEIRA  = ${LOGICO_BANDEIRA:08X};",
        f"  BLOCOCOR_LOG_SENEGAL   = ${LOGICO_BANDEIRA_SENEGAL:08X};",
        f"  BLOCOCOR_LOG_UNIFORME0 = ${LOGICO_UNIFORME_0:08X};",
        f"  BLOCOCOR_LOG_UNIFORME1 = ${LOGICO_UNIFORME_1:08X};",
        f"  BLOCOCOR_PASSO_UNIFORME = {UNIFORME_PASSO};",
        f"  BLOCOCOR_LOG_CHUTEIRA  = ${LOGICO_CHUTEIRA:08X};",
        "",
        "  { Os dois que o original grava como imediato, sem conversao. }",
        f"  BLOCOCOR_QUARTA_PALETA = {ABS_QUARTA_PALETA};",
        f"  BLOCOCOR_PADRAO_CAMISA = {ABS_PADRAO_CAMISA};",
        "",
        "  { Qual paleta de bandeira cada time usa. 255 = tem ramo proprio. }",
        "  PALETA_DA_BANDEIRA: array[0..BLOCOCOR_TIMES - 1] of Byte = (",
    ]
    for i in range(0, TIMES_N, 12):
        pedaco = ", ".join(str(v) for v in paleta[i:i + 12])
        fim = "," if i + 12 < TIMES_N else ""
        linhas.append(f"    {pedaco}{fim}")
    linhas += [
        "  );",
        "",
        "  { As cinco copias do byte de forma de bandeira, conferidas contra",
        "    os `OFS_FLAG_SHAPE_COPY_*` do `we2002_core` pelo gerador. }",
        "  FORMA_DA_BANDEIRA: array[0..4] of TOffset = (",
        "    OFS_FLAG_SHAPE_COPY_1, OFS_FLAG_SHAPE_COPY_2,",
        "    OFS_FLAG_SHAPE_COPY_3, OFS_FLAG_SHAPE_COPY_4,",
        "    OFS_FLAG_SHAPE_COPY_5",
        "  );",
        "",
        "implementation",
        "",
        "end.",
    ]
    return "\n".join(linhas) + "\n"


def gera() -> tuple[dict[Path, str], list[str]]:
    if not EXE.is_file():
        raise BlocoCorError(f"{REL_EXE} nao existe.")
    pe = PE(EXE.read_bytes())
    paleta, forma = tabelas(pe)
    provas = confere(paleta, forma)
    return {OUT_PAS: pascal(paleta, forma)}, provas


def do_check(files: dict[Path, str], provas: list[str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de dump_blococor.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    for p in provas:
        print(f"dump_blococor: {p}")
    print(f"dump_blococor: {len(files)} arquivo(s) em dia com {REL_EXE}")
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
        files, provas = gera()
    except BlocoCorError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files, provas) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
