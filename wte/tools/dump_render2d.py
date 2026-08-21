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


def bitmaps() -> dict[str, int]:
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
    for caminho in sorted(IMAGEM.rglob("*.bmp")):
        nome = caminho.name.lower()
        cab = caminho.read_bytes()[:54]
        if len(cab) < 54 or cab[:2] != b"BM":
            contas["fora"] += 1
            continue
        bpp, = struct.unpack_from("<H", cab, 28)
        if bpp == 8:
            contas["oito_bpp"] += 1
        else:
            contas["fora"] += 1
        if caminho.parent.name == "banderas":
            contas["bandeiras"] += 1
        elif caminho.parent.name == "uniformes2d":
            if nome.startswith("camiseta"):
                contas["camisas"] += 1
            elif nome.startswith("pantalon"):
                contas["calcoes"] += 1
    return contas


def gera() -> dict[Path, str]:
    if not EXE.is_file():
        raise RenderError(f"{REL_EXE} nao existe.")
    blob = EXE.read_bytes()
    provas = confere_assinaturas(blob)
    desenhistas = confere_desenhistas(blob)
    contas = bitmaps()
    cores = le_bytes(blob, VA_CORES_BANDEIRA, 2 * CORES_BANDEIRA_N)
    return {OUT_TSV: gera_tsv(provas, contas),
            OUT_MD: gera_md(provas, desenhistas, contas, cores)}


def gera_tsv(provas, contas: dict[str, int]) -> str:
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
    return "\n".join(out) + "\n"


def gera_md(provas, desenhistas, contas, cores: bytes) -> str:
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

    w("## O que fica para o Pascal\n")
    w("Duas decisões já tomadas noutro lugar, e que este documento não\n"
      "reabre:\n")
    w("- **recolorir em memória**, e não reescrevendo o `.bmp` do usuário. A\n"
      "  recomendação é da seção 6.2 do [`assets.md`](assets.md); o original só\n"
      "  grava no arquivo porque a VCL de 2002 carregava paleta por\n"
      "  `LoadFromFile`;\n"
      "- **`TLazIntfImage`**, não `Canvas.Pixels`. Com um punhado de entradas\n"
      "  de paleta o custo é irrisório de qualquer jeito, mas a regra vale para\n"
      "  quando o desenho crescer.\n")
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
          f"{len(ASSINATURAS)} assinaturas conferidas no `.text`")
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
