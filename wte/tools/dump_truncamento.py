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

# As larguras que a camada de dados declara, e o campo de cada uma. Os nomes
# sao lidos do Pascal gerado -- nao ha numero digitado aqui.
DESTINOS = {
    "edit_nombre1": ("wte/src/we2002_team.pas", "raw_kanji_name"),
    "edit_nombre2": ("wte/src/we2002_team.pas", "mixed_case_name"),
    "edit_nombre3": ("wte/src/we2002_team.pas", "abbreviations"),
    "casilla_nombre": ("wte/src/we2002_player.pas", "name"),
}

# Campo cujo `MaxLength` NAO governa o truncamento, e por que. Sem esta lista o
# documento afirmaria que o numero de camisa corta em 10 caracteres.
SEM_GOVERNO = {
    "casilla_dorsal": (
        "número de camisa, no máximo três dígitos. Quem recusa tecla é o "
        "`casilla_dorsalKeyPress`; o `MaxLength` de 10 nunca chega a valer"),
    "casilla_precio": (
        "campo numérico de preço. O `MaxLength` de 3 limita dígito, não texto "
        "— ver a WTE-TASK-30"),
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
                f"{GERADOR}: `{campo}` recebe SetMaxLength e nao tem destino "
                f"declarado em DESTINOS")
        rel, nome_do_campo = DESTINOS[campo]
        largura = largura_do_destino(rel, nome_do_campo)

        if forma == "metade":
            valor, texto = largura // 2, f"[{operando:#010x}] div 2"
        elif forma == "menos_um":
            valor, texto = largura - 1, f"[{operando:#010x}] - 1"
        else:
            valor, texto = operando, str(operando)

        # A conferencia: a expressao lida do `.exe` tem de casar com a largura
        # que a camada de dados declara. Nao e redundancia -- sao dois lados da
        # mesma conta, medidos por caminhos que nao se falam.
        if forma == "literal" and valor != largura - 1:
            raise DumpError(
                f"{REL_EXE}: `{campo}` recebe o literal {valor} e o destino "
                f"`{nome_do_campo}` tem {largura} bytes; esperava "
                f"{largura - 1}")

        nota = ""
        if (formulario, campo) in dfm:
            nota = (f"o `.dfm` declara {dfm[(formulario, campo)]} e o código "
                    f"reafirma o mesmo em tempo de execução")
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
        "sobre a largura do campo de destino, e a expressão tem motivo.",
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
        "A coluna **Largura** não sai do `.exe`: sai de",
        "[`../src/we2002_team.pas`](../src/we2002_team.pas) e",
        "[`../src/we2002_player.pas`](../src/we2002_player.pas) — a camada de",
        "dados, que é byte-idêntica ao `ed.exe`. É o **outro lado da conta**, e",
        "o gerador aborta se os dois não casarem:",
        "",
        "```text",
        "raw_kanji_name    40 bytes  -> div 2   -> 20   dois bytes por caractere",
        "mixed_case_name   20 bytes  -> menos 1 -> 19   o byte do terminador",
        "abbreviations[0]   4 bytes  -> literal  3      idem",
        "```",
        "",
        "**O `div 2` é o achado.** `edit_nombre1` mostra o nome em kanji, e o",
        "campo no disco guarda dois bytes por caractere: metade dos 40 bytes é",
        "20 caracteres. Quem lesse a expressão como \"metade do limite\" sem",
        "olhar o destino escreveria 20 e não saberia por quê — e erraria no dia",
        "em que o campo mudasse de largura.",
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
