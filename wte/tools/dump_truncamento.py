#!/usr/bin/env python3
"""Onde cada campo editavel corta o texto -- o `MaxLength` de cada um.

Gera `wte/re/truncamento.md` e `wte/re/truncamento.tsv` -- fecha o criterio
"comportamento de truncamento documentado por campo" da
[WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md).

## O problema que ele resolve

Todo campo de texto do editor tem um limite, e o limite **nao esta num lugar
so**: quatro controles o declaram no `.dfm` e tres o recebem em tempo de
execucao, por `TCustomEdit::SetMaxLength`. Ler so o `.dfm` acha quatro dos
sete e nao anuncia os outros tres; ler so o codigo acha tres e perde os quatro.

Pior: dos tres de tempo de execucao, **nenhum e literal**. Dois sao expressao
sobre a largura do campo de destino -- metade dela, ou ela menos um --, e a
metade tem motivo: o campo e kanji, dois bytes por caractere.

## As duas fontes, e por que elas se conferem

| Fonte | O que da |
|---|---|
| os 18 `.dfm` | o `MaxLength` declarado, quando ha |
| o `.text` do `.exe` | as tres chamadas a `SetMaxLength`, com a expressao |
| `wte/src/we2002_team.pas`, `we2002_player.pas` | a largura do campo de destino |

A terceira e o oraculo de FORMATO -- o `we2002_core`, byte-identico ao
`ed.exe`. Ela nao repete as outras duas: e o outro lado da conta. O gerador
**aborta** se a expressao decodificada do `.exe` nao casar com a largura que a
camada de dados declara, e e esse casamento que prova que a leitura da
expressao esta certa:

    raw_kanji_name    40 bytes  -> div 2 -> 20   (dois bytes por caractere)
    mixed_case_name   20 bytes  -> menos 1 -> 19 (o byte do terminador)
    abbreviations[0]   4 bytes  -> literal 3     (idem)

## O achado que ele registra

`jugador.casilla_dorsal` declara `MaxLength = 10` e recebe **numero de
camisa**, que tem no maximo tres digitos. O limite util nao vem dali: vem do
`casilla_dorsalKeyPress`, que recusa tecla. Quem portasse "o campo corta em 10"
teria copiado um numero verdadeiro e irrelevante.

Uso:

    python3 wte/tools/dump_truncamento.py            # regenera
    python3 wte/tools/dump_truncamento.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from dump_auxiliares import PE, DumpError, decode

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
DFM_DIR = ROOT / "wte" / "re" / "dfm"
CAMPOS = ROOT / "wte" / "re" / "campos.tsv"
OUT = ROOT / "wte" / "re"

REL_EXE = "we-team-editor/we-team-editor.exe"
GERADOR = "wte/tools/dump_truncamento.py"

TSV_NAME = "truncamento.tsv"
MD_NAME = "truncamento.md"

SETMAXLENGTH = "@Stdctrls@TCustomEdit@SetMaxLength$qqri"

# Quantos bytes antes da chamada o decodificador aceita procurar os dois
# operandos. Medido: o maior sitio ocupa 27 bytes.
JANELA = 64

# A tabela de LOTES do original, e o array de medidas que ela alimenta.
#
# `lista_equiposChange` (0x0040cbc8) percorre `0x004231a0` -- 3 linhas de 6
# colunas de DWORD, 24 bytes por linha -- e, para cada entrada nao-zero, chama
# `0x00403c0c`, que ANDA pelo arquivo ate o registro do time selecionado e
# grava tres campos por lote em `0x00433a0c`:
#
#     +0  o offset do registro no arquivo (`ftell` - 1)
#     +4  a LARGURA do registro em bytes  (run nao-zero + run zero)
#     +8  os proprios bytes do registro
#
# O passo e 312 bytes por linha e 52 por coluna, lidos do
# `lea ecx,[eax*8+0x433a0c]` com `eax = linha*39` e do `edx = coluna*13`
# multiplicado por 4 no `mov [ecx+edx*4],eax`.
#
# Logo `0x00433a10` e o campo `+4` da linha 0 coluna 0, e `0x00433b48` e o `+4`
# da linha 1 coluna 0, 312 bytes adiante. **Nao sao constantes**: sao medidas
# refeitas a cada troca de time, e a travessia pula o rodape de cada setor
# MODE2/2352 (`0x00403388`: se `ftell % 2352 == 2072`, avanca 304).
TABELA_DE_LOTES = 0x004231A0
LOTE_LINHAS, LOTE_COLUNAS = 3, 6
BASE_DAS_MEDIDAS = 0x00433A0C
PASSO_LINHA, PASSO_COLUNA, CAMPO_LARGURA = 312, 52, 4

OFFSETS_PAS = ROOT / "wte" / "src" / "we2002_offsets.pas"
TABELAS_PAS = ROOT / "wte" / "src" / "we2002_tables.pas"

# O destino de cada limite.
#
# Para os dois que vem do codigo o destino **nao e um campo de struct**: e uma
# tabela de comprimento POR TIME. Foi esse o erro que custou duas divergencias
# seguidas -- a primeira versao declarou `raw_kanji_name` (40 bytes, div 2 =
# 20) e a segunda desistiu e pos o literal 5 lido da tela. As duas partiam do
# mesmo modelo errado, o de que existe UM numero.
#
# Entrada dos dois de codigo: (`OFS_*` esperado, tabela de comprimento). O
# `OFS_*` nao e decorativo: o gerador **decodifica** o endereco do operando ate
# a entrada de `0x004231a0`, le o offset que esta la e aborta se ele nao for o
# `OFS_*` declarado. E isso que prova o mapeamento, e e o que faltava -- a
# conferencia antiga so batia a aritmetica contra uma largura escrita a mao, e
# por isso passou com o campo errado.
#
# Entrada dos que vem do `.dfm`: (arquivo Pascal, campo), como antes.
DESTINOS = {
    "edit_nombre1": ("OFS_TEAM_NAME_KANJI", "TEAM_NAME_KANJI_LEN"),
    "edit_nombre2": ("OFS_TEAM_NAME_3", "TEAM_NAME_LEN_3"),
    "edit_nombre3": ("wte/src/we2002_team.pas", "abbreviations"),
    "casilla_nombre": ("wte/src/we2002_player.pas", "name"),
}

# Os dois campos cujo limite e por time. Separados porque o resto da ferramenta
# trata largura de struct, e misturar os dois modelos foi o defeito.
POR_TIME = {"edit_nombre1", "edit_nombre2"}

# O lote que o original DECREMENTA antes de guardar, e o porque.
#
# `0x00403c0c` termina com um caso especial que so vale para a linha 0 coluna 0
# (`0x00403d59`: `test edi,edi` / `cmp [ebp-0x4],0`):
#
#     dec DWORD PTR [0x00433a10 + linha*312 + coluna*52]
#     mov DWORD PTR [0x00433a14 + linha*312 + coluna*52], 1
#
# Ou seja: **o lote kanji guarda a largura MENOS UM**, e o campo `+8` recebe 1
# em vez do 2 que todos os outros recebem. Esse `+8` e o modo do decodificador
# de texto (`0x00403598` compara com `0x82`, o byte-lider Shift-JIS): 1 = dois
# bytes por caractere, 2 = um byte.
#
# Sem esse `dec`, `div 2` da um a mais. Foi ele que sustentou duas versoes
# erradas seguidas desta ferramenta -- `raw_kanji_name` (40 div 2 = 20) e
# depois o literal 5 lido da tela --, porque a conta parecia nao fechar com
# nenhum campo do formato.
#
# Medido em 2026-08-18 (CORR-WTE-064) dirigindo o oraculo em **tres** times de
# larguras diferentes, digitando `ABCDEFGHIJKLMNOP` no `edit_nombre1`:
#
#     time  2  (LEN  6)  ->  ABCDE          =  5
#     time  0  (LEN  8)  ->  ABCDEFG        =  7
#     time 56  (LEN 14)  ->  ABCDEFGHIJKLM  = 13
#
# A diferenca e **constante em 1**, nao proporcional, e `(largura - 1) div 2`
# fecha nos tres. Sobre a imagem japonesa isso e `TEAM_NAME_KANJI_LEN - 1` em
# **95/95** times.
LOTE_COM_DECREMENTO = ("OFS_TEAM_NAME_KANJI",)

# O time de referencia das colunas numericas -- o mesmo que o
# `compara_tela.sh --nomes` dirige (`IDX_EDICAO`), para o numero do documento e
# o numero da tela serem o mesmo numero.
TIME_DE_REFERENCIA = 2

# Campo cujo `MaxLength` NAO governa o truncamento, e por que. Sem esta lista o
# documento afirmaria que o numero de camisa corta em 10 caracteres.
SEM_GOVERNO = {
    "casilla_dorsal": (
        "número de camisa, no máximo três dígitos. Quem recusa tecla é o "
        "`casilla_dorsalKeyPress`; o `MaxLength` de 10 nunca chega a valer"),
    "casilla_precio": (
        "campo numérico de preço. O `MaxLength` de 3 limita dígito, não texto "
        "— ver a WTE-TASK-32"),
}


# ------------------------------------------------------------ leitura do DFM --

def maxlength_dos_dfm() -> dict[tuple[str, str], int]:
    """(`formulario`, `controle`) -> `MaxLength` declarado."""
    fora: dict[tuple[str, str], int] = {}
    for caminho in sorted(DFM_DIR.glob("*.dfm")):
        formulario = caminho.stem
        atual: str | None = None
        for linha in caminho.read_text(encoding="latin1").splitlines():
            corte = linha.strip()
            if corte.startswith("object "):
                atual = corte[len("object "):].split(":")[0].strip()
            elif atual and corte.startswith("MaxLength = "):
                fora[(formulario, atual)] = int(corte[len("MaxLength = "):])
    return fora


def campos() -> dict[tuple[str, int], str]:
    """(`formulario`, deslocamento) -> nome do campo publicado."""
    fora: dict[tuple[str, int], str] = {}
    linhas = CAMPOS.read_text(encoding="utf-8").splitlines()[1:]
    for linha in linhas:
        formulario, offset, campo, _classe = linha.split("\t")
        fora[(formulario, int(offset, 16))] = campo
    return fora


def largura_do_destino(rel: str, campo: str) -> int:
    """Quantos bytes o campo da camada de dados tem, do Pascal gerado."""
    texto = (ROOT / rel).read_text(encoding="utf-8")
    # `nome: array[0..N] of AnsiChar` ou `array[0..K] of array[0..N] of AnsiChar`
    m = re.search(rf"^\s*{re.escape(campo)}:\s*array\[0\.\.(\d+)\]\s*of\s*"
                  rf"(?:array\[0\.\.(\d+)\]\s*of\s*)?AnsiChar", texto,
                  re.MULTILINE)
    if not m:
        raise DumpError(f"{rel}: nao achei `{campo}` como vetor de AnsiChar")
    interno = m.group(2)
    return int(interno if interno is not None else m.group(1)) + 1


# --------------------------------------------------------- leitura do `.text` --

def _u32(d: bytes, o: int) -> int:
    return int.from_bytes(d[o:o + 4], "little")


def thunk_de(pe: PE, simbolo: str) -> int:
    """O `jmp DWORD PTR ds:<IAT>` que leva ao importado `simbolo`."""
    iat = pe.imports()
    entradas = [va for va, nome in iat.items() if nome == simbolo]
    if len(entradas) != 1:
        raise DumpError(
            f"{REL_EXE}: {len(entradas)} entrada(s) de IAT para `{simbolo}`, "
            f"esperava uma")
    alvo = entradas[0]
    ini, o_ini, tam = faixa(pe)
    d = pe.data
    achados = []
    for o in range(o_ini, o_ini + tam - 6):
        if d[o] == 0xFF and d[o + 1] == 0x25 and _u32(d, o + 2) == alvo:
            achados.append(ini + (o - o_ini))
    if len(achados) != 1:
        raise DumpError(
            f"{REL_EXE}: {len(achados)} thunk(s) para `{simbolo}`")
    return achados[0]


def faixa(pe: PE) -> tuple[int, int, int]:
    """(VA inicial, offset de arquivo inicial, tamanho) da `.text`.

    Devolve offset e tamanho em vez de VA final: `pe.off` de um endereco um
    byte alem do fim devolve `None`, e foi assim que a primeira versao deste
    script morreu numa subtracao com `None`.
    """
    for nome, vaddr, _vsize, raddr, rsize in pe.sections:
        if nome == ".text":
            return pe.base + vaddr, raddr, rsize
    raise DumpError(f"{REL_EXE}: sem secao .text")


def sitios(pe: PE, thunk: int) -> list[int]:
    """Os offsets de arquivo de cada `call thunk`."""
    _ini, o_ini, tam = faixa(pe)
    d = pe.data
    fora = []
    o = o_ini
    while o < o_ini + tam - 5:
        if d[o] == 0xE8:
            rel = struct.unpack_from("<i", d, o + 1)[0]
            if o + 5 + rel == pe.off(thunk):
                fora.append(o)
        o += 1
    return fora


def expressao(pe: PE, o_call: int) -> tuple[str, int]:
    """(`forma`, operando) do valor que vai em `edx` antes da chamada.

    Tres formas, e nenhuma outra e aceita -- expressao que este decodificador
    nao reconheca aborta em vez de virar um numero plausivel:

        mov edx,IMM                        -> ('literal', IMM)
        mov edx,ds:ADDR ; dec edx          -> ('menos_um', ADDR)
        mov edx,ds:ADDR ; sar edx,1 ; ...  -> ('metade', ADDR)
    """
    d = pe.data
    ini = max(0, o_call - JANELA)
    forma: tuple[str, int] | None = None
    o = ini
    while o < o_call:
        tam, _c, _a = decode(d, o, o_call + 1)
        if d[o] == 0xBA and tam == 5:                       # mov edx,imm32
            forma = ("literal", _u32(d, o + 1))
        elif d[o] == 0x8B and d[o + 1] == 0x15:             # mov edx,ds:addr
            endereco = _u32(d, o + 2)
            resto = d[o + 6:o + 14]
            if resto[:2] == b"\xd1\xfa":                    # sar edx,1
                forma = ("metade", endereco)
            elif resto[:1] == b"\x4a":                      # dec edx
                forma = ("menos_um", endereco)
            elif resto[:2] == b"\x8b\x82":                  # mov eax,[edx+..]
                # `edx` aqui e o ponteiro do formulario, nao um comprimento --
                # o terceiro sitio carrega o global em `edx`, indexa o controle
                # e so depois poe o literal em `edx`. Tratar isto como
                # expressao daria "MaxLength := endereco do formulario".
                pass
            else:
                raise DumpError(
                    f"{REL_EXE}: em {o:#x} um `mov edx,ds:{endereco:#010x}` "
                    f"seguido de {resto[:2]!r}, que este decodificador nao "
                    f"reconhece")
        o += tam
    if forma is None:
        raise DumpError(
            f"{REL_EXE}: chamada a SetMaxLength em {o_call:#x} sem carga de "
            f"edx nos {JANELA} bytes anteriores")
    return forma


def alvo_do_sitio(pe: PE, o_call: int) -> tuple[str, int]:
    """(`formulario`, deslocamento) do controle que recebe o `MaxLength`.

    O padrao e `mov REG,ds:<global do formulario>` seguido de
    `mov eax,[REG+disp]`. O global e resolvido pela tabela de exportacao do
    proprio `.exe`, que nomeia `_MainForm`, `_jugador` e os demais.
    """
    d = pe.data
    exportados = {pe.base + rva: nome for rva, nome in pe.exports().items()}
    ini = max(0, o_call - JANELA)
    globais: dict[int, int] = {}      # registrador (modrm base) -> endereco
    disp: int | None = None
    formulario: str | None = None
    o = ini
    while o < o_call:
        tam, _c, _a = decode(d, o, o_call + 1)
        # mov eax,ds:addr / mov ecx,ds:addr / mov edx,ds:addr
        if d[o] == 0xA1 and tam == 5:                       # mov eax,ds:addr
            globais[0] = _u32(d, o + 1)
        elif d[o] == 0x8B and d[o + 1] in (0x0D, 0x15) and tam == 6:
            globais[{0x0D: 1, 0x15: 2}[d[o + 1]]] = _u32(d, o + 2)
        # mov eax,[REG+disp32]
        elif d[o] == 0x8B and (d[o + 1] & 0xF8) == 0x80 and tam == 6:
            base = d[o + 1] & 0x07
            if base in globais:
                nome = exportados.get(globais[base])
                if nome:
                    formulario = nome.lstrip("_")
                    disp = _u32(d, o + 2)
        o += tam
    if formulario is None or disp is None:
        raise DumpError(
            f"{REL_EXE}: nao consegui resolver o controle da chamada em "
            f"{o_call:#x}")
    return formulario, disp


# ------------------------------------------------------------------- saidas --

class Linha:
    __slots__ = ("formulario", "campo", "maxlength", "fonte", "expr",
                 "destino", "largura", "nota")

    def __init__(self, formulario, campo, maxlength, fonte, expr, destino,
                 largura, nota):
        self.formulario = formulario
        self.campo = campo
        self.maxlength = maxlength
        self.fonte = fonte
        self.expr = expr
        self.destino = destino
        self.largura = largura
        self.nota = nota


def offsets_do_core() -> dict[int, str]:
    """valor -> nome do `OFS_*`, lido do Pascal gerado do `we2002_core`."""
    fora: dict[int, str] = {}
    for m in re.finditer(r"^\s*(OFS_\w+)\s*=\s*(\d+);",
                         OFFSETS_PAS.read_text(encoding="utf-8"), re.M):
        fora.setdefault(int(m.group(2)), m.group(1))
    if not fora:
        raise DumpError(f"{OFFSETS_PAS}: nenhum OFS_* lido")
    return fora


def tabela_de_comprimento(nome: str) -> list[int]:
    """A tabela `<nome>: array[0..N] of ShortInt` do `we2002_tables.pas`."""
    texto = TABELAS_PAS.read_text(encoding="utf-8")
    m = re.search(rf"^\s*{nome}:\s*array\[0\.\.(\d+)\] of ShortInt\s*=\s*"
                  r"\((.*?)\);", texto, re.S | re.M)
    if not m:
        raise DumpError(f"{TABELAS_PAS}: tabela `{nome}` nao encontrada")
    valores = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    if len(valores) != int(m.group(1)) + 1:
        raise DumpError(
            f"{TABELAS_PAS}: `{nome}` declara {int(m.group(1)) + 1} entradas e "
            f"tem {len(valores)}")
    return valores


def lote_do_operando(pe: PE, endereco: int) -> tuple[int, int, int]:
    """(`linha`, `coluna`, offset do lote) do campo `+4` que o operando aponta.

    Aborta se o endereco nao cair EXATAMENTE num campo `+4`: um operando que
    caia no meio de uma entrada significa que o modelo da tabela esta errado, e
    seguir daria um lote plausivel e falso.
    """
    d = endereco - (BASE_DAS_MEDIDAS + CAMPO_LARGURA)
    if d < 0:
        raise DumpError(
            f"{REL_EXE}: operando {endereco:#010x} antes de "
            f"{BASE_DAS_MEDIDAS + CAMPO_LARGURA:#010x}, a primeira largura")
    linha, resto = divmod(d, PASSO_LINHA)
    coluna, sobra = divmod(resto, PASSO_COLUNA)
    if sobra or linha >= LOTE_LINHAS or coluna >= LOTE_COLUNAS:
        raise DumpError(
            f"{REL_EXE}: operando {endereco:#010x} nao e o campo `+4` de uma "
            f"entrada de {BASE_DAS_MEDIDAS:#010x} "
            f"(linha {linha}, coluna {coluna}, sobra {sobra})")
    offset = pe.dword(TABELA_DE_LOTES + (linha * LOTE_COLUNAS + coluna) * 4)
    if offset == 0:
        raise DumpError(
            f"{REL_EXE}: a entrada [{linha}][{coluna}] de "
            f"{TABELA_DE_LOTES:#010x} e zero -- o operando {endereco:#010x} "
            f"aponta para um buraco da tabela")
    return linha, coluna, offset


def monta() -> list[Linha]:
    pe = PE(EXE.read_bytes(), REL_EXE)
    mapa = campos()
    dfm = maxlength_dos_dfm()
    thunk = thunk_de(pe, SETMAXLENGTH)
    linhas: list[Linha] = []
    vistos: set[tuple[str, str]] = set()

    _ini_va, o_ini, _tam = faixa(pe)
    for o_call in sitios(pe, thunk):
        va_call = _ini_va + (o_call - o_ini)
        formulario, disp = alvo_do_sitio(pe, o_call)
        campo = mapa.get((formulario, disp))
        if campo is None:
            raise DumpError(
                f"{REL_EXE}: {formulario}+{disp:#x} nao esta no campos.tsv")
        forma, operando = expressao(pe, o_call)

        if campo not in DESTINOS:
            raise DumpError(
                f"{GERADOR}: `{campo}` recebe SetMaxLength e nao aparece em "
                f"DESTINOS -- declare o destino")
        declarado = DESTINOS[campo]

        if forma == "metade":
            texto = f"[{operando:#010x}] div 2"
        elif forma == "menos_um":
            texto = f"[{operando:#010x}] - 1"
        else:
            texto = str(operando)

        nota = ""
        if campo in POR_TIME:
            # O caminho POR TIME. Duas conferencias, e a primeira e a que
            # faltava: o operando e decodificado ate a entrada de
            # `0x004231a0`, e o offset que esta la tem de ser o `OFS_*`
            # declarado. Isso PROVA o lote; a aritmetica sozinha nunca provou.
            ofs_esperado, nome_da_tabela = declarado
            linha, coluna, offset = lote_do_operando(pe, operando)
            ofs_lido = offsets_do_core().get(offset)
            if ofs_lido != ofs_esperado:
                raise DumpError(
                    f"{REL_EXE}: `{campo}` le [{operando:#010x}] = a largura do "
                    f"lote [{linha}][{coluna}] de {TABELA_DE_LOTES:#010x}, que "
                    f"vale {offset} ({ofs_lido or 'nenhum OFS_* do core'}); "
                    f"DESTINOS declara {ofs_esperado}")
            tab = tabela_de_comprimento(nome_da_tabela)
            # A segunda conferencia: a forma da expressao tem de casar com o
            # que a tabela conta. `div 2` so faz sentido num lote de dois bytes
            # por caractere -- e e o kanji que tem `*2` no `Load` do core.
            dois_bytes = "KANJI" in nome_da_tabela
            if (forma == "metade") != dois_bytes:
                raise DumpError(
                    f"{REL_EXE}: `{campo}` usa a forma `{forma}` sobre "
                    f"`{nome_da_tabela}`; `metade` so vale para lote de dois "
                    f"bytes por caractere")
            # O lote kanji guarda a largura MENOS UM -- ver
            # LOTE_COM_DECREMENTO. Como a largura e `LEN*2`, `div 2` do valor
            # decrementado da `LEN - 1`.
            decrementa = ofs_esperado in LOTE_COM_DECREMENTO
            def limite(n: int) -> int:
                if forma == "metade":
                    return n - 1 if decrementa else n
                return n - 1
            if decrementa and forma != "metade":
                raise DumpError(
                    f"{GERADOR}: `{campo}` le o lote {ofs_esperado}, que o "
                    f"original decrementa, mas a expressao e `{forma}` e nao "
                    f"`metade` -- o decremento so foi medido no caminho do "
                    f"`div 2`")
            valor = limite(tab[TIME_DE_REFERENCIA])
            nome_do_campo, largura = nome_da_tabela, len(tab)
            faixa_min, faixa_max = limite(min(tab)), limite(max(tab))
            extra = (" A largura desse lote e guardada **menos um** "
                     f"(`dec` em `0x00403d95`, so para "
                     f"`{TABELA_DE_LOTES:#010x}`[0][0]), logo o limite e "
                     f"`{nome_da_tabela} - 1`." if decrementa else "")
            nota = (f"**por time** -- a largura e remedida a cada troca de "
                    f"time, do lote {ofs_esperado} "
                    f"(`{TABELA_DE_LOTES:#010x}`[{linha}][{coluna}]); "
                    f"{faixa_min}..{faixa_max} nos 95, e {valor} no time "
                    f"{TIME_DE_REFERENCIA}, que e o do `compara_tela.sh "
                    f"--nomes`.{extra}")
        else:
            rel, nome_do_campo = declarado
            largura = largura_do_destino(rel, nome_do_campo)
            valor = (largura // 2 if forma == "metade"
                     else largura - 1 if forma == "menos_um" else operando)
            if forma == "literal" and valor != largura - 1:
                raise DumpError(
                    f"{REL_EXE}: `{campo}` recebe o literal {valor} e o destino "
                    f"`{nome_do_campo}` tem {largura} bytes; esperava "
                    f"{largura - 1}")

        if (formulario, campo) in dfm:
            aviso = (f"o `.dfm` declara {dfm[(formulario, campo)]} e o código "
                     f"reafirma o mesmo em tempo de execução")
            nota = f"{nota}; {aviso}" if nota else aviso
        linhas.append(Linha(formulario, campo, valor,
                            f"código, `{va_call:#010x}`",
                            texto, nome_do_campo, largura, nota))
        vistos.add((formulario, campo))

    for (formulario, campo), valor in sorted(dfm.items()):
        if (formulario, campo) in vistos:
            continue
        rel_nome = DESTINOS.get(campo)
        destino, largura = "", 0
        if rel_nome:
            destino = rel_nome[1]
            largura = largura_do_destino(*rel_nome)
        linhas.append(Linha(formulario, campo, valor, "dfm", str(valor),
                            destino, largura, SEM_GOVERNO.get(campo, "")))

    if not linhas:
        raise DumpError(f"{REL_EXE}: nenhum campo com limite encontrado")
    return sorted(linhas, key=lambda l: (l.formulario, l.campo))


def tsv(linhas: list[Linha]) -> str:
    fora = ["formulario\tcampo\tmaxlength\tfonte\texpressao\tdestino"
            "\tlargura_do_destino\tnota"]
    for l in linhas:
        fora.append(f"{l.formulario}\t{l.campo}\t{l.maxlength}\t{l.fonte}\t"
                    f"{l.expr}\t{l.destino}\t{l.largura or ''}\t{l.nota}")
    return "\n".join(fora) + "\n"


def md(linhas: list[Linha]) -> str:
    do_codigo = [l for l in linhas if l.fonte.startswith("código")]
    do_dfm = [l for l in linhas if l.fonte == "dfm"]
    fora = [
        "# `re/truncamento.md` — onde cada campo editável corta o texto",
        "",
        "Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md), o",
        "critério *comportamento de truncamento documentado por campo*. Gerado",
        "por [`../tools/dump_truncamento.py`](../tools/dump_truncamento.py).",
        f"**Não editar à mão.** A tabela está em [`{TSV_NAME}`]({TSV_NAME}).",
        "",
        "## O limite não está num lugar só",
        "",
        f"São **{len(linhas)} campos** com limite declarado: {len(do_dfm)} o trazem",
        f"do `.dfm` e {len(do_codigo)} o recebem em tempo de execução, por",
        "`TCustomEdit::SetMaxLength`. Ler só uma das fontes acha parte e **não",
        "anuncia** que há outra.",
        "",
        "Dos que vêm do código, **nenhum é literal puro**: dois são expressão",
        "sobre uma largura **medida em tempo de execução**, e a expressão tem",
        "motivo.",
        "",
        "| Formulário | Campo | `MaxLength` | Fonte | Expressão | Destino | Largura |",
        "|---|---|--:|---|---|---|--:|",
    ]
    for l in linhas:
        destino = f"`{l.destino}`" if l.destino else "—"
        largura = str(l.largura) if l.largura else "—"
        fora.append(f"| `{l.formulario}` | `{l.campo}` | {l.maxlength} | "
                    f"{l.fonte} | `{l.expr}` | {destino} | {largura} |")
    fora += [
        "",
        "## A conferência, e por que ela vale",
        "",
        "As duas linhas de código **não medem a mesma coisa** que as do `.dfm`,",
        "e tratá-las como se medissem custou duas divergências seguidas.",
        "",
        "`lista_equiposChange` percorre uma tabela de **lotes** em",
        "`0x004231a0` — 3 linhas × 6 colunas de offset, e 11 das 18 entradas",
        "são não-zero. Para cada uma ela **anda pelo arquivo** até o registro do",
        "time selecionado, pulando o rodapé de cada setor MODE2/2352, e grava",
        "três campos em `0x00433a0c`: o offset do registro, a **largura** dele",
        "em bytes, e os próprios bytes. O passo é 312 por linha e 52 por",
        "coluna.",
        "",
        "Logo `[0x00433a10]` é a largura da linha 0 coluna 0 e `[0x00433b48]` a",
        "da linha 1 coluna 0. **Não são constantes** — são remedidas a cada",
        "troca de time, e é por isso que nenhum número fixo estava certo:",
        "",
        "```text",
        "0x004231a0[0][0] = 2002316 = OFS_TEAM_NAME_KANJI -> TEAM_NAME_KANJI_LEN",
        "0x004231a0[1][0] = 2003996 = OFS_TEAM_NAME_3     -> TEAM_NAME_LEN_3",
        "```",
        "",
        "**O gerador prova esse mapeamento, e é isso que faltava.** Ele",
        "decodifica o endereço do operando até a entrada de `0x004231a0`, lê o",
        "offset que está lá, e aborta se ele não for o `OFS_*` que a tabela",
        "`DESTINOS` declara. Também confere a forma: `div 2` só vale para lote",
        "de dois bytes por caractere, que é o kanji — o `Load` do",
        "`we2002_core` lê `TEAM_NAME_KANJI_LEN[t]*2` bytes ali, e",
        "`TEAM_NAME_LEN_3[t]` no outro.",
        "",
        "**A conferência antiga batia a aritmética contra uma largura escrita à",
        "mão, e por isso passou com o campo errado — duas vezes.** A primeira",
        "versão declarou `raw_kanji_name` (40 bytes, `div 2` = 20) e a conta",
        "fechou. O `compara_tela.sh --nomes` então mostrou o oráculo cortando",
        "em cinco caracteres, e a segunda versão trocou 20 por um literal 5 —",
        "que também estava errado, porque o limite é **por time**.",
        "",
        "## O `dec` que faltava, e ele explica as duas versões erradas",
        "",
        "`0x00403c0c` termina com um caso especial que vale **só** para a linha",
        "0 coluna 0 — o lote kanji:",
        "",
        "```text",
        "0x00403d59  test edi,edi        ' linha == 0 ?",
        "0x00403d6e  cmp [ebp-4],0       ' coluna == 0 ?",
        "0x00403d95  dec  [0x00433a10 + linha*312 + coluna*52]",
        "0x00403d98  mov  [0x00433a14 + ...], 1",
        "```",
        "",
        "**O lote kanji guarda a largura menos um**, e o campo `+8` recebe `1`",
        "em vez do `2` que todos os outros recebem — esse `+8` é o modo do",
        "decodificador de texto (`0x00403598` compara com `0x82`, o byte-líder",
        "Shift-JIS): 1 = dois bytes por caractere, 2 = um byte.",
        "",
        "Sem esse `dec`, `div 2` dá **um a mais**, e foi ele que sustentou as",
        "duas versões erradas: a conta não fechava com nenhum campo do formato",
        "porque a largura guardada não era a largura medida.",
        "",
        "Medido em 2026-08-18 dirigindo o oráculo em **três** times de larguras",
        "diferentes, digitando `ABCDEFGHIJKLMNOP` no `edit_nombre1`:",
        "",
        "| time | `TEAM_NAME_KANJI_LEN` | o oráculo mostra | |",
        "|--:|--:|---|--:|",
        "| 2 | 6 | `ABCDE` | 5 |",
        "| 0 | 8 | `ABCDEFG` | 7 |",
        "| 56 | 14 | `ABCDEFGHIJKLM` | 13 |",
        "",
        "A diferença é **constante em 1**, não proporcional — o que descarta",
        "erro de escala e aponta um decremento. `(largura − 1) div 2` fecha nos",
        "três, e sobre a imagem japonesa isso é `TEAM_NAME_KANJI_LEN − 1` em",
        "**95/95** times.",
        "",
        "Emulada a travessia do original sobre as duas imagens, a largura",
        "medida bate com a tabela do `we2002_core` em **95/95** times para os",
        "dois lotes na imagem japonesa. Na European Deluxe o lote kanji bate em",
        "46/95 — nomes latinos foram escritos em slot de kanji e deixaram lixo",
        "depois do terminador, então a distância ao próximo registro encurta.",
        "É comportamento do original com aquela imagem, não defeito do port.",
        "",
        "## Onde as duas fontes se sobrepõem",
        "",
    ]
    sobrepostos = [l for l in linhas if l.fonte.startswith("código") and l.nota]
    if sobrepostos:
        for l in sobrepostos:
            fora.append(f"- **`{l.formulario}.{l.campo}`** — {l.nota}.")
        fora += [
            "",
            "Concordam, e é por isso que aparece um só. Se um dia discordarem, o",
            "que vale é o código: `SetMaxLength` roda depois de o formulário ser",
            "construído e sobrescreve o que o `.dfm` pediu.",
            "",
        ]
    else:
        fora += ["Nenhum campo aparece nas duas fontes.", ""]
    fora += [
        "## O campo cujo `MaxLength` não governa nada",
        "",
    ]
    for l in linhas:
        if l.campo in SEM_GOVERNO:
            fora.append(f"- **`{l.formulario}.{l.campo}`** — {l.nota}.")
    fora += [
        "",
        "Registrado porque o número é **verdadeiro e irrelevante**: portar \"o",
        "campo corta em 10\" copiaria uma medição correta para o lugar errado.",
        "",
    ]
    return "\n".join(fora)


def gera() -> dict[Path, str]:
    if not EXE.exists():
        raise DumpError(
            f"{REL_EXE} nao esta no disco. A pasta e do usuario e nao entra no "
            f"repositorio -- ver o CLAUDE.md.")
    linhas = monta()
    return {OUT / TSV_NAME: tsv(linhas), OUT / MD_NAME: md(linhas)}


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de dump_truncamento.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    return 0


def do_write(files: dict[Path, str]) -> int:
    for caminho, conteudo in sorted(files.items()):
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
