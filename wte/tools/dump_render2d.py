#!/usr/bin/env python3
"""O render 2D do WE2002 Team Editor: cor, aritmetica e arredondamento.

Gera `wte/re/render2d.md` e `wte/re/render2d.tsv` -- insumo da
[WTE-TASK-29](../../docs/tasks/29-camisa-e-bandeira-2d.md).

    python3 wte/tools/dump_render2d.py           # regera as duas saidas
    python3 wte/tools/dump_render2d.py --check   # o que `make -C wte check` roda

## O que este script existe para responder ANTES de escrever Pascal

O enunciado da task nomeia tres perguntas e manda responde-las antes do codigo,
porque cada uma **muda o algoritmo inteiro**:

1. paleta ou varredura de pixel?
2. que espaco de cor tem o escurecer/clarear?
3. onde some a fidelidade do gradiente?

As tres tem resposta no `.text`, e nenhuma precisa de decompilador -- sao
padroes de instrucao curtos e inequivocos. Este script os **le** e recusa
emitir markdown se algum deixar de bater. Nenhum numero daqui e afirmado a mao.

## A resposta curta, para quem so quer o resumo

**Paleta.** O bitmap guarda forma; a cor mora nas primeiras entradas da paleta,
e o original as reescreve -- 16 na bandeira, 15 no uniforme, e a assimetria e
medida aqui. Ja estava medido na WTE-TASK-08 (secao 6 do `assets.md`) que o
meio e a paleta; a mecanica de escrita e reconferida instrucao a instrucao.

**Nem RGB nem HSL: a aritmetica acontece na palavra BGR555 empacotada.**
Escurecer subtrai `1`, `0x20` e `0x400` -- um passo em cada campo de 5 bits --
com piso em zero conferido no byte JA expandido. Clarear soma os mesmos tres,
com teto em `0xF8`. Nao ha multiplicacao, nao ha conversao para outro espaco.

**O gradiente acumula em float de precisao SIMPLES e trunca para zero.** E ali
que a fidelidade some, e a §9 do plano previu: um port que use `Round` desloca
a rampa inteira.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GERADOR = "wte/tools/dump_render2d.py"

EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
IMAGEM = ROOT / "we-team-editor" / "image"
REL_EXE = "we-team-editor/we-team-editor.exe"

OUT_MD = ROOT / "wte" / "re" / "render2d.md"
OUT_TSV = ROOT / "wte" / "re" / "render2d.tsv"
PASCAL = ROOT / "wte" / "src" / "we2002_render.pas"
REL_PASCAL = "wte/src/we2002_render.pas"
PASCAL_BMP = ROOT / "wte" / "src" / "we2002_bmp.pas"
REL_PASCAL_BMP = "wte/src/we2002_bmp.pas"
OUT_PAS = ROOT / "wte" / "src" / "wte_uniformes.pas"

# --- os enderecos, todos da tabela de alvos da WTE-TASK-29 ----------------
VA_DECODIFICA = 0x00404DD4    # BGR555 -> 3 bytes, 154 B
VA_TRUNCA = 0x00419D80        # o `__ftol` da RTL: fistp com RC = truncar
VA_ESCURECER = 0x004065FC     # oscurecerClick
VA_CLAREAR = 0x00406744       # aclararClick
VA_GRADIENTE = 0x004063B0     # gradienteClick
VA_BANDEIRA_1 = 0x00405270    # desenha a bandeira do titular
VA_BANDEIRA_2 = 0x00405468    # ... e a do reserva
VA_UNIFORME = 0x004056C8      # desenha camisa e calcao
VA_EXPORTA_UNI = 0x0040EE80   # grabar_camisetaClick
VA_CORES_BANDEIRA = 0x00432EF4  # as 16 palavras BGR555 da bandeira em vigor
VA_KIT_EM_VIGOR = 0x00432F56   # os DOIS jogos de 16 palavras que o desenho le
VA_KIT_LIDO = 0x00432F16       # ... e os dois que o carregador enche do disco
VA_COPIA_ESTADO = 0x00404F90   # copia o estado visual de um slot para o outro
VA_CARREGA_ESTADO = 0x004050F0  # le o estado visual do time do disco
SLOT_BYTES = 64                # um slot sao os dois jogos, 32 bytes cada
VA_TAB_FORMA = 0x004231E8      # 95 bytes: a forma de bandeira padrao por time
VA_TAB_UNIFORME = 0x004232A6   # 95 x 4 bytes: camiseta e calcao, por time e jogo

# Quantos times o formato tem: 63 selecoes (0..62) + 32 clubes de Master League
# (63..94). E o mesmo 95 dos arrays `TEAM_NAME_LEN_*` do `we2002_core`, e o
# mesmo em que o `lista_equiposChange` corta (`cmp eax,0x5f`).
TIMES_N = 95
# Um jogo de uniforme sao 16 palavras BGR555; os dois ficam colados, e e por
# isso que o `lea` do desenhista multiplica o jogo por 32.
KIT_PALAVRAS = 16
KIT_PASSO = KIT_PALAVRAS * 2

# O bitmap de 8 bpp: 54 de cabecalho e 256 entradas de 4 bytes. O `0x36` dos
# renderizadores e exatamente o fim do cabecalho -- a primeira entrada.
BMP_CABECALHO = 54
BMP_ENTRADAS = 256
BMP_ENTRADA_BYTES = 4
# Quantas palavras BGR555 a tabela da bandeira em vigor guarda. NAO e o mesmo
# que "quantas entradas de paleta cada rotina reescreve" -- ver DESENHISTAS.
CORES_BANDEIRA_N = 16

# O setor MODE2/2352 da imagem de CD, para a conta do exportador.
SETOR_BYTES = 2352
SETOR_PAYLOAD = 0x800         # 2048
SETOR_RESTO = 0x130           # 304 = 24 de cabecalho + 280 de EDC/ECC

# --- os padroes de instrucao que sustentam cada afirmacao -----------------
# Cada entrada e (rotina, padrao, quantas vezes, o que prova). O script recusa
# emitir se a contagem nao bater: padrao que sumiu e afirmacao que caducou.
ASSINATURAS = [
    (VA_DECODIFICA, 0x9A, bytes.fromhex("c02203"), 1,
     "`shl BYTE PTR [edx],0x3` — a expansao de 5 para 8 bits e deslocamento, "
     "e NAO replicacao de bit alto"),
    (VA_DECODIFICA, 0x9A, bytes.fromhex("83fe05"), 1,
     "`cmp esi,0x5` — sao cinco bits por canal"),
    (VA_DECODIFICA, 0x9A, bytes.fromhex("833c2403"), 1,
     "`cmp DWORD PTR [esp],0x3` — sao tres canais"),
    (VA_TRUNCA, 0x2C, bytes.fromhex("814dfc010c0000"), 1,
     "`or DWORD PTR [ebp-0x4],0xc01` — os bits 10-11 do control word em `11`, "
     "que e **truncar para zero**"),
    (VA_ESCURECER, 0x50, bytes.fromhex("ff0b"), 1,
     "`dec DWORD PTR [ebx]` — um passo para baixo no canal R (bits 0-4)"),
    (VA_ESCURECER, 0x50, bytes.fromhex("832b20"), 1,
     "`sub DWORD PTR [ebx],0x20` — um passo no canal G (bits 5-9)"),
    (VA_ESCURECER, 0x50, bytes.fromhex("812b00040000"), 1,
     "`sub DWORD PTR [ebx],0x400` — um passo no canal B (bits 10-14)"),
    (VA_ESCURECER, 0x50, bytes.fromhex("807d0000"), 1,
     "`cmp BYTE PTR [ebp+0x0],0x0` — o piso e conferido no byte EXPANDIDO"),
    (VA_CLAREAR, 0x45, bytes.fromhex("ff03"), 1,
     "`inc DWORD PTR [ebx]` — o espelho exato do escurecer, no canal R"),
    (VA_CLAREAR, 0x45, bytes.fromhex("830320"), 1,
     "`add DWORD PTR [ebx],0x20` — idem, canal G"),
    (VA_CLAREAR, 0x45, bytes.fromhex("810300040000"), 1,
     "`add DWORD PTR [ebx],0x400` — idem, canal B"),
    (VA_CLAREAR, 0x45, bytes.fromhex("807d00f8"), 1,
     "`cmp BYTE PTR [ebp+0x0],0xf8` — o teto e `0xF8`, que e `31 << 3`: a "
     "prova de que a expansao satura em **248**, e nao em 255"),
    (VA_GRADIENTE, 0x24C, bytes.fromhex("d91e"), 1,
     "`fstp DWORD PTR [esi]` — o passo do gradiente e guardado em float de "
     "precisao **simples**"),
    (VA_GRADIENTE, 0x24C, bytes.fromhex("c1e005"), 1,
     "`shl eax,0x5` — o canal G volta empacotado por deslocamento"),
    (VA_GRADIENTE, 0x24C, bytes.fromhex("c1e00a"), 1,
     "`shl eax,0xa` — e o B por dez"),
    (VA_EXPORTA_UNI, 0x290, bytes.fromhex("6800080000"), 2,
     "`push 0x800` duas vezes — le 2048 e escreve 2048, o payload do setor"),
    (VA_EXPORTA_UNI, 0x290, bytes.fromhex("6830010000"), 1,
     "`push 0x130` — e pula 304, que e cabecalho mais EDC/ECC"),
    (VA_BANDEIRA_1, 0x200, bytes.fromhex("bbf42e4300"), 1,
     "`mov ebx,0x432ef4` — a bandeira le as 16 palavras da GLOBAL do time "
     "selecionado, ja carregada"),
    (VA_UNIFORME, 0x40A, bytes.fromhex("8d1cc5562f4300"), 2,
     "`lea ebx,[eax*8+0x432f56]` **duas vezes, com a mesma base** — camisa e "
     "calcao recebem o MESMO jogo de cores, e nao um cada"),
    (VA_UNIFORME, 0x40A, bytes.fromhex("8d0c95a6324200"), 1,
     "`lea ecx,[edx*4+0x4232a6]` — o indice da camisa sai de tabela do `.exe`, "
     "e nao da imagem de CD"),
    (VA_UNIFORME, 0x40A, bytes.fromhex("8d048da7324200"), 1,
     "`lea eax,[ecx*4+0x4232a7]` — o do calcao e o byte seguinte da mesma "
     "tabela"),
    (VA_CARREGA_ESTADO, 0x50, bytes.fromhex("68162f4300"), 1,
     "`push 0x432f16` — o carregador enche o PRIMEIRO jogo do slot 0 com "
     "0x20 bytes lidos do disco"),
    (VA_CARREGA_ESTADO, 0x50, bytes.fromhex("68362f4300"), 1,
     "`push 0x432f36` — e o segundo jogo, logo depois, com outros 0x20"),
    (VA_COPIA_ESTADO, 0x100, bytes.fromhex("8d04c5162f4300"), 1,
     "`lea eax,[eax*8+0x432f16]` — o slot tem 64 bytes (`eax` ja vem "
     "multiplicado por 8), e e por isso que o slot 1 comeca em `0x432f56`"),
    (VA_COPIA_ESTADO, 0x100, bytes.fromhex("8d14d5162f4300"), 1,
     "`lea edx,[edx*8+0x432f16]` — a outra ponta da mesma copia: origem e "
     "destino sao slots do MESMO vetor"),
]

# As tres rotinas de desenho. O quarto campo e quantas entradas de paleta cada
# uma reescreve POR ARQUIVO, e ele NAO e o mesmo nas tres -- ver o achado no
# markdown. O quinto e quantos arquivos ela toca.
DESENHISTAS = [
    (VA_BANDEIRA_1, 0x200, "bandeira do titular", 16, 1),
    (VA_BANDEIRA_2, 0x260, "bandeira do reserva", 16, 1),
    (VA_UNIFORME, 0x40A, "camisa e calcao", 15, 2),
]
# `push 0x36` = seek para a primeira entrada da paleta.
PAT_SEEK_PALETA = bytes.fromhex("6a36")
# `cmp esi,<n>` -- o limite do laco de entradas. `83 fe <n>`, com `jl` logo
# depois, entao o laco roda de 0 a n-1.
def pat_limite(n: int) -> bytes:
    return bytes([0x83, 0xFE, n])


class RenderError(Exception):
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
    raise RenderError(f"{REL_EXE}: VA {va:#x}+{quantos} fora de toda secao")


def confere_assinaturas(blob: bytes) -> list[tuple[int, str, str]]:
    """Cada afirmacao do markdown contra o `.text`, uma a uma.

    Devolve a lista `(rotina, padrao, prova)` para a tabela do markdown. Recusa
    se a contagem nao bater -- e a mesma politica do `dump_mcr.py`: nao emito
    layout que nao fecha.
    """
    saida = []
    ruins = []
    for va, tam, padrao, vezes, prova in ASSINATURAS:
        corpo = le_bytes(blob, va, tam)
        achou = corpo.count(padrao)
        if achou != vezes:
            ruins.append(f"{va:#010x}: `{padrao.hex()}` aparece {achou}x, "
                         f"esperado {vezes}x — {prova}")
            continue
        saida.append((va, padrao.hex(), prova))
    if ruins:
        raise RenderError(
            "o `.text` nao sustenta o que este gerador afirma:\n     "
            + "\n     ".join(ruins))
    return saida


def imediatos_do_exe(blob: bytes) -> dict[str, int]:
    """Os numeros que a unidade Pascal usa, EXTRAIDOS do `.text`.

    Nao e a mesma coisa que a tabela `ASSINATURAS`: aquela confere que um
    padrao existe, esta **le o operando**. A diferenca importa -- um `shl` que
    virasse `shl 4` continuaria casando com um padrao de tres bytes escrito
    frouxo, e sairia daqui como 4.

    Cada valor e localizado pelo opcode que o carrega, e o operando vem de
    dentro da instrucao.
    """
    def imediato8(va: int, tam: int, prefixo: bytes, quem: str) -> int:
        corpo = le_bytes(blob, va, tam)
        i = corpo.find(prefixo)
        if i < 0:
            raise RenderError(f"{quem}: `{prefixo.hex()}` nao esta em "
                              f"{va:#010x}")
        return corpo[i + len(prefixo)]

    def imediato32(va: int, tam: int, prefixo: bytes, quem: str) -> int:
        corpo = le_bytes(blob, va, tam)
        i = corpo.find(prefixo)
        if i < 0:
            raise RenderError(f"{quem}: `{prefixo.hex()}` nao esta em "
                              f"{va:#010x}")
        return int.from_bytes(corpo[i + len(prefixo):i + len(prefixo) + 4],
                              "little")

    achados = {
        # `shl BYTE PTR [edx],<n>` -- de quanto e a expansao de 5 para 8 bits
        "RENDER_EXPANSAO": imediato8(VA_DECODIFICA, 0x9A,
                                     bytes.fromhex("c022"), "expansao"),
        # `cmp esi,<n>` no laco de bits
        "RENDER_BITS": imediato8(VA_DECODIFICA, 0x9A,
                                 bytes.fromhex("83fe"), "bits por canal"),
        # `cmp DWORD PTR [esp],<n>` no laco de canais
        "RENDER_CANAIS": imediato8(VA_DECODIFICA, 0x9A,
                                   bytes.fromhex("833c24"), "canais"),
        # `cmp BYTE PTR [ebp+0x0],<n>` -- o teto do clarear
        "RENDER_MAXIMO": imediato8(VA_CLAREAR, 0x45,
                                   bytes.fromhex("807d00"), "teto"),
        # `add DWORD PTR [ebx],<n>` -- o degrau do canal G
        "RENDER_PASSO_G": imediato8(VA_CLAREAR, 0x45,
                                    bytes.fromhex("8303"), "passo G"),
        # ... e o do B, que nao cabe em oito bits
        "RENDER_PASSO_B": imediato32(VA_CLAREAR, 0x45,
                                     bytes.fromhex("8103"), "passo B"),
    }
    # O degrau do canal R e um `dec`, sem operando: o proprio opcode diz 1.
    if bytes.fromhex("ff03") not in le_bytes(blob, VA_CLAREAR, 0x45):
        raise RenderError("passo R: `inc DWORD PTR [ebx]` nao esta em "
                          f"{VA_CLAREAR:#010x}")
    achados["RENDER_PASSO_R"] = 1
    # Quantas entradas cada desenhista reescreve, do `cmp esi,<n>` de cada um.
    achados["PALETA_BANDEIRA"] = imediato8(VA_BANDEIRA_1, 0x200,
                                           bytes.fromhex("83fe"), "bandeira")
    achados["PALETA_UNIFORME"] = imediato8(VA_UNIFORME, 0x40A,
                                           bytes.fromhex("83fe"), "uniforme")
    return achados


def confere_seek_da_paleta(blob: bytes, cabecalho: int) -> None:
    """O `push <cabecalho>` das tres rotinas de desenho.

    Este e o unico numero que NAO se extrai: um `push imm8` sozinho nao diz
    para que serve, e a rotina tem varios. A conferencia vai na direcao
    contraria -- o Pascal afirma 54, e o `.exe` tem de conter `push 54` dentro
    de cada desenhista. Afirmacao que o binario nao sustenta reprova; numero
    que o binario tem e o Pascal nao conhece, nao.
    """
    padrao = bytes([0x6A, cabecalho])
    faltam = [f"{va:#010x} ({papel})"
              for va, tam, papel, _, _ in DESENHISTAS
              if padrao not in le_bytes(blob, va, tam)]
    if faltam:
        raise RenderError(
            f"o seek de paleta `push {cabecalho:#04x}` nao esta em: "
            + ", ".join(faltam))


def constantes_do_pascal() -> dict[str, int]:
    """As constantes de `we2002_render.pas`, lidas do fonte.

    So `NOME = $HEX;` ou `NOME = decimal;`. Expressao fica de fora de
    proposito: aceitar e avaliar seria reimplementar Pascal aqui, e avaliar
    errado em silencio e pior do que nao conferir. A unidade escreve estes
    valores como literal justamente para caber nesta leitura -- a derivacao
    mora no comentario dela e e executada pelo `test_render.pas`.
    """
    import re
    if not PASCAL.is_file():
        raise RenderError(f"{REL_PASCAL} nao existe")
    achados: dict[str, int] = {}
    for linha in PASCAL.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(\$[0-9A-Fa-f]+|\d+)\s*;",
                     linha)
        if m:
            achados.setdefault(m.group(1),
                               int(m.group(2)[1:], 16)
                               if m.group(2).startswith("$")
                               else int(m.group(2)))
    return achados


def confere_pascal(do_exe: dict[str, int]) -> None:
    """O `.exe` contra o `we2002_render.pas`, numero a numero.

    Mesmo contrato do `dump_mcr.py` sobre o `we2002_mcr.pas`: a unidade e
    escrita a mao, e este e o guard que impede as duas verdades de se
    separarem.
    """
    do_pascal = constantes_do_pascal()
    ruins = []
    for nome, valor in sorted(do_exe.items()):
        if nome not in do_pascal:
            ruins.append(f"{nome}: ausente de {REL_PASCAL}")
        elif do_pascal[nome] != valor:
            ruins.append(f"{nome}: Pascal diz {do_pascal[nome]:#x}, o `.exe` "
                         f"diz {valor:#x}")
    # E a rotina que a rampa NAO pode usar: `Round` no lugar de `Trunc` e o
    # risco nomeado, e um grep e barato.
    corpo = PASCAL.read_text(encoding="utf-8")
    if "Trunc(acumulado[0])" not in corpo:
        ruins.append("Rampa: nao trunca o acumulador -- ver a secao do "
                     "gradiente no markdown")
    if "Round(acumulado" in corpo:
        ruins.append("Rampa: usa `Round`, e o original TRUNCA")
    if ruins:
        raise RenderError(
            f"{REL_PASCAL} e o `.text` divergem:\n     " + "\n     ".join(ruins))


def confere_desenhistas(blob: bytes) -> list[tuple[int, str, int, int]]:
    """As tres rotinas de desenho, e a assimetria entre elas.

    Nenhuma varre pixel: as tres posicionam o arquivo na primeira entrada da
    paleta (`0x36`) e reescrevem um punhado de entradas. **Mas nao o mesmo
    punhado** -- a bandeira faz 16 e o uniforme faz 15, e o uniforme faz isso
    duas vezes, uma por arquivo. Cada `push 0x36` e um arquivo.

    O limite de cada laco e conferido pelo `cmp esi,<n>` que o antecede; se
    algum mudar, este gerador recusa em vez de deixar a prosa mentir.
    """
    ruins = []
    for va, tam, papel, entradas, arquivos in DESENHISTAS:
        corpo = le_bytes(blob, va, tam)
        vistos = corpo.count(PAT_SEEK_PALETA)
        if vistos != arquivos:
            ruins.append(f"{va:#010x} ({papel}): {vistos} `push 0x36`, "
                         f"esperado {arquivos}")
        limites = corpo.count(pat_limite(entradas))
        if limites != arquivos:
            ruins.append(f"{va:#010x} ({papel}): {limites} `cmp esi,"
                         f"{entradas:#04x}`, esperado {arquivos}")
    if ruins:
        raise RenderError(
            "os tres desenhistas nao fecham com o que o markdown afirma:\n     "
            + "\n     ".join(ruins))
    return [(va, papel, entradas, arquivos)
            for va, _, papel, entradas, arquivos in DESENHISTAS]


def larg_alt(cab: bytes) -> tuple[int, int]:
    return struct.unpack_from("<ii", cab, 18)


def bitmaps() -> tuple[dict[str, int], dict[str, int]]:
    """Os `.bmp` em disco, contados e conferidos -- nao afirmados.

    A conta que importa e uma: `0x36` so cai na primeira entrada da paleta se o
    cabecalho tiver 54 bytes, e isso depende de a profundidade ser 8 bpp. Um
    bitmap de 24 bpp no meio da pasta quebraria a mecanica inteira, entao vale
    medir em vez de supor.
    """
    if not IMAGEM.is_dir():
        raise RenderError(f"we-team-editor/image nao existe")
    contas = {"bandeiras": 0, "camisas": 0, "calcoes": 0, "oito_bpp": 0,
              "fora": 0}
    dados, infos, compressoes = set(), set(), set()
    # pixels, largura, altura do maior bitmap que o render 2D toca. So as duas
    # pastas dele: `careto_base.bmp` e maior e nao entra em redesenho nenhum
    # desta task (CORR-WTE-063 tirou cara, cabelo e barba do escopo).
    maior = [0, 0, 0]
    for caminho in sorted(IMAGEM.rglob("*.bmp")):
        nome = caminho.name.lower()
        cab = caminho.read_bytes()[:54]
        if len(cab) < 54 or cab[:2] != b"BM":
            contas["fora"] += 1
            continue
        bpp, = struct.unpack_from("<H", cab, 28)
        if bpp == 8:
            contas["oito_bpp"] += 1
            # A forma que a mecanica ASSUME, medida em vez de suposta: onde os
            # pixels comecam, o tamanho do cabecalho de informacao, e se ha
            # compressao. O `we2002_bmp.pas` recusa arquivo que fuja disso, e o
            # `confere_bmp` cruza os dois lados.
            dados.add(struct.unpack_from("<I", cab, 10)[0])
            infos.add(struct.unpack_from("<I", cab, 14)[0])
            compressoes.add(struct.unpack_from("<I", cab, 30)[0])
            if (caminho.parent.name in ("banderas", "uniformes2d")
                    and abs(larg_alt(cab)[0] * larg_alt(cab)[1]) > maior[0]):
                maior[0], maior[1], maior[2] = (
                    abs(larg_alt(cab)[0] * larg_alt(cab)[1]),
                    abs(larg_alt(cab)[0]), abs(larg_alt(cab)[1]))
        else:
            contas["fora"] += 1
        if caminho.parent.name == "banderas":
            contas["bandeiras"] += 1
        elif caminho.parent.name == "uniformes2d":
            if nome.startswith("camiseta"):
                contas["camisas"] += 1
            elif nome.startswith("pantalon"):
                contas["calcoes"] += 1
    if len(dados) != 1 or len(infos) != 1 or len(compressoes) != 1:
        raise RenderError(
            "os `.bmp` de 8 bpp nao tem todos a mesma forma de cabecalho: "
            f"inicio dos pixels {sorted(dados)}, cabecalho de informacao "
            f"{sorted(infos)}, compressao {sorted(compressoes)}")
    contas["maior_em_pixels"] = maior[0]
    contas["maior_largura"] = maior[1]
    contas["maior_altura"] = maior[2]
    forma = {"BMP_DADOS": dados.pop(),
             "BMP_INFO_BYTES": infos.pop(),
             "BMP_SEM_COMPRESSAO": compressoes.pop(),
             "BMP_BITS": 8,
             "BMP_PALETA_ENTRADAS": BMP_ENTRADAS}
    return contas, forma


def confere_o_slot() -> None:
    """O bloco que o desenho le e o slot 1, e o que o disco enche e o slot 0.

    Nao e curiosidade de layout: e a explicacao de por que o desenho comeca na
    palavra 1 do `home_kit` da camada de dados. O carregador enche
    `0x432f16` + `0x432f36` (dois jogos de 32 bytes) e em seguida copia o slot
    inteiro -- 64 bytes -- para o slot 1, que e o rascunho que o `ficha_color`
    edita e o desenhista le.
    """
    if VA_KIT_EM_VIGOR != VA_KIT_LIDO + SLOT_BYTES:
        raise RenderError(
            f"{VA_KIT_EM_VIGOR:#010x} nao e o slot 1 de {VA_KIT_LIDO:#010x} "
            f"com passo {SLOT_BYTES}")


def tabelas(blob: bytes) -> tuple[list[int], list[tuple[int, int, int, int]]]:
    """As duas tabelas de `.data` que dizem QUAL arquivo cada time usa.

    A cor vem da imagem de CD; a **forma** vem daqui. Sao duas, e elas nao se
    parecem:

    - `0x004231e8`, 95 bytes -- a forma de bandeira *padrao* de cada time. O
      original nao a usa para desenhar: quem manda e o byte lido da imagem
      (secao 3.2 do `assets.md`). Ela alimenta o combo `lista_col0`, e o
      caminho inverso procura nela a PRIMEIRA posicao cujo valor bate;
    - `0x004232a6`, 95 x 4 bytes -- `(camisa, calcao)` por time e por jogo. Esta
      **e** a fonte do desenho: a forma da camisa nao esta na imagem de CD.

    A validacao nao e de forma, e de alcance: todo indice que a tabela nomeia
    tem de ter arquivo na pasta do usuario. Um indice sem arquivo seria uma
    tela em branco no port e um `LoadFromFile` falho no original.
    """
    formas = list(le_bytes(blob, VA_TAB_FORMA, TIMES_N))
    cru = le_bytes(blob, VA_TAB_UNIFORME, TIMES_N * 4)
    kits = [(cru[t * 4], cru[t * 4 + 1], cru[t * 4 + 2], cru[t * 4 + 3])
            for t in range(TIMES_N)]
    if not IMAGEM.is_dir():
        raise RenderError("we-team-editor/image nao existe")
    def existe(sub: str, prefixo: str, n: int) -> bool:
        return (IMAGEM / sub / f"{prefixo}{n}.bmp").is_file()
    faltam = sorted({n for n in formas if not existe("banderas", "bandera", n)})
    if faltam:
        raise RenderError(
            f"{VA_TAB_FORMA:#010x} nomeia bandeiras que nao existem em "
            f"disco: {faltam}")
    sem_camisa = sorted({k[i] for k in kits for i in (0, 2)
                         if not existe("uniformes2d", "camiseta", k[i])})
    sem_calcao = sorted({k[i] for k in kits for i in (1, 3)
                         if not existe("uniformes2d", "pantalon", k[i])})
    if sem_camisa or sem_calcao:
        raise RenderError(
            f"{VA_TAB_UNIFORME:#010x} nomeia arquivos que nao existem: "
            f"camisetas {sem_camisa}, calcoes {sem_calcao}")
    return formas, kits


def constantes_do_bmp() -> dict[str, int]:
    """As constantes de `we2002_bmp.pas`, pela mesma leitura literal."""
    import re
    if not PASCAL_BMP.is_file():
        raise RenderError(f"{REL_PASCAL_BMP} nao existe")
    achados: dict[str, int] = {}
    for linha in PASCAL_BMP.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(\$[0-9A-Fa-f]+|\d+)\s*;",
                     linha)
        if m:
            achados.setdefault(m.group(1),
                               int(m.group(2)[1:], 16)
                               if m.group(2).startswith("$")
                               else int(m.group(2)))
    return achados


def confere_bmp(forma: dict[str, int]) -> None:
    """O recipiente que o Pascal exige contra o que os 198 arquivos SAO.

    Direcao diferente da do `confere_pascal`: ali o juiz e o `.text`, aqui e a
    pasta do usuario. O `we2002_bmp.pas` recusa arquivo que nao case com estas
    constantes, e um valor errado nelas faria o port recusar a pasta inteira em
    silencio -- tela em branco sem erro, que e o pior modo de falhar.
    """
    do_pascal = constantes_do_bmp()
    ruins = []
    for nome, valor in sorted(forma.items()):
        if nome not in do_pascal:
            ruins.append(f"{nome}: ausente de {REL_PASCAL_BMP}")
        elif do_pascal[nome] != valor:
            ruins.append(f"{nome}: Pascal diz {do_pascal[nome]}, os `.bmp` do "
                         f"usuario dizem {valor}")
    # E o fecho do circulo com o `.exe`: o `0x36` das tres rotinas de desenho
    # so cai na primeira entrada da paleta se o cabecalho tiver este tamanho.
    if do_pascal.get("BMP_DADOS") != BMP_CABECALHO + BMP_ENTRADAS * BMP_ENTRADA_BYTES:
        ruins.append(
            f"BMP_DADOS: {do_pascal.get('BMP_DADOS')} nao e "
            f"{BMP_CABECALHO} + {BMP_ENTRADAS} x {BMP_ENTRADA_BYTES}")
    if ruins:
        raise RenderError(
            f"{REL_PASCAL_BMP} e os bitmaps do usuario divergem:\n     "
            + "\n     ".join(ruins))


def pascal_uniformes(formas: list[int],
                     kits: list[tuple[int, int, int, int]]) -> str:
    """A unidade gerada com as duas tabelas de `.data`."""
    linhas = [
        "{ wte_uniformes -- que arquivo de bandeira e de uniforme cada time usa.",
        "",
        "  GERADO por wte/tools/dump_render2d.py a partir de",
        "  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai",
        "  no gerador, e depois se regenera.",
        "",
        "  Sao as duas tabelas de `.data` da WTE-TASK-29, e elas respondem",
        "  perguntas diferentes. A COR de tudo aqui vem da imagem de CD; o que",
        "  estas tabelas dizem e a FORMA -- que estencil de bandeira, que",
        "  padrao de tecido.",
        "",
        f"  FORMA_PADRAO ({VA_TAB_FORMA:#010x}) e a bandeira *padrao* de cada",
        "  time, e o desenho NAO a usa: quem manda e o byte lido da imagem",
        "  (secao 3.2 do `wte/re/assets.md`). Ela existe para o combo de forma",
        "  do `ficha_color`, que indexa esta tabela em vez de digitar o numero,",
        "  e e por isso que os oito indices sem arquivo (44..51) nunca sao",
        "  pedidos.",
        "",
        f"  UNIFORMES ({VA_TAB_UNIFORME:#010x}) e a fonte real do desenho: a",
        "  forma da camisa NAO esta na imagem de CD, e um par fixo por time e",
        "  por jogo. `jogo` e 0 (Primeiro) ou 1 (Segundo). }",
        "unit wte_uniformes;",
        "",
        "{$mode objfpc}{$H+}",
        "",
        "interface",
        "",
        "const",
        f"  TIMES_TOTAL = {TIMES_N};",
        "",
        "  { A forma de bandeira padrao de cada time. }",
        "  FORMA_PADRAO: array[0..TIMES_TOTAL - 1] of Byte = (",
    ]
    def bloco(valores, por_linha=12):
        saida = []
        for i in range(0, len(valores), por_linha):
            pedaco = ", ".join(str(v) for v in valores[i:i + por_linha])
            fim = "," if i + por_linha < len(valores) else ""
            saida.append(f"    {pedaco}{fim}")
        return saida
    linhas += bloco(formas)
    linhas += [
        "  );",
        "",
        "  { `(camisa, calcao)` por time e por jogo: o indice 0 e o Primeiro",
        "    uniforme, o 1 e o Segundo. }",
        "type",
        "  TJogoDeUniforme = record",
        "    camisa: Byte;",
        "    calcao: Byte;",
        "  end;",
        "",
        "const",
        "  UNIFORMES: array[0..TIMES_TOTAL - 1, 0..1] of TJogoDeUniforme = (",
    ]
    for t, (c0, p0, c1, p1) in enumerate(kits):
        fim = "," if t < len(kits) - 1 else ""
        linhas.append(f"    ((camisa: {c0}; calcao: {p0}), "
                      f"(camisa: {c1}; calcao: {p1})){fim}")
    linhas += [
        "  );",
        "",
        "implementation",
        "",
        "end.",
    ]
    return "\n".join(linhas) + "\n"


def gera() -> dict[Path, str]:
    if not EXE.is_file():
        raise RenderError(f"{REL_EXE} nao existe.")
    blob = EXE.read_bytes()
    provas = confere_assinaturas(blob)
    desenhistas = confere_desenhistas(blob)
    do_exe = imediatos_do_exe(blob)
    confere_pascal(do_exe)
    confere_seek_da_paleta(blob, constantes_do_pascal()["BMP_CABECALHO"])
    contas, forma = bitmaps()
    confere_bmp(forma)
    confere_o_slot()
    formas, kits = tabelas(blob)
    cores = le_bytes(blob, VA_CORES_BANDEIRA, 2 * CORES_BANDEIRA_N)
    return {OUT_TSV: gera_tsv(provas, contas, forma, formas, kits),
            OUT_MD: gera_md(provas, desenhistas, contas, forma, cores,
                            formas, kits),
            OUT_PAS: pascal_uniformes(formas, kits)}


def gera_tsv(provas, contas: dict[str, int], forma: dict[str, int],
             formas: list[int], kits) -> str:
    out = ["secao\tchave\tvalor\tnota"]
    for va, padrao, prova in provas:
        texto = prova.replace("`", "").replace("**", "")
        out.append(f"assinatura\t{va:#010x}\t{padrao}\t{texto}")
    for chave, valor in sorted(contas.items()):
        out.append(f"bitmap\t{chave}\t{valor}\tcontado em we-team-editor/image")
    out.append(f"formato\tcabecalho\t{BMP_CABECALHO}\tbytes antes da paleta")
    out.append(f"formato\tentradas\t{BMP_ENTRADAS}\tde "
               f"{BMP_ENTRADA_BYTES} bytes cada")
    for va, _, papel, entradas, arquivos in DESENHISTAS:
        out.append(f"desenhista\t{va:#010x}\t{entradas}\t{papel}; "
                   f"arquivos={arquivos}")
    out.append(f"setor\tpayload\t{SETOR_PAYLOAD}\tlido e escrito pelo "
               f"exportador")
    out.append(f"setor\tresto\t{SETOR_RESTO}\tpulado: cabecalho + EDC/ECC")
    for chave, valor in sorted(forma.items()):
        out.append(f"recipiente\t{chave}\t{valor}\tmedido nos "
                   f"{contas['oito_bpp']} bitmaps de 8 bpp do usuario")
    out.append(f"tabela\t{VA_TAB_FORMA:#010x}\t{len(formas)}\tforma de "
               f"bandeira padrao por time; {len(set(formas))} distintas")
    out.append(f"tabela\t{VA_TAB_UNIFORME:#010x}\t{len(kits)}\t(camisa, "
               f"calcao) por time e jogo; passo 4 bytes")
    for t, (c0, p0, c1, p1) in enumerate(kits):
        out.append(f"uniforme\t{t}\t{c0},{p0},{c1},{p1}\tforma de bandeira "
                   f"padrao {formas[t]}")
    return "\n".join(out) + "\n"


def gera_md(provas, desenhistas, contas, forma, cores: bytes,
            formas: list[int], kits) -> str:
    o = []
    w = o.append
    w("# O render 2D — cor, aritmética e arredondamento\n")
    w(f"**GERADO** por [`dump_render2d.py`](../tools/dump_render2d.py) a partir "
      f"de\n`{REL_EXE}` e de `we-team-editor/image/`. Não edite à mão.\n")
    w("```sh\npython3 wte/tools/dump_render2d.py --check\n```\n")

    w("## As três perguntas que a task manda responder antes do código\n")
    w("O enunciado da\n"
      "[WTE-TASK-29](../../docs/tasks/29-camisa-e-bandeira-2d.md) é explícito:\n"
      "*\"descobrir qual antes de escrever código — muda o algoritmo inteiro\"*.\n"
      "As três têm resposta no `.text`, e nenhuma precisou de decompilador.\n")
    w("| pergunta | resposta | onde está a prova |\n"
      "|---|---|---|\n")
    w("| paleta ou varredura de pixel? | **paleta** | as três rotinas de "
      "desenho posicionam o arquivo em `0x36` e reescrevem as primeiras "
      "entradas; nenhuma toca um pixel |\n")
    w("| que espaço de cor no escurecer/clarear? | **nenhum** — a conta é na "
      "palavra BGR555 empacotada | `dec`/`sub 0x20`/`sub 0x400` no próprio "
      "`DWORD`, sem multiplicação e sem conversão |\n")
    w("| onde some a fidelidade do gradiente? | **no truncamento**, e o passo "
      "é float de precisão simples | `fstp DWORD` para o passo, e o "
      "arredondador põe `0xc01` no control word |\n")

    w("## A paleta é o meio, e o bitmap é só a forma\n")
    w(f"Os `.bmp` de 8 bpp trazem {BMP_CABECALHO} bytes de cabeçalho e\n"
      f"{BMP_ENTRADAS} entradas de {BMP_ENTRADA_BYTES} bytes. O `0x36` que as\n"
      "três rotinas de desenho usam é exatamente\n"
      f"{BMP_CABECALHO} — a **primeira entrada da paleta** —, e cada uma\n"
      "reescreve um punhado a partir dali. Medido na pasta do usuário:\n")
    w("| família | arquivos |\n|---|---:|\n")
    w(f"| bandeiras | {contas['bandeiras']} |\n")
    w(f"| camisas | {contas['camisas']} |\n")
    w(f"| calções | {contas['calcoes']} |\n")
    w(f"| **de 8 bpp** | **{contas['oito_bpp']}** |\n")
    w(f"| fora do padrão | {contas['fora']} |\n")
    w("Um único bitmap de 24 bpp na pasta quebraria a mecânica — o cabeçalho\n"
      "teria outro tamanho e `0x36` cairia no meio do pixel. Por isso a\n"
      "profundidade é **contada**, e não suposta.\n")
    w("### As três rotinas — e elas **não** reescrevem o mesmo tanto\n")
    w("| rotina | papel | arquivos | entradas por arquivo |\n"
      "|---|---|---:|---:|\n")
    for va, papel, entradas, arquivos in desenhistas:
        w(f"| `{va:#010x}` | {papel} | {arquivos} | {entradas} |\n")
    w("**A bandeira reescreve 16 entradas e o uniforme reescreve 15.** O laço\n"
      "do uniforme para em `cmp esi,0xf`, o da bandeira em `cmp esi,0x10`, e o\n"
      "uniforme roda o bloco inteiro duas vezes — uma para `camiseta<n>.bmp` e\n"
      "outra para `pantalon<n>.bmp`, cada uma com o seu `push 0x36`.\n")
    w("Vale registrar porque a seção 6 do [`assets.md`](assets.md) generalizou\n"
      "*\"idem, 16 entradas, por arquivo\"* para o uniforme, e são 15. A\n"
      "generalização é o erro fácil aqui: as três rotinas se parecem o\n"
      "bastante para alguém escrever um laço só, e o resultado seria uma\n"
      "entrada de paleta a mais escrita em toda camisa.\n")

    w("## A palavra de cor: BGR555, e o campo de cada canal\n")
    w(f"A fonte das cores da bandeira é `{VA_CORES_BANDEIRA:#010x}`, "
      f"{CORES_BANDEIRA_N} palavras\nde 16 bits.\n"
      f"O decodificador `{VA_DECODIFICA:#010x}` consome os cinco bits mais\n"
      "baixos primeiro e escreve o resultado no byte 0 do buffer de três; o\n"
      "escritor de paleta despeja esse buffer na ordem **2, 1, 0**, e a entrada\n"
      "de paleta BMP é `B, G, R, reservado`. Os dois fatos juntos fixam o\n"
      "mapeamento sem deixar margem:\n")
    w("| bits | canal | passo de um degrau |\n|---|---|---|\n")
    w("| 0–4 | R | `1` |\n")
    w("| 5–9 | G | `0x20` |\n")
    w("| 10–14 | B | `0x400` |\n")
    w("| 15 | não usado | — |\n")
    w("**A expansão de 5 para 8 bits é `v << 3`, e não replicação de bit\n"
      "alto.** Isso não é detalhe: `31 << 3` dá **248**, não 255, e é por isso\n"
      "que o teto do clarear é `0xF8`. Um port que expandisse com "
      "`v * 255 / 31`\nteria branco diferente do original em toda camisa "
      "clara.\n")

    w("## Escurecer e clarear: um degrau, na palavra empacotada\n")
    w("Nem RGB de 8 bits, nem HSL. Os dois handlers decodificam a palavra só\n"
      "para **testar o limite**, e depois somam ou subtraem direto no `DWORD`\n"
      "empacotado:\n")
    w("```text\n"
      "escurecer (0x004065fc):        clarear (0x00406744):\n"
      "  se R_expandido > 0:            se R_expandido < 0xF8:\n"
      "      palavra -= 1                   palavra += 1\n"
      "  se G_expandido > 0:            se G_expandido < 0xF8:\n"
      "      palavra -= 0x20               palavra += 0x20\n"
      "  se B_expandido > 0:            se B_expandido < 0xF8:\n"
      "      palavra -= 0x400              palavra += 0x400\n"
      "```\n")
    w("**O limite é testado no byte já expandido**, e o detalhe importa: o\n"
      "piso é `> 0` sobre o valor de 8 bits, que é o mesmo que `> 0` sobre o\n"
      "de 5. Mas o teto é `< 0xF8`, que só coincide com `< 31` porque a\n"
      "expansão é deslocamento. Trocar a expansão quebraria o teto junto.\n")
    w("Os dois percorrem a faixa selecionada — de `0x00433dcc` a\n"
      "`0x00433dd0` no vetor `0x00433dd4` —, não a paleta inteira.\n")

    w("## O gradiente, que é o risco nomeado da §9 do plano\n")
    w("A §9 dá probabilidade **média** para *\"render 2D não bate pixel a "
      "pixel\"*\ne nomeia a causa: arredondamento de gradiente. A causa está\n"
      "medida, e são **duas**:\n")
    w("1. **o passo é `Single`, não `Double`.** `fstp DWORD PTR [esi]` guarda\n"
      "   `(fim - início) / n` em precisão simples, e o acumulador também;\n"
      "2. **a conversão para inteiro trunca para zero.** O arredondador da RTL\n"
      "   (`0x00419d80`) põe `0xc01` no control word do 387 antes do `fistp`,\n"
      "   e os bits 10–11 em `11` são *round toward zero*. Não é `Round`, não\n"
      "   é meio-para-cima.\n")
    w("E a soma final não recompõe a palavra canal a canal — ela **soma os\n"
      "deslocamentos sobre a palavra de partida**:\n")
    w("```text\n"
      "passo[c] := Single(fim[c] - inicio[c]) / Single(n)\n"
      "acumulado[c] := 0\n"
      "para cada entrada entre as duas pontas:\n"
      "    acumulado[c] := acumulado[c] + passo[c]\n"
      "    palavra := palavra_inicial\n"
      "             + trunca(acumulado[0])\n"
      "             + trunca(acumulado[1]) shl 5\n"
      "             + trunca(acumulado[2]) shl 10\n"
      "```\n")
    w("Escrever isso como *\"interpola cada canal e reempacota\"* dá o mesmo\n"
      "resultado quase sempre — e diferente exatamente onde o truncamento\n"
      "morde. É a forma de errar que o plano previu.\n")

    w("## `grabar_camisetaClick` **não grava na imagem** — ele exporta\n")
    w(f"`{VA_EXPORTA_UNI:#010x}`. O enunciado da task dizia que este handler\n"
      "grava na imagem de CD e que por isso seria a segunda gravação a provar\n"
      "EDC/ECC. **Medido, não é.** Ele abre o destino em `\"wb\"`, lê da imagem\n"
      "e escreve no arquivo; a ROM sai intacta, e a mensagem de fim é\n"
      "`O uni foi salvo!!!.`\n")
    w(f"O laço de cópia é payload puro: `fread` de {SETOR_PAYLOAD}, `fwrite` "
      f"de\n{SETOR_PAYLOAD}, `fseek(+{SETOR_RESTO})`. E "
      f"{SETOR_PAYLOAD} + {SETOR_RESTO} = {SETOR_PAYLOAD + SETOR_RESTO}, que é "
      f"o setor MODE2/2352\ninteiro — ou seja, ele salta o cabeçalho e o "
      "EDC/ECC de cada setor em vez\nde copiá-los.\n")
    w("**Consequência para o gate:** o golden deste handler é do mesmo\n"
      "formato do [`golden-07-mcr`](../tests/roteiros/golden-07-mcr.txt) — a\n"
      "imagem tem de sair **intacta nos dois lados** e o `--artefato` compara o\n"
      "arquivo que cada lado emitiu. Comparar só as imagens aprovaria um port\n"
      "inerte. Quem grava textura **na** imagem é o\n"
      "[`boton_tex2isoClick`](spec/MainForm.boton_tex2isoClick.md), que já tem\n"
      "veredito `implementado`.\n")

    w("## As afirmações, uma a uma, contra o `.text`\n")
    w("Cada linha é um padrão de instrução que este gerador **procura** e sem\n"
      "o qual ele se recusa a emitir. Padrão que sumir é afirmação que\n"
      "caducou.\n")
    w("| rotina | bytes | o que prova |\n|---|---|---|\n")
    for va, padrao, prova in provas:
        w(f"| `{va:#010x}` | `{padrao}` | {prova} |\n")

    w("## O Pascal, e o que o segura no lugar\n")
    w(f"A aritmética está em [`{REL_PASCAL}`](../src/we2002_render.pas),\n"
      "**escrita à mão** — não há gerador possível para uma rotina. O que é\n"
      "gerado é a *conferência*: o `--check` deste script extrai os operandos\n"
      "das instruções acima e os compara com as constantes da unidade, um a\n"
      "um.\n")
    w("| constante do Pascal | de onde o `.exe` a entrega |\n|---|---|\n")
    w("| `RENDER_EXPANSAO` | o operando do `shl BYTE PTR [edx],<n>` |\n")
    w("| `RENDER_BITS` | o do `cmp esi,<n>` do laço de bits |\n")
    w("| `RENDER_CANAIS` | o do `cmp DWORD PTR [esp],<n>` |\n")
    w("| `RENDER_MAXIMO` | o do `cmp BYTE PTR [ebp+0x0],<n>` do clarear |\n")
    w("| `RENDER_PASSO_G` | o do `add DWORD PTR [ebx],<n>` |\n")
    w("| `RENDER_PASSO_B` | idem, em 32 bits |\n")
    w("| `PALETA_BANDEIRA`, `PALETA_UNIFORME` | o `cmp esi,<n>` de cada "
      "desenhista |\n")
    w("**`BMP_CABECALHO` é o único que não se extrai**, e a conferência dele\n"
      "vai na direção contrária: um `push imm8` sozinho não diz para que\n"
      "serve, e a rotina tem vários. Então o Pascal afirma 54 e o script exige\n"
      "que `push 54` esteja dentro das três rotinas de desenho.\n")
    w("E há um guard que não é sobre número: a unidade **não pode** conter\n"
      "`Round(acumulado` — o original trunca, e trocar isso é o risco da §9\n"
      "acontecendo em silêncio. As constantes da unidade são escritas como\n"
      "literal justamente para caber nesta leitura; a derivação\n"
      "(`RENDER_MAXIMO = 31 shl 3`) mora no comentário e é **executada** pelo\n"
      "[`test_render.pas`](../tests/test_render.pas).\n")

    w("## O recipiente: o que os 198 arquivos **são**\n")
    w("A conferência do parágrafo acima é contra o `.text`. Esta é contra a\n"
      "pasta do usuário, e a direção importa: o\n"
      "[`we2002_bmp.pas`](../src/we2002_bmp.pas) **recusa** um `.bmp` que não\n"
      "case com a forma abaixo, e uma constante errada ali faria o port\n"
      "recusar a pasta inteira em silêncio — tela em branco, sem erro, que é o\n"
      "pior modo de falhar.\n")
    w("| constante | valor | medido em |\n|---|---:|---|\n")
    for chave, valor in sorted(forma.items()):
        w(f"| `{chave}` | {valor} | os {contas['oito_bpp']} bitmaps de 8 bpp |\n")
    w(f"Os {forma['BMP_DADOS']} são "
      f"{BMP_CABECALHO} + {BMP_ENTRADAS} × {BMP_ENTRADA_BYTES}, e é o número\n"
      "que fecha o círculo com o `push 0x36`: a paleta só termina onde os\n"
      "pixels começam se ela tiver exatamente 256 entradas.\n")
    w("**O `bfOffBits` é conferido, e o original não o consulta.** Ele assume\n"
      "`0x36`. Um arquivo com outro valor faria a troca de paleta acertar o\n"
      "lugar errado — nos dois lados —, e é por isso que o port prefere\n"
      "recusar o arquivo a desenhá-lo torto.\n")

    w("## Que arquivo cada time usa: as duas tabelas de `.data`\n")
    w("A cor vem da imagem de CD. A **forma** vem daqui, e as duas tabelas\n"
      "respondem perguntas diferentes:\n")
    w("| tabela | tamanho | o que é | usada no desenho? |\n"
      "|---|---:|---|---|\n")
    w(f"| `{VA_TAB_FORMA:#010x}` | {len(formas)} bytes | forma de bandeira "
      f"*padrão* por time, {len(set(formas))} distintas | **não** |\n")
    w(f"| `{VA_TAB_UNIFORME:#010x}` | {len(kits)} × 4 bytes | `(camisa, "
      "calção)` por time e por jogo | **sim** |\n")
    w("A assimetria é o achado: **a forma da bandeira é lida da imagem de CD,\n"
      "e a da camisa não.** A tabela de bandeiras só alimenta o combo de forma\n"
      "do `ficha_color`, que a *indexa* em vez de digitar o número — e é por\n"
      "isso que os oito índices sem arquivo (44..51) nunca são pedidos. A de\n"
      "uniformes é a fonte real: nenhum byte do disco diz que padrão de tecido\n"
      "um time veste.\n")
    w("As duas saem para [`wte_uniformes.pas`](../src/wte_uniformes.pas), e\n"
      "este gerador **recusa** se qualquer índice que elas nomeiam não tiver\n"
      "arquivo em disco. Não é conferência de forma, é de alcance: índice sem\n"
      "arquivo seria tela em branco no port e `LoadFromFile` falho no\n"
      "original.\n")

    w("### E camisa e calção recebem o **mesmo** jogo de cores\n")
    w(f"O desenhista do uniforme monta o endereço das cores com\n"
      f"`lea ebx,[eax*8+{VA_KIT_EM_VIGOR:#010x}]`, onde `eax` é o jogo × 4 — "
      f"ou seja, passo de\n{KIT_PASSO} bytes, que são as "
      f"{KIT_PALAVRAS} palavras de um jogo. **A mesma\n"
      "instrução, com a mesma base, aparece nos dois laços**: o de\n"
      "`camiseta<n>.bmp` e o de `pantalon<n>.bmp`.\n")
    w("Não são dois conjuntos de cor, é um só aplicado a dois arquivos. Um\n"
      "port que guardasse cores de camisa e cores de calção em separado\n"
      "estaria inventando um grau de liberdade que o formato não tem — e a\n"
      "tela mostraria calção de cor errada assim que alguém editasse.\n")

    w("### E o uniforme começa na palavra **1**, não na 0\n")
    w("A assimetria contra a bandeira não é só de contagem — é de **início**, e\n"
      "essa metade não se vê olhando o laço. Os dois leem palavras de 16 bits\n"
      "em sequência; o que muda é onde a sequência começa dentro do bloco de\n"
      f"{KIT_PALAVRAS} palavras do time:\n")
    w("| desenhista | primeira palavra | quantas |\n|---|---:|---:|\n")
    w("| bandeira | 0 | 16 |\n")
    w("| uniforme | **1** | 15 |\n")
    w("**Foi medido de frente, e o original entregou a resposta de graça:** ele\n"
      "grava a paleta *dentro* do `.bmp` (seção 6 do [`assets.md`](assets.md)),\n"
      "então o arquivo que o oráculo deixou em disco **é** o resultado. Três\n"
      "pares (arquivo, time) independentes — `camiseta3`, `pantalon4`,\n"
      "`pantalon0` — casaram com `home_kit[1..15]` da camada de dados, e\n"
      "nenhum com `[0..14]`.\n")
    w("O `.text` explica por quê, e a explicação é de layout:\n")
    w(f"1. o carregador (`{VA_CARREGA_ESTADO:#010x}`) lê do disco `0x20` bytes "
      f"para\n   `{VA_KIT_LIDO:#010x}` e outros `0x20` para "
      f"`{VA_KIT_LIDO + 0x20:#010x}` — os dois jogos do\n   **slot 0**;\n"
      f"2. em seguida copia o slot inteiro, {SLOT_BYTES} bytes "
      f"(`{VA_COPIA_ESTADO:#010x}`, com\n"
      f"   `lea eax,[eax*8+{VA_KIT_LIDO:#010x}]`), para o **slot 1** — o "
      "rascunho que o\n   `ficha_color` edita;\n"
      f"3. o desenhista lê de `{VA_KIT_EM_VIGOR:#010x}`, que é exatamente\n"
      f"   `{VA_KIT_LIDO:#010x} + {SLOT_BYTES}`: o slot 1.\n")
    w("E o dado fecha a conta: **nos 190 conjuntos de uniforme das duas ROMs a\n"
      "palavra 0 é zero.** Ela não é cor, é enchimento — o `.exe` simplesmente\n"
      "começa na primeira cor de verdade. Já `flag_colours[15]` é zero nas 95, e\n"
      "o desenhista da bandeira **escreve** esse zero: entrada preta.\n")
    w("> **Este é o erro que a task previu, e o único que apareceu.** Um laço\n"
      "> compartilhado entre os três desenhistas erraria a contagem *e* o\n"
      "> início, e o resultado não é tela em branco — é uma camisa colorida com\n"
      "> as cores certas nos lugares errados, que passa por decisão de design\n"
      "> para quem não tiver o original ao lado.\n")

    w("## O que fica para o resto da task\n")
    w("Duas decisões já tomadas noutro lugar, e que este documento não\n"
      "reabre:\n")
    w("- **recolorir em memória**, e não reescrevendo o `.bmp` do usuário. A\n"
      "  recomendação é da seção 6.2 do [`assets.md`](assets.md); o original só\n"
      "  grava no arquivo porque a VCL de 2002 carregava paleta por\n"
      "  `LoadFromFile`. É o que a [`wte_render2d.pas`](../src/wte_render2d.pas)\n"
      "  faz;\n")
    w("- **`TLazIntfImage`**, não `Canvas.Pixels`. É o que a\n"
      "  [`wte_render2d.pas`](../src/wte_render2d.pas) usa, e o custo de um\n"
      "  redesenho está medido: o maior bitmap que este render toca tem\n"
      f"  {contas['maior_largura']}×{contas['maior_altura']} = "
      f"{contas['maior_em_pixels']} pixels, uma troca de time redesenha três\n"
      "  arquivos, e a troca de paleta em si são 45 bytes. O arquivo é lido do\n"
      "  disco uma vez e fica em memória — o original o relê a cada redesenho,\n"
      "  porque para ele o arquivo *é* o estado.\n")
    return arruma("".join(s if s.endswith("\n") else s + "\n" for s in o))


def arruma(texto: str) -> str:
    """Linha em branco onde o markdown precisa dela.

    Mesma ideia do `dump_mcr.py`, com duas quebras a mais: lista e cerca de
    codigo. O corpo e escrito em blocos curtos, um `w()` por paragrafo, e
    lembrar de um `\\n` solto em cada um deles seria a forma conhecida de
    esquecer um.

    O interruptor `dentro` existe para nao mexer no que esta DENTRO de uma
    cerca: ali o texto e literal, e uma linha em branco inventada mudaria o
    que o leitor ve.
    """
    saida: list[str] = []
    dentro = False
    fechou_cerca = False
    fechou_lista = False
    for linha in texto.splitlines():
        cerca = linha.startswith("```")
        if dentro:
            saida.append(linha)
            if cerca:
                dentro = False
                fechou_cerca = True
            continue
        anterior = saida[-1] if saida else ""
        titulo = linha.startswith("#")
        tabela = linha.startswith("|")
        lista = linha.startswith(("- ", "1. "))
        # ... e tambem DEPOIS: paragrafo colado no fim de uma lista ou de uma
        # cerca renderiza dentro dela.
        saiu_de_lista = (fechou_lista and not lista
                         and not linha.startswith(("  ", "2. ", "3. ")))
        precisa = (titulo or cerca or lista or saiu_de_lista or fechou_cerca
                   or (tabela and not anterior.startswith("|"))
                   or (anterior.startswith("|") and not tabela))
        if anterior.strip() and precisa:
            saida.append("")
        saida.append(linha)
        fechou_cerca = False
        fechou_lista = linha.startswith(("- ", "1. ", "2. ", "3. ", "  "))
        if cerca:
            dentro = True
    return "\n".join(saida) + "\n"


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de dump_render2d.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    print(f"{len(files)} arquivos em dia com {REL_EXE}; "
          f"{len(ASSINATURAS)} assinaturas conferidas no `.text`; "
          f"{REL_PASCAL} bate com os imediatos")
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
    except RenderError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
