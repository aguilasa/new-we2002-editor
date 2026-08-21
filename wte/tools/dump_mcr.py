#!/usr/bin/env python3
"""O `.mcr` do WE2002: o conteiner pela documentacao publica, o bloco pelo `.exe`.

Gera `wte/re/mcr.md` e `wte/re/mcr.tsv` -- insumo da
[WTE-TASK-28](../../docs/tasks/28-import-de-mcr.md).

    python3 wte/tools/dump_mcr.py           # regera as duas saidas
    python3 wte/tools/dump_mcr.py --check   # o que `make -C wte check` roda

## A divisao que o enunciado da task manda fazer

**Conteiner pela documentacao publica, conteudo por engenharia reversa.** O
memory card do PSX e formato documentado -- 16 blocos de 8192 bytes, o bloco 0
sendo cabecalho mais diretorio de 15 quadros de 128 bytes. O que NAO e publico e
o que o WE2002 guarda dentro do bloco dele, e isso sai do `.exe`.

Este script nao *supoe* o conteiner: ele **le** o diretorio do molde
(`we-team-editor/data/dat.bin`, primeira metade) e emite o que achou. Se o molde
mudar, o markdown muda junto.

## As duas metades do `dat.bin`

145.408 bytes, e nao 131.072. A primeira metade e um cartao formatado com o
save do WE2002 dentro -- e o molde que o `grabar_memoryClick` copia inteiro
antes de escrever por cima. Os 14.336 restantes sao os sete setores que a
abertura da imagem injeta, ja descritos na secao 8 do `assets.md`.

## O achado que este script existe para nao deixar passar

**O editor grava a maior parte dos destinos num bloco que o proprio diretorio do
cartao declara LIVRE.** O save diz ocupar 16.384 bytes -- os blocos 1 e 2 --, e
formacao, tatica e cobradores caem todos no bloco 3, que o molde entrega zerado
e marcado `0xA0`. Jogadores e numeros de camisa, esses sim, caem no bloco 2.

O readme do original registra que a v0.98 consertou *"the problem with the
captain and kickers when loading from .mcr files"* -- e capitao e cobradores sao
exatamente campos do bloco 3. O script mede a coincidencia e a deixa escrita; o
veredito e da task.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GERADOR = "wte/tools/dump_mcr.py"

EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
DAT = ROOT / "we-team-editor" / "data" / "dat.bin"
REL_EXE = "we-team-editor/we-team-editor.exe"
REL_DAT = "we-team-editor/data/dat.bin"

OUT_MD = ROOT / "wte" / "re" / "mcr.md"
OUT_TSV = ROOT / "wte" / "re" / "mcr.tsv"
MEDIDO = ROOT / "wte" / "re" / "mcr-medido.tsv"
IDA_E_VOLTA = ROOT / "wte" / "re" / "mcr-roundtrip.tsv"
PASCAL = ROOT / "wte" / "src" / "we2002_mcr.pas"
REL_PASCAL = "wte/src/we2002_mcr.pas"
AUX = ROOT / "wte" / "src" / "impl" / "ep2002_mainform.aux.inc"
REL_AUX = "wte/src/impl/ep2002_mainform.aux.inc"

# --- o conteiner, pela documentacao publica -------------------------------
CARTAO_BYTES = 0x20000       # 131.072 = 16 blocos
BLOCO_BYTES = 8192
QUADRO_BYTES = 128
QUADROS_DE_DIRETORIO = 15    # o quadro 0 e o cabecalho `MC`

# Os codigos de estado do quadro de diretorio. Documentacao publica do formato
# (nocash PSX spec, "Memory Card Data Format"): o nibble alto separa livre de
# em uso, o baixo diz a posicao na cadeia.
ESTADOS = {
    0x51: "em uso, primeiro bloco da cadeia",
    0x52: "em uso, bloco do meio",
    0x53: "em uso, ultimo bloco da cadeia",
    0xA0: "livre (formatado)",
    0xA1: "livre (era o primeiro de uma cadeia apagada)",
    0xA2: "livre (era do meio)",
    0xA3: "livre (era o ultimo)",
    0xFF: "sem uso",
}

# --- o conteudo, lido do `.exe` -------------------------------------------
# Endereco no cartao -> (campo, bytes, quem escreve, quem le).
# As colunas "escreve"/"le" sao os dois lados medidos: o `0x0040f150` do
# `grabar_memoryClick` e o `0x0040b9ec` que o `boton_mcrClick` chama.
LAYOUT = [
    (0x5404, "numeros de camisa, 23 x 5 bits", 16, "0x0040f5c9", "0x0040baa9"),
    (0x5904, "jogador j: 12 B de atributo (passo 32)", 12 * 23, "0x0040f2fe",
     "0x0040ba55"),
    (0x5910, "jogador j: 10 B de nome (passo 32)", 10 * 23, "0x0040f2fe",
     "0x0040ba01"),
    (0x6102, "tatica byte 0, mais 50", 1, "0x0040f36d", "-"),
    (0x6113, "cobrador 3", 1, "0x0040f4a2", "0x0040bb40"),
    (0x6122, "cobrador 2", 1, "0x0040f4a2", "0x0040bb40"),
    (0x6131, "cobrador 4", 1, "0x0040f4a2", "0x0040bb40"),
    (0x6140, "cobrador 1", 1, "0x0040f4a2", "0x0040bb40"),
    (0x614F, "cobrador 0", 1, "0x0040f4a2", "0x0040bb40"),
    (0x62A8, "formacao, bytes 10..29", 20, "0x0040f21d", "0x0040bb07"),
    (0x63D5, "formacao, bytes 0..9", 10, "0x0040f21d", "0x0040bad9"),
    (0x6479, "tatica byte 1, nibble alto", 1, "0x0040f43a", "-"),
    (0x6488, "tatica byte 1, nibble baixo", 1, "0x0040f40a", "-"),
    (0x6497, "tatica byte 2, nibble baixo", 1, "0x0040f3d8", "-"),
    (0x64A6, "tatica byte 2, nibble alto", 1, "0x0040f3a6", "-"),
    (0x64E2, "tatica byte 0, cru", 1, "0x0040f33d", "-"),
    (0x6500, "cobrador 5 (o capitao)", 1, "0x0040f4f8", "0x0040bb68"),
]

VA_TABELA_COBRADORES = 0x00423F84   # 5 DWORDs: os destinos de cobrador
VA_TABELA_BITS = 0x0042360C         # 6 DWORDs: o bit dentro do byte
COBRADORES_ESPERADOS = (0x614F, 0x6140, 0x6122, 0x6113, 0x6131)
BITS_ESPERADOS = (0, 5, 2, 7, 4, 1)

# --- o carregador de buffer, e o que ele carimba -------------------------
# `0x0040478c` enche um buffer de jogador a partir do `.mcr`. Alem dos dois
# `fread` (nome e atributos), ele CARIMBA tres campos com literal, e um deles e
# a correcao do "goleiro da Eire" do readme -- ver a secao dos casos especiais
# no markdown. Estes enderecos sao lidos do `.exe`, nao supostos.
VA_CARREGA_DO_CARTAO = 0x0040478C
VA_CARREGA_FIM = 0x00404820          # onde a `GravaJogador` comeca
VA_BUFFER_JOGADOR = 0x004335EC       # o vetor de buffers, +0 do registro 0
BUFFER_PASSO = 44                    # `ebx*11*4` nas tres contas de indice

# deslocamento no registro -> quantos bytes o `fread` traz
CARTAO_CAMPOS_ESPERADOS = {0x00: 10, 0x0A: 12}
# deslocamento no registro -> o literal carimbado (`mov BYTE PTR [..],imm8`)
CARTAO_MARCAS_ESPERADAS = {0x16: 0xFF, 0x18: 0x19, 0x19: 0x03}
# e o nome da constante Pascal que tem de valer o mesmo, no `.aux.inc`
CARTAO_MARCAS_PASCAL = {0x16: "IDENT_NENHUMA", 0x18: "CARTAO_CONDICIONAL",
                        0x19: "TIPO_SOLTO"}
# as tres atribuicoes que `CarregaJogadorDoCartao` tem de fazer
CARTAO_ATRIBUICOES = {0x16: "ident_time", 0x18: "condicional", 0x19: "tipo"}


class McrError(Exception):
    pass


def secoes(blob: bytes):
    pe = struct.unpack_from("<I", blob, 0x3C)[0]
    n_sec, = struct.unpack_from("<H", blob, pe + 6)
    tam_opt, = struct.unpack_from("<H", blob, pe + 20)
    base = pe + 24 + tam_opt
    for i in range(n_sec):
        cab = base + 40 * i
        vsize, va, rsize, roff = struct.unpack_from("<IIII", blob, cab + 8)
        yield va, max(vsize, rsize), roff


def le_bytes(blob: bytes, va: int, quantos: int) -> bytes:
    for sec_va, tam, roff in secoes(blob):
        ini = 0x00400000 + sec_va
        if ini <= va and va + quantos <= ini + tam:
            return blob[roff + (va - ini):roff + (va - ini) + quantos]
    raise McrError(f"{REL_EXE}: VA {va:#x}+{quantos} fora de toda secao")


def carimbos_do_carregador(blob: bytes) -> tuple[dict[int, int], dict[int, int]]:
    """O que a `0x0040478c` escreve no buffer, lido do `.text`.

    Devolve dois mapas, os dois indexados pelo DESLOCAMENTO no registro de
    jogador de 44 bytes:

    - os campos que vem do arquivo, com quantos bytes cada `fread` traz. O
      destino sai de um `add reg,imm32` que cai dentro do registro
      (`81 c1`/`81 c2`), e o tamanho do `push imm8` que o antecede;
    - os campos CARIMBADOS com literal, de `mov BYTE PTR [eax*4+disp],imm8`
      (`c6 04 85`), que e a forma que o compilador da Borland usou para
      `buffer[b].campo = <constante>`.

    Os carimbos sao o assunto: um deles (`+0x16 := 0xFF`) e o que faz o import
    funcionar no time 0 slot 0 -- ver a secao dos casos especiais.
    """
    corpo = le_bytes(blob, VA_CARREGA_DO_CARTAO,
                     VA_CARREGA_FIM - VA_CARREGA_DO_CARTAO)
    campos: dict[int, int] = {}
    marcas: dict[int, int] = {}
    i = 0
    ultimo_push = None
    while i < len(corpo) - 5:
        if corpo[i] == 0x6A:                       # push imm8
            ultimo_push = corpo[i + 1]
            i += 2
            continue
        if corpo[i] == 0x81 and corpo[i + 1] in (0xC1, 0xC2):   # add ecx/edx
            disp = int.from_bytes(corpo[i + 2:i + 6], "little")
            if VA_BUFFER_JOGADOR <= disp < VA_BUFFER_JOGADOR + BUFFER_PASSO:
                campos[disp - VA_BUFFER_JOGADOR] = ultimo_push
            i += 6
            continue
        if corpo[i:i + 3] == b"\xc6\x04\x85":      # mov BYTE [eax*4+d],imm8
            disp = int.from_bytes(corpo[i + 3:i + 7], "little")
            if VA_BUFFER_JOGADOR <= disp < VA_BUFFER_JOGADOR + BUFFER_PASSO:
                marcas[disp - VA_BUFFER_JOGADOR] = corpo[i + 7]
            i += 8
            continue
        i += 1
    return campos, marcas


def le_dwords(blob: bytes, va: int, quantos: int) -> tuple[int, ...]:
    for sec_va, tam, roff in secoes(blob):
        ini = 0x00400000 + sec_va
        if ini <= va < ini + tam:
            return struct.unpack_from(f"<{quantos}I", blob, roff + (va - ini))
    raise McrError(f"{REL_EXE}: VA {va:#x} fora de toda secao")


# Nome da constante Pascal -> endereco que o layout aqui diz. O `we2002_mcr`
# e escrito a mao (com a prosa que a leitura do disassembly produziu), e esta
# tabela e o que impede as duas verdades de se separarem: o `--check` le o
# Pascal e compara. E o mesmo contrato do `check_lcl_props.py` -- confere o que
# nao gera.
CONSTANTES_PASCAL = {
    "MCR_NUMEROS": 0x5404,
    "MCR_JOGADORES": 0x5904,
    "MCR_JOGADOR_PASSO": 32,
    "MCR_FORMACAO_1": 0x63D5,
    "MCR_FORMACAO_2": 0x62A8,
    "MCR_TATICA_CRUA": 0x64E2,
    "MCR_TATICA_MAIS50": 0x6102,
    "MCR_TATICA_1_BAIXO": 0x6488,
    "MCR_TATICA_1_ALTO": 0x6479,
    "MCR_TATICA_2_BAIXO": 0x6497,
    "MCR_TATICA_2_ALTO": 0x64A6,
    "MCR_CAPITAO": 0x6500,
    "CARTAO_BYTES": CARTAO_BYTES,
    "CARTAO_BLOCO": BLOCO_BYTES,
}


def constantes_do_pascal() -> dict[str, int]:
    """As constantes de `we2002_mcr.pas`, lidas do fonte.

    So `NOME = $HEX;` ou `NOME = decimal;` na secao `const` -- e o bastante
    para o que esta tabela cobre, e recusar o resto e melhor do que aceitar uma
    expressao e avaliar errado.
    """
    if not PASCAL.is_file():
        raise McrError(f"{REL_PASCAL} nao existe")
    achados: dict[str, int] = {}
    for linha in PASCAL.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(\$[0-9A-Fa-f]+|\d+)\s*;",
                     linha)
        if m:
            achados[m.group(1)] = (int(m.group(2)[1:], 16)
                                   if m.group(2).startswith("$")
                                   else int(m.group(2)))
    return achados


def cobradores_do_pascal() -> tuple[int, ...]:
    m = re.search(r"MCR_COBRADORES:[^=]*=\s*\(([^)]*)\)",
                  PASCAL.read_text(encoding="utf-8"))
    if not m:
        raise McrError(f"{REL_PASCAL}: MCR_COBRADORES nao encontrado")
    return tuple(int(x.strip()[1:], 16) for x in m.group(1).split(","))


def confere_pascal(cob: tuple[int, ...]) -> None:
    achados = constantes_do_pascal()
    ruins = []
    for nome, esperado in CONSTANTES_PASCAL.items():
        if nome not in achados:
            ruins.append(f"{nome}: ausente")
        elif achados[nome] != esperado:
            ruins.append(f"{nome}: Pascal diz {achados[nome]:#x}, o layout diz "
                         f"{esperado:#x}")
    no_pascal = cobradores_do_pascal()
    if no_pascal != cob:
        ruins.append(f"MCR_COBRADORES: Pascal diz "
                     f"{[hex(x) for x in no_pascal]}, o `.exe` diz "
                     f"{[hex(x) for x in cob]}")
    if ruins:
        raise McrError(
            f"{REL_PASCAL} e o layout deste gerador divergem:\n     "
            + "\n     ".join(ruins))


def primeiro_time() -> str:
    """O nome do time de indice 0, do `we2002_core`.

    Lido, e nao afirmado: o caso do "goleiro da Eire" so faz sentido se o item
    0 do combo for mesmo a Irlanda, e a tabela do `newWe2002` -- que ja e
    byte-identica ao `ed.exe` -- e quem diz.
    """
    tabelas = ROOT / "src" / "core" / "Tables.cpp"
    if not tabelas.is_file():
        raise McrError("src/core/Tables.cpp nao existe")
    texto = tabelas.read_text(encoding="utf-8")
    i = texto.find("const char TEAM_NAMES[120][20]")
    if i < 0:
        raise McrError("src/core/Tables.cpp: TEAM_NAMES nao encontrada")
    m = re.search(r'"([^"]*)"', texto[i:])
    if not m:
        raise McrError("src/core/Tables.cpp: TEAM_NAMES sem primeira entrada")
    return m.group(1)


def corpo_do_carrega_jogador() -> str:
    """O corpo de `CarregaJogadorDoCartao`, do `.aux.inc`.

    Recorta da assinatura ate o `end;` da rotina. E texto, e de proposito: o
    que se confere aqui e que as tres atribuicoes ESTAO LA, nao o que elas
    calculam -- isso quem julga e o golden.
    """
    if not AUX.is_file():
        raise McrError(f"{REL_AUX} nao existe")
    texto = AUX.read_text(encoding="utf-8")
    i = texto.find("procedure CarregaJogadorDoCartao")
    if i < 0:
        raise McrError(f"{REL_AUX}: CarregaJogadorDoCartao nao encontrada")
    j = texto.find("\nend;", i)
    if j < 0:
        raise McrError(f"{REL_AUX}: CarregaJogadorDoCartao sem fim")
    return texto[i:j]


def constantes_do_aux() -> dict[str, int]:
    if not AUX.is_file():
        raise McrError(f"{REL_AUX} nao existe")
    achados: dict[str, int] = {}
    for linha in AUX.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(\$[0-9A-Fa-f]+|\d+)\s*;",
                     linha)
        if m:
            achados.setdefault(m.group(1),
                               int(m.group(2)[1:], 16)
                               if m.group(2).startswith("$")
                               else int(m.group(2)))
    return achados


def confere_carregador(campos: dict[int, int], marcas: dict[int, int]) -> None:
    """O `.exe` contra o Pascal, no ponto em que o "goleiro da Eire" mora.

    Tres carimbos, e o do deslocamento `+0x16` e o que importa: sem ele o
    buffer vindo do cartao chegaria com identidade `(0, 0)`, que e exatamente
    a identidade do slot 0 do time 0. A `0x00404820` compara identidade e
    recusa jogador repetido -- e recusaria SO aquele slot, so naquele time.
    """
    ruins = []
    if campos != CARTAO_CAMPOS_ESPERADOS:
        ruins.append(f"os `fread` de {VA_CARREGA_DO_CARTAO:#x} trazem "
                     f"{ {hex(k): v for k, v in sorted(campos.items())} }, "
                     f"esperado "
                     f"{ {hex(k): v for k, v in CARTAO_CAMPOS_ESPERADOS.items()} }")
    if marcas != CARTAO_MARCAS_ESPERADAS:
        ruins.append(f"os carimbos de {VA_CARREGA_DO_CARTAO:#x} valem "
                     f"{ {hex(k): hex(v) for k, v in sorted(marcas.items())} }, "
                     f"esperado "
                     f"{ {hex(k): hex(v) for k, v in CARTAO_MARCAS_ESPERADAS.items()} }")
    do_pascal = constantes_do_pascal()
    do_aux = constantes_do_aux()
    for desl, valor in sorted(CARTAO_MARCAS_ESPERADAS.items()):
        nome = CARTAO_MARCAS_PASCAL[desl]
        if nome not in do_aux:
            ruins.append(f"{nome}: ausente de {REL_AUX}")
        elif do_aux[nome] != valor:
            ruins.append(f"{nome}: Pascal diz {do_aux[nome]:#x}, o `.exe` "
                         f"carimba {valor:#x} em +{desl:#04x}")
    corpo = corpo_do_carrega_jogador()
    for desl, campo in sorted(CARTAO_ATRIBUICOES.items()):
        nome = CARTAO_MARCAS_PASCAL[desl]
        if f"{campo} := {nome}" not in corpo:
            ruins.append(f"CarregaJogadorDoCartao nao faz `{campo} := {nome}`")
    for desl, quantos in sorted(CARTAO_CAMPOS_ESPERADOS.items()):
        nome = "MCR_NOME_BYTES" if desl == 0 else "MCR_ATRIBUTO_BYTES"
        if do_pascal.get(nome) != quantos:
            ruins.append(f"{nome}: Pascal diz {do_pascal.get(nome)}, o "
                         f"`fread` de +{desl:#04x} traz {quantos}")
        if nome not in corpo:
            ruins.append(f"CarregaJogadorDoCartao nao copia {nome} bytes")
    if ruins:
        raise McrError(
            "o carregador de buffer do `.exe` e o Pascal divergem:\n     "
            + "\n     ".join(ruins))


def diretorio(card: bytes) -> list[dict]:
    saida = []
    for i in range(1, QUADROS_DE_DIRETORIO + 1):
        q = card[i * QUADRO_BYTES:(i + 1) * QUADRO_BYTES]
        saida.append({
            "bloco": i,
            "estado": q[0],
            "tamanho": int.from_bytes(q[4:8], "little"),
            "link": int.from_bytes(q[8:10], "little"),
            "nome": q[10:30].split(b"\0")[0].decode("ascii", "replace"),
        })
    return saida


def blocos_do_save(dir_: list[dict]) -> list[int]:
    return [d["bloco"] for d in dir_ if d["estado"] in (0x51, 0x52, 0x53)]


def gera() -> dict[Path, str]:
    if not EXE.is_file():
        raise McrError(f"{REL_EXE} nao existe.")
    if not DAT.is_file():
        raise McrError(f"{REL_DAT} nao existe.")
    blob = EXE.read_bytes()
    dat = DAT.read_bytes()
    if dat[:2] != b"MC":
        raise McrError(f"{REL_DAT}: nao comeca com 'MC' -- nao e cartao")
    card = dat[:CARTAO_BYTES]

    cob = le_dwords(blob, VA_TABELA_COBRADORES, 5)
    if cob != COBRADORES_ESPERADOS:
        raise McrError(
            f"{REL_EXE}: a tabela de cobradores em {VA_TABELA_COBRADORES:#x} "
            f"vale {[hex(x) for x in cob]}, e o layout diz "
            f"{[hex(x) for x in COBRADORES_ESPERADOS]}. Uma das duas leituras "
            "esta errada -- nao emito layout que nao fecha.")
    bits = le_dwords(blob, VA_TABELA_BITS, 6)
    if bits != BITS_ESPERADOS:
        raise McrError(
            f"{REL_EXE}: a tabela de bits em {VA_TABELA_BITS:#x} vale {bits}, "
            f"esperado {BITS_ESPERADOS}")

    confere_pascal(cob)
    campos, marcas = carimbos_do_carregador(blob)
    confere_carregador(campos, marcas)

    dir_ = diretorio(card)
    usados = blocos_do_save(dir_)
    ocupados_por_dado = sorted({o // BLOCO_BYTES for o, _, _, _, _ in LAYOUT})
    fora = [b for b in ocupados_por_dado if b not in usados]

    nao_zero = {b: sum(1 for x in card[b * BLOCO_BYTES:(b + 1) * BLOCO_BYTES]
                       if x) for b in range(16)}

    return {OUT_TSV: gera_tsv(dir_, nao_zero),
            OUT_MD: gera_md(dat, card, dir_, usados, ocupados_por_dado, fora,
                            nao_zero, cob, bits, marcas)}


def gera_tsv(dir_: list[dict], nao_zero: dict[int, int]) -> str:
    out = ["secao\tchave\tvalor\tnota"]
    for d in dir_:
        out.append(f"diretorio\tbloco {d['bloco']}\t{d['estado']:#04x}\t"
                   f"{ESTADOS.get(d['estado'], 'desconhecido')}; "
                   f"tamanho={d['tamanho']}; link={d['link']:#06x}; "
                   f"nome={d['nome'] or '-'}")
    for b in range(16):
        out.append(f"molde\tbloco {b}\t{nao_zero[b]}\tbytes nao-zero de "
                   f"{BLOCO_BYTES}")
    for off, campo, tam, escreve, le in LAYOUT:
        out.append(f"layout\t{off:#06x}\t{tam}\t{campo}; bloco "
                   f"{off // BLOCO_BYTES}; escreve={escreve}; le={le}")
    return "\n".join(out) + "\n"


def gera_md(dat, card, dir_, usados, ocupados, fora, nao_zero, cob, bits,
            marcas) -> str:
    o = []
    w = o.append
    w("# O `.mcr` do WE2002 — contêiner e conteúdo\n")
    w(f"**GERADO** por [`dump_mcr.py`](../tools/dump_mcr.py) a partir de\n"
      f"`{REL_DAT}` e `{REL_EXE}`. Não edite a mão.\n")
    w("```sh\npython3 wte/tools/dump_mcr.py --check\n```\n")

    w("## A divisão, e por que ela poupa a maior parte do trabalho\n")
    w("**Contêiner pela documentação pública, conteúdo por engenharia\n"
      "reversa.** O memory card do PSX é formato documentado; o que o WE2002\n"
      "guarda dentro do bloco dele não é. Este documento lê o contêiner do\n"
      "molde e tira o conteúdo do `.exe` — nenhuma das duas metades é suposta.\n")

    w("## O molde: as duas metades do `dat.bin`\n")
    w(f"`{REL_DAT}` tem **{len(dat)}** bytes, e não os {CARTAO_BYTES} de um\n"
      "cartão. A primeira metade é um cartão formatado com o save do WE2002\n"
      f"dentro — o molde que o `grabar_memoryClick` copia inteiro antes de\n"
      f"escrever por cima. Os **{len(dat) - CARTAO_BYTES}** restantes são os\n"
      "sete setores que a abertura da imagem injeta, descritos na seção 8 do\n"
      "[`assets.md`](assets.md). Era a pergunta que o enunciado da\n"
      "[WTE-TASK-28](../../docs/tasks/28-import-de-mcr.md) mandava responder\n"
      "antes de usar o arquivo como fixture.\n")

    w("## O contêiner\n")
    w(f"{CARTAO_BYTES} bytes = 16 blocos de {BLOCO_BYTES}. O bloco 0 é\n"
      f"cabeçalho (`MC`) mais {QUADROS_DE_DIRETORIO} quadros de\n"
      f"{QUADRO_BYTES} bytes, um por bloco de save.\n")
    w("| bloco | estado | significado | tamanho | link | nome |\n"
      "|---:|---|---|---:|---|---|\n")
    for d in dir_:
        w(f"| {d['bloco']} | `{d['estado']:#04x}` | "
          f"{ESTADOS.get(d['estado'], '**desconhecido**')} | {d['tamanho']} | "
          f"`{d['link']:#06x}` | `{d['nome'] or '—'}` |\n")
    w(f"O save ocupa os blocos **{usados}** e se chama\n"
      f"`{dir_[0]['nome']}` — `SLPM-86600` é o *World Soccer Winning Eleven\n"
      "2002* japonês, o mesmo da ROM que o gate usa.\n")

    w("## O conteúdo do bloco do WE2002\n")
    w("Os dois lados foram medidos: quem escreve é o `0x0040f150` do\n"
      "`grabar_memoryClick`, quem lê é o `0x0040b9ec` que o `boton_mcrClick`\n"
      "chama. **Eles não são simétricos**, e a assimetria está na coluna `lê`.\n")
    w("| endereço | bloco | bytes | campo | escreve | lê |\n"
      "|---|---:|---:|---|---|---|\n")
    for off, campo, tam, escreve, le in LAYOUT:
        marca = "" if le != "-" else " **—**"
        w(f"| `{off:#06x}` | {off // BLOCO_BYTES} | {tam} | {campo} | "
          f"`{escreve}` | `{le}`{marca} |\n")

    sem_leitura = [f"`{off:#06x}`" for off, _, _, _, le in LAYOUT if le == "-"]
    w(f"### A tática vai e não volta\n")
    w(f"**{len(sem_leitura)} destinos são escritos e nunca lidos de volta** por\n"
      f"`0x0040b9ec`: {', '.join(sem_leitura)} — os seis campos de tática. O\n"
      "leitor traz nomes, atributos, números de camisa, formação e cobradores,\n"
      "e para aí. Quem lê a tática de um `.mcr` é o `boton_mcr2isoClick`,\n"
      "direto do arquivo (`0x0040c759` em diante), sem passar pelo buffer que\n"
      "o `boton_mcrClick` enche.\n")

    w("### As duas tabelas que o `.exe` guarda, e por que são tabelas\n")
    w(f"Os cinco destinos de cobrador saem de `{VA_TABELA_COBRADORES:#010x}` e\n"
      f"valem {', '.join(f'`{x:#06x}`' for x in cob)} — **não são\n"
      "crescentes**, e é por isso que são tabela e não aritmética.\n")
    w(f"Os deslocamentos de bit do número de camisa saem de\n"
      f"`{VA_TABELA_BITS:#010x}` e valem {list(bits)}, que é\n"
      "`(5 · (j mod 6)) mod 8` — a mesma forma do `SquadNumbers` do\n"
      "`we2002_core`: 30 bits usados por grupo de seis, 2 perdidos, quatro\n"
      "grupos, 16 bytes.\n")
    w("O gerador **recusa** se qualquer uma das duas deixar de bater com o\n"
      "layout escrito aqui.\n")

    n_fora = sum(1 for o, *_ in LAYOUT if o // BLOCO_BYTES in fora)
    w(f"## O achado: {n_fora} dos {len(LAYOUT)} destinos caem num bloco que o "
      "diretório diz livre\n")
    w(f"O save declara ocupar os blocos {usados}. Os destinos de escrita caem\n"
      f"nos blocos {ocupados}, e **{fora} não está entre os declarados**.\n")
    w("| bloco | bytes não-zero no molde | declarado |\n|---:|---:|---|\n")
    for b in range(1, 5):
        decl = "sim" if b in usados else "**não** (`0xA0`, livre)"
        w(f"| {b} | {nao_zero[b]} | {decl} |\n")
    w("Ou seja: jogadores e números de camisa vão para o bloco 2, que é do\n"
      "save; **formação, tática e cobradores vão para o bloco 3**, que o molde\n"
      "entrega zerado e o diretório marca livre. E o escritor nunca toca o\n"
      "diretório — o menor endereço que ele grava é\n"
      f"`{min(off for off, *_ in LAYOUT):#06x}`, muito depois dos\n"
      f"{QUADRO_BYTES * (QUADROS_DE_DIRETORIO + 1)} bytes de cabeçalho.\n")
    w("**A coincidência que vale registrar:** o readme do original diz que a\n"
      "v0.98 consertou *\"the problem with the captain and kickers when loading\n"
      "from .mcr files\"*, e capitão e cobradores são exatamente campos do\n"
      "bloco 3. O veredito — se o cartão emitido é válido para o console, ou se\n"
      "só serve de transporte entre cópias do editor — é da\n"
      "[WTE-TASK-28](../../docs/tasks/28-import-de-mcr.md); aqui fica a\n"
      "medição.\n")

    med = linhas_medidas()
    if med:
        r = med[0]
        w("## A fixture, e por que ela NAO e versionada\n")
        w("O proprio original emite `.mcr` -- e o `grabar_memoryClick` --,\n"
          "entao a fixture se gera em vez de se escrever a mao: o roteiro\n"
          "[`27-mcr.txt`](../tests/roteiros/27-mcr.txt) abre a ROM japonesa,\n"
          "escolhe um time e salva o cartao.\n")
        w("**O arquivo fica em `work/`, fora do git.** Sao 128 KiB de nomes e\n"
          "atributos tirados da ROM, e este repositorio nao versiona dado do\n"
          "jogo -- nem `roms/`, nem `we-team-editor/`. O que entra no git e a\n"
          "**medicao** abaixo, produzida por\n"
          "`python3 wte/tools/dump_mcr.py --medir <cartao.mcr>`.\n")
        w("| arquivo | bytes mudados | faixas | diretorio intacto | por bloco |\n"
          "|---|---:|---:|:-:|---|\n")
        w(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n")
        w("As duas primeiras colunas fecham com o que a spec do\n"
          "[`grabar_memoryClick`](spec/MainForm.grabar_memoryClick.md) mediu\n"
          "quando o handler foi portado, e as duas ultimas sao a prova do\n"
          "achado acima: **o diretorio sai intacto** e a escrita se reparte\n"
          "entre o bloco declarado e o bloco livre.\n")
    w("## O que o `boton_mcr2isoClick` faz com isso\n")
    w("`0x0040c46c`. Ele **não** é um leitor a mais: reusa as duas rotinas de\n"
      "gravação que a [WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md)\n"
      "portou. Para cada um dos 23 slots, enche o buffer 23 a partir do `.mcr`\n"
      "(`0x0040478c`) e chama a `0x00404820` — a mesma dos handlers de mover —,\n"
      "depois grava o número de camisa pela `0x00404048`. Formação e tática vão\n"
      "direto para a imagem.\n")
    w("**A recusa dele é a mesma família da `-1`, e é aritmética antes de\n"
      "gravar:** para destino de clube de Master League (`ItemIndex > 62`) ele\n"
      "varre os 23 vínculos do time contando quantos precisariam de bloco novo,\n"
      "e se o contador de blocos livres for menor recusa com `Voce precisa de\n"
      "<n> mais blocos livres!!!` sem escrever byte nenhum. Para seleção não\n"
      "confere nada — não há bloco a alocar.\n")

    w("## Os três casos especiais do readme, e onde cada um mora\n")
    w("O readme da v0.98 do original registra três correções sobre `.mcr`, e\n"
      "cada uma é um caso que o **formato** tem. O que se reproduz é a\n"
      "correção, não o bug — e as três estão medidas no binário da v0.99,\n"
      "que já é o corrigido.\n")
    w("| readme | onde a correção mora | como o port a perde |\n"
      "|---|---|---|\n")
    w(f"| *the captain and kickers when loading from .mcr files* | a tabela "
      f"`{VA_TABELA_COBRADORES:#010x}`, que **não é crescente**, mais o capitão "
      f"sozinho em `{0x6500:#06x}` | trocar a tabela por aritmética: os cinco "
      f"sairiam na ordem do endereço e o capitão viraria o sexto vizinho |\n")
    w(f"| *the Eire's goalkeeper when loading a .mcr file* | o carimbo "
      f"`+{0x16:#04x} := {marcas[0x16]:#04x}` da `{VA_CARREGA_DO_CARTAO:#010x}` "
      f"| deixar a identidade zerada: `(0, 0)` é a identidade real do slot 0 do "
      f"time 0, e a `0x00404820` recusa jogador repetido |\n")
    w("| *the spaces in the players names* | o nome é **10 bytes crus**, lidos "
      "por `fread`, e o `0x0040b2d8` tem um ramo próprio para `0x20` ao montar "
      "a lista | tratar o campo como cadeia C: nome que enche os 10 bytes "
      "perderia o fim, e o espaço sumiria da tela |\n")
    w("**O do meio é o que se enxerga menos, e o mais fácil de perder.** Ele "
      "só aparece num time e num slot — o 0 e o 0 —, porque só ali a "
      "identidade real coincide com o zero que um buffer não carimbado teria. "
      f"*{primeiro_time()}* é o item 0 da lista de times, e o slot 0 é o "
      "goleiro; daí o nome que o autor deu ao bug. O `--check` deste gerador lê os três "
      "carimbos do `.text` e os compara com as constantes do Pascal, e o gate "
      f"[`golden-13-roundtrip`](../tests/roteiros/golden-13-roundtrip.txt) "
      "importa **no time 0** justamente por isso.\n")

    rt = linhas_do_roundtrip()
    w("## O round-trip: cartão → imagem → cartão\n")
    if not rt:
        w("Sem medição. Rode\n"
          "`python3 wte/tools/dump_mcr.py --roundtrip <antes> <depois>`.\n")
    else:
        w("Medido **no lado oráculo** do gate: o mesmo cartão entra pelo\n"
          "`boton_mcr2iso` e sai pelo `grabar_memory`, sem nada no meio. A\n"
          "pergunta é do formato, não do port — o que não voltar aqui não\n"
          "volta para o original tampouco.\n")
        w("| campo | bytes | iguais | diferentes | nota |\n"
          "|---|---:|---:|---:|---|\n")
        for ln in rt:
            w(f"| `{ln[0]}` | {ln[1]} | {ln[2]} | {ln[3]} | {ln[4]} |\n")
        if all(int(ln[3]) == 0 for ln in rt):
            w("**Zero divergência, e o arquivo inteiro junto** — a última\n"
              "linha não é campo, é o `cmp` cru dos 131.072 bytes. Nada do que\n"
              "o cartão guarda se perde na ida e volta, nem sequer a folga.\n")
        w("A comparação é **campo a campo**, e não byte a byte no arquivo: os\n"
          "dois cartões herdam a mesma folga do molde, e comparar cru faria a\n"
          "folga responder pelo dado — precaução que esta medição não precisou\n"
          "cobrar, mas que a próxima pode.\n")
    return arruma("".join(s if s.endswith("\n") else s + "\n" for s in o))


def arruma(texto: str) -> str:
    """Linha em branco onde o markdown precisa dela.

    O corpo acima e escrito em blocos curtos, um `w()` por paragrafo, e sem
    isto titulo e tabela sairiam colados no paragrafo anterior -- que renderiza
    errado no GitHub. Fazer aqui, uma vez, e melhor do que lembrar de um `\n`
    solto em cada um dos quarenta `w()`.
    """
    saida: list[str] = []
    for linha in texto.splitlines():
        anterior = saida[-1] if saida else ""
        titulo = linha.startswith("#")
        tabela = linha.startswith("|")
        if anterior.strip() and (titulo
                                 or (tabela and not anterior.startswith("|"))
                                 or (anterior.startswith("|") and not tabela)):
            saida.append("")
        saida.append(linha)
    return "\n".join(saida) + "\n"


def linhas_medidas() -> list[list[str]]:
    if not MEDIDO.is_file():
        return []
    linhas = MEDIDO.read_text(encoding="utf-8").splitlines()
    return [ln.split("\t") for ln in linhas[1:] if ln.strip()]


def do_medir(caminho: str) -> int:
    """Confere um `.mcr` de verdade contra o molde, e versiona a conta.

    A FIXTURE NAO E VERSIONADA, e a decisao esta escrita no markdown: 128 KiB
    de nomes e atributos tirados da ROM sao dado do jogo, e este repositorio
    nao versiona dado do jogo -- nem `roms/`, nem `we-team-editor/`. O que
    entra no git e a MEDICAO; quem quiser refazer gera a fixture com o proprio
    original, pelo roteiro `27-mcr.txt`.
    """
    p = Path(caminho)
    if not p.is_file():
        print(f"ERRO: {caminho} nao existe", file=sys.stderr)
        return 2
    mcr = p.read_bytes()
    molde = DAT.read_bytes()[:CARTAO_BYTES]
    if len(mcr) != CARTAO_BYTES:
        print(f"ERRO: {caminho} tem {len(mcr)} bytes, e cartao tem "
              f"{CARTAO_BYTES}", file=sys.stderr)
        return 2
    faixas = []
    i = 0
    while i < len(mcr):
        if mcr[i] != molde[i]:
            j = i
            while j < len(mcr) and mcr[j] != molde[j]:
                j += 1
            faixas.append((i, j - 1, j - i))
            i = j
        else:
            i += 1
    por_bloco: dict[int, int] = {}
    for a, _, n in faixas:
        por_bloco[a // BLOCO_BYTES] = por_bloco.get(a // BLOCO_BYTES, 0) + n
    dir_igual = mcr[:BLOCO_BYTES] == molde[:BLOCO_BYTES]
    linhas = ["arquivo\tbytes\tfaixas\tdiretorio_intacto\tpor_bloco"]
    linhas.append(f"{p.name}\t{sum(f[2] for f in faixas)}\t{len(faixas)}\t"
                  f"{'sim' if dir_igual else 'NAO'}\t"
                  + ";".join(f"{b}={por_bloco[b]}" for b in sorted(por_bloco)))
    MEDIDO.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(f"  {p.name}: {sum(f[2] for f in faixas)} bytes em {len(faixas)} "
          f"faixas; diretorio intacto={dir_igual}; por bloco {por_bloco}")
    print(f"  {MEDIDO.relative_to(ROOT)}")
    return 0


def campos_do_cartao(card: bytes) -> dict[str, bytes]:
    """Os seis campos logicos de um cartao, ja remontados.

    NAO E FATIA CONTIGUA em dois deles: nome e atributos moram em registros de
    32 bytes com 10 de folga, e a formacao sai partida em 10 + 20. Comparar
    fatia crua misturaria folga com dado, e a folga e a mesma nos dois lados
    por vir do molde -- o que faria um round-trip quebrado parecer melhor do
    que e.
    """
    nomes = b"".join(card[0x5910 + 32 * j:0x5910 + 32 * j + 10]
                     for j in range(23))
    atrib = b"".join(card[0x5904 + 32 * j:0x5904 + 32 * j + 12]
                     for j in range(23))
    cob = bytes(card[a] for a in COBRADORES_ESPERADOS) + bytes([card[0x6500]])
    tat = bytes(card[a] for a in (0x64E2, 0x6102, 0x6488, 0x6479, 0x6497,
                                  0x64A6))
    return {
        "nomes": nomes,
        "atributos": atrib,
        "numeros": card[0x5404:0x5404 + 16],
        "formacao": card[0x63D5:0x63D5 + 10] + card[0x62A8:0x62A8 + 20],
        "cobradores": cob,
        "tatica": tat,
    }


def _curto(caminho: Path) -> Path:
    # O destino pode estar fora da arvore (o teste aponta para um `tempfile`);
    # ali o caminho absoluto e o que se quer ler.
    return (caminho.relative_to(ROOT)
            if caminho.is_relative_to(ROOT) else caminho)


def do_roundtrip(antes: str, depois: str,
                 destino: Path = IDA_E_VOLTA) -> int:
    """`.mcr` -> imagem -> `.mcr`: o que sobrevive a ida e volta.

    A pergunta do criterio da WTE-TASK-28 e se exportar depois de importar
    devolve o mesmo cartao. Nao e pergunta sobre o port: e sobre o FORMATO, e
    a resposta vale para o original tanto quanto para nos -- por isso os dois
    arquivos comparados aqui saem do lado ORACULO do gate.

    Compara campo a campo, e nao byte a byte no arquivo inteiro: o cartao tem
    folga que vem do molde nos dois lados, e ela mascararia divergencia.

    `destino` existe para o teste NAO escrever por cima da medicao versionada:
    ele aponta para o `tempfile` que ja cria. Sem isso a bateria reescrevia um
    arquivo de `wte/re/` a cada corrida e o repunha num `finally` -- e
    interrupcao que pulasse o `finally` deixava dado sintetico no lugar da
    medicao.
    """
    caminhos = [Path(antes), Path(depois)]
    cartoes = []
    for c in caminhos:
        if not c.is_file():
            print(f"ERRO: {c} nao existe", file=sys.stderr)
            return 2
        dados = c.read_bytes()
        if len(dados) != CARTAO_BYTES:
            print(f"ERRO: {c} tem {len(dados)} bytes, e cartao tem "
                  f"{CARTAO_BYTES}", file=sys.stderr)
            return 2
        cartoes.append(dados)
    a, b = (campos_do_cartao(c) for c in cartoes)
    linhas = ["campo\tbytes\tiguais\tdiferentes\tnota"]
    for nome in ("nomes", "atributos", "numeros", "formacao", "cobradores",
                 "tatica"):
        x, y = a[nome], b[nome]
        difs = [i for i in range(len(x)) if x[i] != y[i]]
        nota = "-"
        if difs:
            nota = ("deslocamentos " + ",".join(str(i) for i in difs[:8])
                    + ("..." if len(difs) > 8 else ""))
        linhas.append(f"{nome}\t{len(x)}\t{len(x) - len(difs)}\t{len(difs)}\t"
                      f"{nota}")
        print(f"  {nome}: {len(x) - len(difs)}/{len(x)} iguais")
    bruto = sum(1 for i in range(CARTAO_BYTES) if cartoes[0][i] != cartoes[1][i])
    linhas.append(f"arquivo inteiro\t{CARTAO_BYTES}\t{CARTAO_BYTES - bruto}\t"
                  f"{bruto}\t{caminhos[0].name} contra {caminhos[1].name}")
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8",
                       newline="\n")
    print(f"  arquivo inteiro: {bruto} bytes diferentes")
    print(f"  {_curto(destino)}")
    return 0


def linhas_do_roundtrip(destino: Path = IDA_E_VOLTA) -> list[list[str]]:
    if not destino.is_file():
        return []
    linhas = destino.read_text(encoding="utf-8").splitlines()
    return [ln.split("\t") for ln in linhas[1:] if ln.strip()]


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de dump_mcr.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    print(f"{len(files)} arquivos em dia com {REL_DAT} + {REL_EXE}; "
          f"{REL_PASCAL} bate com o layout")
    return 0


def do_write(files: dict[Path, str]) -> int:
    for caminho, conteudo in sorted(files.items()):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {caminho.relative_to(ROOT)}: {conteudo.count(chr(10))} linhas")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--roundtrip":
        if len(argv) != 3:
            print(f"uso: {GERADOR} --roundtrip <antes.mcr> <depois.mcr>",
                  file=sys.stderr)
            return 2
        try:
            return do_roundtrip(argv[1], argv[2])
        except McrError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2
    if argv and argv[0] == "--medir":
        if len(argv) != 2:
            print(f"uso: {GERADOR} --medir <cartao.mcr>", file=sys.stderr)
            return 2
        try:
            return do_medir(argv[1])
        except McrError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GERADOR} [--check] | {GERADOR} --medir "
                  f"<cartao.mcr> | {GERADOR} --roundtrip <antes> <depois>",
                  file=sys.stderr)
            return 2
    try:
        files = gera()
    except McrError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
