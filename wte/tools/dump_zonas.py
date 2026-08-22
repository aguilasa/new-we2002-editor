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

## E as DUAS MALHAS, que chegaram na WTE-TASK-29

O mesmo formulario tem duas grades de marcador: a `malla1`, com quatro colunas
de `simbolo`, e a `malla2`, com seis de `tirador`. Clicar numa delas escolhe a
coluna pelo X e move o marcador daquela coluna para a linha do Y.

Elas moram aqui, e nao num gerador proprio, porque sao **geometria do mesmo
formulario** e a conferencia usa as mesmas duas fontes: o `.text`, que da os
tres numeros, e o `.lfm`, que da as coordenadas dos marcadores. Um gerador novo
duplicaria a leitura do PE e a do formulario para decodificar tres imediatos.

Os tres numeros de cada handler saem de padroes curtos:

    mov ecx,IMM ; cdq ; idiv ecx        ' a largura da coluna
    sar ecx,N   ; shl ecx,N             ' o passo da linha, 1 shl N
    add edx,IMM                         ' a folga do marcador dentro da malha
    mov eax,VA                          ' o prefixo do nome (`simbolo`/`tirador`)

E a conferencia cruzada e o que da valor a eles -- **o `.lfm` tem de concordar
nas quatro contas**:

1. `malla.Width div largura_da_coluna` = quantos marcadores existem;
2. `marcador1.Left` = `malla.Left + folga`;
3. `marcador1.Top` = `malla.Top + folga`;
4. o passo de `Left` entre marcadores vizinhos = a largura da coluna.

Uma folga lida errada quebra as duas do meio; uma largura de coluna errada
quebra a primeira e a quarta. E as duas fontes sao independentes: uma e o
codigo de 2002, a outra e o formulario de 2002.

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
MALHAS_TSV_NAME = "malhas.tsv"

# `estrategia.FormCreate`, do published_methods.tsv. O fim e o inicio do
# handler seguinte na mesma unidade (`rectanguloDragOver`).
INI = 0x004090FC
FIM = 0x00409644

BASE = 0x00433E5C          # ebx
CAMPOS = 4                 # x1, y1, x2, y2
PASSO = CAMPOS * 4         # 16 bytes por registro

LFM = "wte/forms/ep2002_estrategia.lfm"
CAMPOS_TSV = "wte/re/campos.tsv"

# As duas malhas: (handler, inicio, fim, campo do formulario, prefixo esperado).
# O `fim` de cada uma e o inicio do corpo seguinte -- o da `malla2` e a rotina
# interna `0x0040a0b4`, que nao e handler publicado e por isso nao esta no TSV.
MALHAS = (
    ("malla1MouseDown", 0x00409F4C, 0x0040A000, "malla1", "simbolo"),
    ("malla2MouseDown", 0x0040A000, 0x0040A0B4, "malla2", "tirador"),
)

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


# ------------------------------------------------------- as duas malhas ----

def _shapes(prefixo: str) -> list[tuple[int, int, int]]:
    """Os `TShape` chamados `<prefixo><n>`, como (n, Left, Top), ordenados.

    O `.lfm` NAO os declara em ordem -- `simbolo3` vem antes do `simbolo1` --,
    e ler na ordem do arquivo daria passo negativo na primeira conta.
    """
    texto = (ROOT / LFM).read_text(encoding="utf-8", errors="replace")
    saida = []
    for m in re.finditer(
            rf"^  object {prefixo}(\d+): TShape$(.*?)^  (?:object|end)",
            texto, re.MULTILINE | re.DOTALL):
        esq = re.search(r"^\s*Left = (-?\d+)", m.group(2), re.MULTILINE)
        topo = re.search(r"^\s*Top = (-?\d+)", m.group(2), re.MULTILINE)
        if not esq or not topo:
            raise DumpError(f"{LFM}: {prefixo}{m.group(1)} sem Left/Top")
        saida.append((int(m.group(1)), int(esq.group(1)), int(topo.group(1))))
    if not saida:
        raise DumpError(f"{LFM}: nenhum `{prefixo}N: TShape`")
    return sorted(saida)


def _imagem(nome: str) -> tuple[int, int, int, int]:
    """Left, Top, Width, Height do `TImage` de nome dado, do `.lfm`."""
    texto = (ROOT / LFM).read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^  object {nome}: TImage$(.*?)^  object ", texto,
                  re.MULTILINE | re.DOTALL)
    if not m:
        raise DumpError(f"{LFM}: nao achei o objeto `{nome}`")
    vals = []
    for prop in ("Left", "Top", "Width", "Height"):
        achado = re.search(rf"^\s*{prop} = (-?\d+)", m.group(1), re.MULTILINE)
        if not achado:
            raise DumpError(f"{LFM}: `{nome}` sem {prop}")
        vals.append(int(achado.group(1)))
    return tuple(vals)


def _campo_por_offset(offset: int) -> str:
    """O nome do campo do `estrategia` naquele deslocamento, do campos.tsv.

    A terceira fonte: o `.text` diz `[esi+0x384]` e nao diz de quem, e contar
    componentes na ordem do `.dfm` ja deu o resultado oposto ao certo noutro
    formulario. A *published field table* e quem decide.
    """
    for linha in (ROOT / CAMPOS_TSV).read_text(encoding="utf-8").splitlines()[1:]:
        form, desl, campo, _classe = linha.split("\t")
        if form == "estrategia" and int(desl, 16) == offset:
            return campo
    raise DumpError(f"{CAMPOS_TSV}: estrategia nao tem campo em {offset:#06x}")


def _acha(corpo: bytes, padrao: bytes, o_que: str, handler: str) -> int:
    i = corpo.find(padrao)
    if i < 0:
        raise DumpError(f"{REL_EXE}: {handler} sem {o_que} "
                        f"({padrao.hex()}) -- a afirmacao caducou")
    if corpo.find(padrao, i + 1) >= 0:
        raise DumpError(f"{REL_EXE}: {handler} tem {o_que} mais de uma vez; "
                        f"o decodificador leria a errada")
    return i


def _cadeia_carregada(pe: PE, corpo: bytes, handler: str) -> tuple[int, str]:
    """O unico `mov eax,imm32` do corpo cujo destino e uma cadeia imprimivel."""
    achados = []
    for i in range(len(corpo) - 5):
        if corpo[i] != 0xB8:
            continue
        va = _u32(corpo, i + 1)
        off = pe.off(va)
        if off is None:
            continue
        bruto = pe.data[off:off + 33].split(b"\x00")[0]
        if not 1 <= len(bruto) <= 32:
            continue
        if not all(0x20 <= c < 0x7F for c in bruto):
            continue
        achados.append((va, bruto.decode("latin-1")))
    unicos = sorted(set(achados))
    if len(unicos) != 1:
        raise DumpError(
            f"{REL_EXE}: {handler}: {len(unicos)} `mov eax,imm32` apontando "
            f"para cadeia ({[c for _v, c in unicos]}) -- esperava exatamente um")
    return unicos[0]


def malha(pe: PE, handler: str, ini: int, fim: int, campo_esperado: str,
          prefixo_esperado: str) -> dict:
    """Os tres numeros e o prefixo de um dos dois `mallaNMouseDown`."""
    a, b = pe.off(ini), pe.off(fim)
    if a is None or b is None:
        raise DumpError(f"{REL_EXE}: {ini:#010x}..{fim:#010x} fora de secao")
    corpo = pe.data[a:b]

    # `mov ecx,IMM32 ; cdq ; idiv ecx` -- a largura da coluna.
    i = _acha(corpo, b"\x99\xf7\xf9", "o `cdq ; idiv ecx`", handler)
    if i < 5 or corpo[i - 5] != 0xB9:
        raise DumpError(f"{REL_EXE}: {handler}: o divisor nao vem de um "
                        f"`mov ecx,imm32` imediatamente antes do `idiv`")
    coluna = _u32(corpo, i - 4)

    # `sar ecx,N` e `shl ecx,N` -- o passo da linha e `1 shl N`, e os dois
    # deslocamentos tem de ser o MESMO: um snap que descesse e subisse por
    # valores diferentes nao seria snap.
    i = _acha(corpo, b"\xc1\xf9", "o `sar ecx,N`", handler)
    j = _acha(corpo, b"\xc1\xe1", "o `shl ecx,N`", handler)
    if corpo[i + 2] != corpo[j + 2]:
        raise DumpError(f"{REL_EXE}: {handler}: `sar {corpo[i + 2]}` contra "
                        f"`shl {corpo[j + 2]}` -- nao e arredondamento")
    linha = 1 << corpo[i + 2]

    # `add edx,IMM8` -- a folga do marcador dentro da malha.
    i = _acha(corpo, b"\x83\xc2", "o `add edx,imm8` da folga", handler)
    folga = _i8(corpo[i + 2])

    # `mov eax,VA` -- o prefixo do nome, e ele fica no `.data`.
    #
    # O corpo tem DOIS `mov eax,imm32`: o primeiro carrega o registro de
    # excecao que o prologo do C++Builder instala, e so o segundo e cadeia. O
    # filtro nao e a ordem -- e o que esta no destino: um e zero, o outro e
    # texto imprimivel terminado em NUL. Filtrar por ordem quebraria no dia em
    # que o prologo mudasse; filtrar pelo conteudo diz o que se procura.
    va, prefixo = _cadeia_carregada(pe, corpo, handler)
    if prefixo != prefixo_esperado:
        raise DumpError(f"{REL_EXE}: {handler}: prefixo `{prefixo}` em "
                        f"{va:#010x}, esperava `{prefixo_esperado}`")

    # `mov ecx,[esi+DISP32]` -- de qual `TImage` sai o `Top` de referencia.
    i = _acha(corpo, b"\x8b\x8e", "o `mov ecx,[esi+disp32]` da malha", handler)
    campo_nome = _campo_por_offset(_u32(corpo, i + 2))
    if campo_nome != campo_esperado:
        raise DumpError(f"{REL_EXE}: {handler}: le o Top de `{campo_nome}`, "
                        f"esperava `{campo_esperado}`")

    # `mov edx,[ecx+0x44]` -- e o campo lido e mesmo o `Top` do `TControl`.
    _acha(corpo, b"\x8b\x51\x44", "o `mov edx,[ecx+0x44]` (TControl.FTop)",
          handler)
    # `inc edx ; call` -- a base UM do sufixo do nome.
    _acha(corpo, b"\x42\xe8", "o `inc edx` da base um", handler)

    return {"handler": handler, "endereco": ini, "bytes": fim - ini,
            "campo": campo_nome, "prefixo": prefixo, "coluna": coluna,
            "linha": linha, "folga": folga}


def confere_malhas(malhas: list[dict]) -> list[dict]:
    """As quatro contas contra o `.lfm` -- a segunda fonte."""
    for m in malhas:
        esq, topo, larg, alt = _imagem(m["campo"])
        shapes = _shapes(m["prefixo"])
        m["colunas"] = larg // m["coluna"]
        m["linhas"] = alt // m["linha"]
        if len(shapes) != m["colunas"]:
            raise DumpError(
                f"{m['handler']}: {larg} div {m['coluna']} = {m['colunas']} "
                f"coluna(s), mas o {LFM} tem {len(shapes)} `{m['prefixo']}N`")
        if [n for n, _e, _t in shapes] != list(range(1, len(shapes) + 1)):
            raise DumpError(f"{LFM}: os `{m['prefixo']}N` nao sao 1..N")
        if shapes[0][1] != esq + m["folga"]:
            raise DumpError(
                f"{m['handler']}: {m['prefixo']}1.Left = {shapes[0][1]}, mas "
                f"{m['campo']}.Left + folga = {esq} + {m['folga']}")
        if shapes[0][2] != topo + m["folga"]:
            raise DumpError(
                f"{m['handler']}: {m['prefixo']}1.Top = {shapes[0][2]}, mas "
                f"{m['campo']}.Top + folga = {topo} + {m['folga']}")
        passos = {b[1] - a[1] for a, b in zip(shapes, shapes[1:])}
        if passos != {m["coluna"]}:
            raise DumpError(
                f"{m['handler']}: os `{m['prefixo']}N` andam {sorted(passos)} "
                f"px em Left, e a coluna do `.text` mede {m['coluna']}")
    passos = {(m["coluna"], m["linha"], m["folga"]) for m in malhas}
    if len(passos) != 1:
        raise DumpError(
            "as duas malhas usam constantes diferentes "
            f"{sorted(passos)} -- o Pascal as emite uma vez so")
    return malhas


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


def tsv_malhas(malhas) -> str:
    linhas = ["handler\tendereco\tmalha\tprefixo\tcolunas\tlinhas"
              "\tpasso_x\tpasso_y\tfolga"]
    for m in malhas:
        linhas.append(
            f"{m['handler']}\t0x{m['endereco']:08x}\t{m['campo']}"
            f"\t{m['prefixo']}\t{m['colunas']}\t{m['linhas']}"
            f"\t{m['coluna']}\t{m['linha']}\t{m['folga']}")
    return "\n".join(linhas) + "\n"


def pascal(zonas, malhas) -> str:
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
        "  o `estrategia.lista_formacionesClick`.",
        "",
        "  E as DUAS MALHAS do mesmo formulario, que sao geometria e nao",
        "  tabela: quatro colunas de `simbolo` e seis de `tirador`. Cada",
        "  numero foi conferido contra o `.lfm` -- a largura da malha dividida",
        "  pelo passo tem de dar a contagem de marcadores, e o primeiro deles",
        "  tem de estar na folga a partir do canto da malha. }",
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
    corpo += ["  );", ""]

    # As tres constantes sao as MESMAS nas duas malhas -- o `confere_malhas`
    # aborta se deixarem de ser --, e por isso saem uma vez so.
    ref = malhas[0]
    corpo += [
        "  { A grade dos marcadores. `MALHA_PASSO_X` e a largura de uma",
        "    coluna; `MALHA_PASSO_Y` e a altura de uma linha, e ela sai do",
        "    deslocamento do `sar`/`shl` e nao de um imediato; `MALHA_FOLGA` e",
        "    o quanto o marcador recua do canto da malha. Os tres sao iguais",
        "    nas duas malhas, e o gerador aborta se deixarem de ser. }",
        f"  MALHA_PASSO_X = {ref['coluna']};",
        f"  MALHA_PASSO_Y = {ref['linha']};",
        f"  MALHA_FOLGA = {ref['folga']};",
        "",
    ]
    for m in malhas:
        corpo += [
            f"  {{ {m['handler']} -- {m['endereco']:#010x}, sobre a "
            f"`{m['campo']}`. }}",
            f"  {m['prefixo'].upper()}_PREFIXO = '{m['prefixo']}';",
            f"  {m['prefixo'].upper()}_COLUNAS = {m['colunas']};",
            "",
        ]
    corpo += [
        "implementation",
        "",
        "end.",
    ]
    return "\n".join(corpo) + "\n"


def md_malhas(malhas) -> list[str]:
    ref = malhas[0]
    linhas = [
        "",
        "## As duas malhas de marcador — `malla1MouseDown` e `malla2MouseDown`",
        "",
        "*(WTE-TASK-29)* O mesmo formulário tem duas grades. Clicar numa delas",
        "**escolhe a coluna pelo X e move o marcador daquela coluna para a",
        "linha do Y** — o `Left` de cada marcador é fixo, quem anda é o `Top`.",
        "",
        f"O passo é `{ref['coluna']}` px na horizontal e `{ref['linha']}` na",
        f"vertical, e a folga do marcador é `{ref['folga']}` px. **Os três são",
        "os mesmos nas duas malhas**, e este gerador aborta se deixarem de ser.",
        "",
        "| handler | endereço | malha | prefixo | colunas | linhas |",
        "|---|---|---|---|---:|---:|",
    ]
    for m in malhas:
        linhas.append(
            f"| `{m['handler']}` | `{m['endereco']:#010x}` | `{m['campo']}` | "
            f"`{m['prefixo']}N` | {m['colunas']} | {m['linhas']} |")
    linhas += [
        "",
        "### As quatro contas que o `.lfm` confere",
        "",
        "Os três números saem do `.text`; as coordenadas dos marcadores saem do",
        "formulário. As duas fontes são independentes — uma é o código de 2002,",
        "a outra é o formulário de 2002 — e têm de concordar em quatro pontos:",
        "",
    ]
    for m in malhas:
        esq, topo, larg, alt = _imagem(m["campo"])
        shapes = _shapes(m["prefixo"])
        linhas += [
            f"**`{m['campo']}`** — {larg}×{alt} px em ({esq}, {topo}):",
            "",
            f"1. `{larg} div {m['coluna']}` = **{m['colunas']}**, e o `.lfm` "
            f"declara {len(shapes)} `{m['prefixo']}N`;",
            f"2. `{m['prefixo']}1.Left` = {shapes[0][1]} = "
            f"`{esq} + {m['folga']}`;",
            f"3. `{m['prefixo']}1.Top` = {shapes[0][2]} = "
            f"`{topo} + {m['folga']}`;",
            f"4. os marcadores andam {shapes[1][1] - shapes[0][1]} px em "
            f"`Left`, que é o passo lido do `.text`.",
            "",
        ]
    linhas += [
        "Uma folga lida errada quebra as duas do meio; um passo errado quebra a",
        "primeira e a quarta.",
        "",
        "### O que eles **não** fazem",
        "",
        "Nenhum dos dois toca a imagem de CD, e nenhum dos dois lê dado. São "
        + " e ".join(str(m["bytes"]) for m in malhas)
        + " bytes de geometria:",
        "dividir, achar o marcador pelo nome, escrever `Top`.",
        "Quem lê a posição de volta é o `estrategia.BitBtn3Click`",
        "(`0x0040a660`), que é da",
        "[WTE-TASK-30](../../docs/tasks/30-handlers-auxiliares.md); quem a",
        "escreve a partir do dado é a rotina interna `0x0040a0b4`, portada",
        "como `PreencheTelaDeTatica` na `wte_tatica.pas` (CORR-WTE-082).",
        "**O caminho fechou nos dois sentidos** desde a CORR-WTE-081: a ida é",
        "o `PreencheTelaDeTatica` e a volta é o ` Accept`, que grava 45 bytes",
        "por time e tem gate byte a byte no `golden-17-tatica`.",
        "",
        "E só o botão esquerdo faz alguma coisa: o original testa `cl` na",
        "entrada e sai sem fazer nada — sem limpar estado — para qualquer outro,",
        "como o `bolaMouseDown` faz.",
        "",
    ]
    return linhas


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
    malhas = confere_malhas([malha(pe, *m) for m in MALHAS])
    return {
        OUT_RE / TSV_NAME: tsv(zonas),
        OUT_RE / MALHAS_TSV_NAME: tsv_malhas(malhas),
        OUT_RE / MD_NAME: md(zonas) + "\n".join(md_malhas(malhas)),
        OUT_PAS: pascal(zonas, malhas),
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
