#!/usr/bin/env python3
"""As 18 formacoes predefinidas do campinho tatico, e o que cada uma impoe.

Gera `wte/re/formacoes.md`, `wte/re/formacoes.tsv` e a unidade Pascal
`wte/src/wte_formacoes.pas` -- insumo da
[CORR-WTE-062](../../docs/tasks/CORR-WTE-062.md), que porta o
`estrategia.lista_formacionesClick`.

## O problema que ele resolve

Clicar num item de `lista_formaciones` move os dez jogadores de campo para as
posicoes daquela formacao e repinta os rotulos de posicao. O handler em si
(`0x00409aa0`) nao tem numero nenhum: ele so aponta **quatro ponteiros
globais** para dentro de uma tabela, e as duas auxiliares leem dali.

A tabela mora em `0x00433f0c` e **nao existe no arquivo** -- e `.bss`, montada
pelo `estrategia.FormCreate` com quatro `rep movsd` a partir de quatro blobs
contiguos de `.data`. Sao 18 registros de 44 bytes = 792, terminando
exatamente em `0x00434224`, que e o primeiro dos quatro ponteiros; a
contiguidade fecha o tamanho sem que ninguem precise supo-lo.

## Por que ferramenta, e nao transcricao

Sao **792 numeros**, e os quatro blobs sao *interleavados* na copia: o de
papel vai para `reg+0x00`, o de X para `reg+0x0b`, o de Y para `reg+0x16` e o
de zona para `reg+0x21`. Transcrever a olho troca X por Y sem que nada
reclame, e formacao errada so aparece para quem conhece o jogo -- e o mesmo
argumento do [`dump_zonas.py`](dump_zonas.py), com dezoito vezes mais numeros.

## O que ele decodifica

Quatro blobs de 198 bytes em `.data`, 18 x 11 cada:

| Endereco | Coluna | Faixa medida | Para que serve |
|---|---|---|---|
| `0x00423be4` | papel | 0..21 | indexa as 22 abreviaturas de `0x00423b8c` |
| `0x00423cb0` | x | 0..43 | `DestinoX = x*8 - 2`, em coordenada do `campo` |
| `0x00423d7c` | y | 0..87 | `DestinoY = ((y - 3) div 2)*5 - 7` |
| `0x00423e48` | zona | 0..10 | indexa as 11 `ZONAS` do `wte_zonas.pas` |

Mais a constante da animacao: um `long double` de 10 bytes em `0x004099b0`,
dentro da `.text`, logo apos o corpo de `0x004097d4`. Vale **0.2**, e com
quatro quadros isso cobre 80% do trajeto -- o ramo de encaixe do `relojTimer`
da o ultimo quinto de uma vez.

## As conferencias que abortam

0. **O nome diz a contagem.** `4 - 5 - 1  A` tem de ter quatro defensores,
   cinco de meio e um atacante entre os jogadores 1..10. O texto vem do `.lfm`
   e os papeis vem de `.data`: sao duas fontes, e e a unica conferencia que
   pega ordem de registro trocada ou coluna lida errada -- as faixas das quatro
   colunas se sobrepoem o bastante para que nenhuma das outras notasse.
1. **As quatro faixas.** `papel` tem de caber nas 22 abreviaturas e `zona` nas
   11 zonas do `wte_zonas.pas` -- que e outra fonte, gerada por outro script.
   Faixa estourada significa que o decodificador leu o blob errado.
2. **As posicoes cabem no `campo`.** Aplicadas as duas formulas, todo destino
   das bolas 1..10 tem de cair dentro do `campo` do `.lfm`. O indice 0, o
   goleiro, fica **de fora**: as tres rotinas do original iteram `1..10`, e o
   registro 0 de varias formacoes tem `x = y = 0`, que daria `(-2, -12)`.
3. **Os destinos caem na grade do arrasto.** `x*8 - 2` e congruente a 6 modulo
   8, e a grade do `rectanguloDragOver` tem passo 8 e fase 5 com raio 7:
   `5 - 7` tambem e 6 modulo 8. Idem no Y: `5k - 7` e 3 modulo 5.

   **Esta guarda e sobre as FORMULAS, nao sobre a tabela**, e vale dizer isso:
   as duas congruencias valem para QUALQUER byte, entao nenhum dado planta
   falha nela. O que ela confere e a coincidencia entre duas leituras
   independentes -- o `8`/`-2` saiu do `0x004097d4` e o `8`/`5`/`7` do
   `rectanguloDragOver`. Trocar uma das duas derruba, e e assim que o teste a
   exercita. Chama-la de conferencia do dado seria mentira.
4. **A constante e 0.2.** Decodificada do `long double` de 80 bits, nao
   escrita a mao.

Uso:

    python3 wte/tools/dump_formacoes.py            # regenera
    python3 wte/tools/dump_formacoes.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from dump_auxiliares import PE, DumpError

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
OUT_RE = ROOT / "wte" / "re"
OUT_PAS = ROOT / "wte" / "src" / "wte_formacoes.pas"

# As oito cores de radar de `0x00423624`, em BGR555 -- uma palavra por item do
# `ComboBox1`/`ComboBox2` do `estrategia`. Elas entram aqui, e nao num gerador
# proprio, porque sao da MESMA tela e do mesmo tipo de tabela de `.data` que as
# formacoes: quem abre o formulario precisa das duas (CORR-WTE-082).
#
# O `0x0040A0B4` nao usa a tabela como paleta -- ele a PERCORRE procurando o par
# de bytes que a imagem trouxe, e o indice que casar e o item que o combo
# seleciona. Por isso o que importa aqui e a ORDEM, nao o valor.
VA_CORES_RADAR = 0x00423624
CORES_RADAR_N = 8
LFM = ROOT / "wte" / "forms" / "ep2002_estrategia.lfm"
ZONAS_PAS = ROOT / "wte" / "src" / "wte_zonas.pas"
LEGENDAS_TSV = ROOT / "wte" / "re" / "legendas.tsv"

REL_EXE = "we-team-editor/we-team-editor.exe"
GERADOR = "wte/tools/dump_formacoes.py"

TSV_NAME = "formacoes.tsv"
MD_NAME = "formacoes.md"

# Os quatro blobs, na ordem em que o `FormCreate` os copia para dentro do
# registro de 44 bytes.
BLOBS = (
    ("papel", 0x00423BE4, 0x00),
    ("x",     0x00423CB0, 0x0B),
    ("y",     0x00423D7C, 0x16),
    ("zona",  0x00423E48, 0x21),
)

FORMACOES = 18
JOGADORES = 11
# O item `DEFAULT` da lista: o `ItemIndex` que o handler testa para
# desviar da tabela e ler o buffer da formacao viva do time.
FORMACAO_DEFAULT = 1
REGISTRO = 44                      # 4 x 11
TABELA = 0x00433F0C                # a base em .bss
FIM_DA_TABELA = 0x00434224         # o primeiro dos quatro ponteiros

# O `long double` de 80 bits com o passo da animacao, na `.text`.
PASSO_VA = 0x004099B0

# A grade do `rectanguloDragOver`, do `.aux.inc` -- repetida aqui de proposito
# para a conferencia 3 ter dois lados.
PASSO_X, FASE_X, PASSO_Y, RAIO = 8, 5, 5, 7

# A que linha do time cada abreviatura de posicao pertence. NAO e a regra de
# COR do `0x004099bc` -- aquela pinta `Zl` de vermelho junto com os atacantes,
# excentricidade do original que nao muda o que `Zl` e. Esta tabela existe para
# a conferencia 4, e nada no port a le.
LINHA_DA_POSICAO = {
    "Gl": "goleiro",
    "Za": "defesa", "Zl": "defesa", "Lib": "defesa", "Le": "defesa",
    "Ld": "defesa",
    "Vl": "meio", "Ae": "meio", "Ad": "meio", "Me": "meio",
    "At": "ataque", "Pe": "ataque", "Pd": "ataque",
}


def campo_do_lfm() -> tuple[int, int]:
    """(largura, altura) do `campo`, do formulario -- a outra fonte."""
    texto = LFM.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"object campo: TImage\b(.*?)\n(\s*)end", texto, re.S)
    if not m:
        raise DumpError(f"{LFM}: sem `object campo: TImage`")
    corpo = m.group(1)
    def prop(nome: str) -> int:
        p = re.search(rf"^\s*{nome} = (-?\d+)$", corpo, re.M)
        if not p:
            raise DumpError(f"{LFM}: `campo` sem `{nome}`")
        return int(p.group(1))
    return prop("Width"), prop("Height")


def zonas_declaradas() -> int:
    m = re.search(r"ZONAS_TOTAL = (\d+);", ZONAS_PAS.read_text(encoding="utf-8"))
    if not m:
        raise DumpError(f"{ZONAS_PAS}: sem `ZONAS_TOTAL`")
    return int(m.group(1))


def abreviaturas() -> list[str]:
    """As 22 de `0x00423b8c`, do `legendas.tsv` -- extraidas por outro script."""
    fora: list[tuple[int, str]] = []
    for linha in LEGENDAS_TSV.read_text(encoding="utf-8").splitlines():
        c = linha.split("\t")
        if c[0] != "resto":
            continue
        endereco = int(c[3], 16)
        if 0x00423B8C <= endereco < 0x00423B8C + 22 * 4:
            fora.append(((endereco - 0x00423B8C) // 4, c[5] if len(c) > 5 else ""))
    fora.sort()
    if [i for i, _ in fora] != list(range(22)):
        raise DumpError(
            f"wte/re/legendas.tsv: esperava as 22 cadeias de 0x00423b8c na "
            f"tabela `resto`, achei {len(fora)}")
    return [t for _, t in fora]


def long_double(b: bytes) -> float:
    """Decodifica um `long double` x87 de 80 bits."""
    if len(b) != 10:
        raise DumpError("long double precisa de 10 bytes")
    mantissa = int.from_bytes(b[:8], "little")
    expoente = int.from_bytes(b[8:10], "little")
    sinal = -1.0 if expoente >> 15 else 1.0
    return sinal * (mantissa / 2 ** 63) * 2.0 ** ((expoente & 0x7FFF) - 16383)


def varre(pe: PE) -> tuple[list[dict[str, list[int]]], float]:
    colunas: dict[str, list[int]] = {}
    for nome, va, _disp in BLOBS:
        off = pe.off(va)
        if off is None:
            raise DumpError(f"{REL_EXE}: {va:#010x} fora das secoes")
        b = pe.data[off:off + FORMACOES * JOGADORES]
        if len(b) != FORMACOES * JOGADORES:
            raise DumpError(f"{REL_EXE}: blob `{nome}` truncado em {va:#010x}")
        colunas[nome] = list(b)
    passo = pe.off(PASSO_VA)
    if passo is None:
        raise DumpError(f"{REL_EXE}: {PASSO_VA:#010x} fora das secoes")
    return ([{k: colunas[k][f * JOGADORES:(f + 1) * JOGADORES]
              for k in colunas} for f in range(FORMACOES)],
            long_double(pe.data[passo:passo + 10]))


def destino_x(x: int) -> int:
    return x * 8 - 2


def destino_y(y: int) -> int:
    # `idiv` trunca para zero, e o Python trunca para -inf: para y < 3 os dois
    # discordam, e e justamente onde o registro 0 mora.
    d = y - 3
    return (int(d / 2) if d < 0 else d // 2) * 5 - 7


def confere(formacoes: list[dict[str, list[int]]], passo: float) -> None:
    n_abrev = len(abreviaturas())
    n_zonas = zonas_declaradas()
    largura, altura = campo_do_lfm()
    if REGISTRO * FORMACOES != FIM_DA_TABELA - TABELA:
        raise DumpError(
            f"{GERADOR}: {FORMACOES} x {REGISTRO} nao fecha em "
            f"{FIM_DA_TABELA - TABELA} bytes entre {TABELA:#010x} e "
            f"{FIM_DA_TABELA:#010x}")
    for i, f in enumerate(formacoes):
        if i == FORMACAO_DEFAULT:
            # O registro 1 e um BURACO, e a isencao tem guarda propria: o
            # handler nunca o le -- `ItemIndex = 1` e o ramo que pega o buffer
            # da formacao viva do time (`0x00432e88`), nao a tabela. A prova
            # esta no dado: as quatro colunas dele sao zero, e um zero em `x`
            # daria destino -2. Se a linha deixar de ser zero, a isencao cai.
            if any(v for k in ("papel", "x", "y", "zona") for v in f[k]):
                raise DumpError(
                    f"{REL_EXE}: o registro {FORMACAO_DEFAULT} (`DEFAULT`) "
                    f"deixou de ser zero. Ele e o buraco do ramo que le o "
                    f"buffer do time; se tem dado, o handler pode le-lo e "
                    f"esta isencao esconde uma conferencia de verdade")
            continue
        for j in range(JOGADORES):
            p, z = f["papel"][j], f["zona"][j]
            if p >= n_abrev:
                raise DumpError(
                    f"{REL_EXE}: formacao {i}, jogador {j}: papel {p} e as "
                    f"abreviaturas de 0x00423b8c sao {n_abrev}")
            if z >= n_zonas:
                raise DumpError(
                    f"{REL_EXE}: formacao {i}, jogador {j}: zona {z} e o "
                    f"wte_zonas.pas declara {n_zonas}")
            if j == 0:
                continue          # o goleiro nao anda: as tres rotinas fazem 1..10
            dx, dy = destino_x(f["x"][j]), destino_y(f["y"][j])
            if not 0 <= dx < largura or not 0 <= dy < altura:
                raise DumpError(
                    f"{REL_EXE}: formacao {i}, jogador {j}: destino "
                    f"({dx}, {dy}) fora do campo de {largura}x{altura}")
            if dx % PASSO_X != (FASE_X - RAIO) % PASSO_X:
                raise DumpError(
                    f"{REL_EXE}: formacao {i}, jogador {j}: x {dx} fora da "
                    f"grade do arrasto (passo {PASSO_X}, fase "
                    f"{(FASE_X - RAIO) % PASSO_X})")
            if dy % PASSO_Y != (-RAIO) % PASSO_Y:
                raise DumpError(
                    f"{REL_EXE}: formacao {i}, jogador {j}: y {dy} fora da "
                    f"grade do arrasto (passo {PASSO_Y}, fase "
                    f"{(-RAIO) % PASSO_Y})")
    # 4. O NOME DIZ A CONTAGEM, e as duas fontes sao independentes: o texto
    #    vem do `.lfm` e os papeis vem de `.data`. `4 - 5 - 1 A` tem de ter
    #    quatro defensores, cinco de meio e um atacante entre os jogadores
    #    1..10. Se a ordem dos registros nao casasse com a ordem da lista, ou
    #    se a coluna lida nao fosse a de papel, isto cairia -- e nenhuma das
    #    outras tres conferencias pegaria.
    abrev = abreviaturas()
    for i, (f, nome) in enumerate(zip(formacoes, nomes_da_lista())):
        numeros = [int(n) for n in re.findall(r"\d", nome)]
        if len(numeros) != 3:
            continue          # `STOCK` e `DEFAULT` nao anunciam contagem
        conta = {"defesa": 0, "meio": 0, "ataque": 0, "goleiro": 0}
        for j in range(1, JOGADORES):
            linha = LINHA_DA_POSICAO.get(abrev[f["papel"][j]])
            if linha is None:
                raise DumpError(
                    f"{GERADOR}: a abreviatura `{abrev[f['papel'][j]]}` nao "
                    f"esta em LINHA_DA_POSICAO")
            conta[linha] += 1
        medido = [conta["defesa"], conta["meio"], conta["ataque"]]
        if medido != numeros:
            raise DumpError(
                f"{REL_EXE}: o registro {i} da lista se chama `{nome}` e os "
                f"papeis contam {medido[0]}-{medido[1]}-{medido[2]}. Ou a "
                f"ordem dos registros nao e a da lista, ou a coluna lida nao "
                f"e a de papel")

    if abs(passo - 0.2) > 1e-12:
        raise DumpError(
            f"{REL_EXE}: o passo da animacao em {PASSO_VA:#010x} decodifica "
            f"como {passo!r}, esperava 0.2")


def nomes_da_lista() -> list[str]:
    """Os itens de `lista_formaciones`, do `.lfm` -- para nomear as 18 linhas."""
    texto = LFM.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"object lista_formaciones: TListBox\b(.*?)\n(\s*)end", texto, re.S)
    if not m:
        raise DumpError(f"{LFM}: sem `lista_formaciones`")
    # O `.lfm` fecha o parenteses NA MESMA linha do ultimo item, e nao numa
    # linha propria -- foi o que derrubou a primeira versao deste recorte.
    itens = re.search(r"Items\.Strings = \((.*?)\)\s*$", m.group(1),
                      re.S | re.M)
    if not itens:
        raise DumpError(f"{LFM}: `lista_formaciones` sem `Items.Strings`")
    fora = re.findall(r"'([^']*)'", itens.group(1))
    if len(fora) != FORMACOES:
        raise DumpError(
            f"{LFM}: `lista_formaciones` tem {len(fora)} itens e a tabela tem "
            f"{FORMACOES} registros")
    return fora


def tsv(formacoes, nomes) -> str:
    fora = ["formacao\tnome\tjogador\tpapel\tabreviatura\tx\ty\tzona"
            "\tdestino_x\tdestino_y"]
    abrev = abreviaturas()
    for i, f in enumerate(formacoes):
        for j in range(JOGADORES):
            p = f["papel"][j]
            fora.append(
                f"{i}\t{nomes[i]}\t{j}\t{p}\t{abrev[p]}\t{f['x'][j]}\t"
                f"{f['y'][j]}\t{f['zona'][j]}\t{destino_x(f['x'][j])}\t"
                f"{destino_y(f['y'][j])}")
    return "\n".join(fora) + "\n"


def md(formacoes, nomes, passo) -> str:
    largura, altura = campo_do_lfm()
    fora = [
        "# `re/formacoes.md` — as 18 formações do campinho tático",
        "",
        "Produto da [CORR-WTE-062](../../docs/tasks/CORR-WTE-062.md). Gerado",
        f"por [`../tools/dump_formacoes.py`](../tools/dump_formacoes.py).",
        f"**Não editar à mão.** A tabela está em [`{TSV_NAME}`]({TSV_NAME}); a",
        "unidade Pascal é",
        "[`../src/wte_formacoes.pas`](../src/wte_formacoes.pas).",
        "",
        "## O que é",
        "",
        f"`lista_formaciones` tem **{FORMACOES}** itens e a tabela tem",
        f"**{FORMACOES}** registros de **{REGISTRO}** bytes — quatro colunas de",
        f"{JOGADORES} bytes cada. Ela vive em `{TABELA:#010x}`, **não existe no",
        "arquivo**, e é montada pelo `estrategia.FormCreate` com quatro",
        "`rep movsd` a partir de quatro blobs contíguos de `.data`. O fim dela",
        f"encosta em `{FIM_DA_TABELA:#010x}`, que é o primeiro dos quatro",
        "ponteiros globais — e é essa contiguidade que fecha o tamanho.",
        "",
        "| Blob | Coluna | Vai para | Faixa | Serve para |",
        "|---|---|---|---|---|",
    ]
    for nome, va, disp in BLOBS:
        vals = [f[nome][j] for f in formacoes for j in range(JOGADORES)]
        serve = {
            "papel": "indexa as 22 abreviaturas de `0x00423b8c`",
            "x": "`DestinoX = x × 8 − 2`",
            "y": "`DestinoY = ((y − 3) div 2) × 5 − 7`",
            "zona": "indexa as 11 `ZONAS` do `wte_zonas.pas`",
        }[nome]
        fora.append(f"| `{va:#010x}` | `{nome}` | `reg+{disp:#04x}` | "
                    f"{min(vals)}..{max(vals)} | {serve} |")
    fora += [
        "",
        "## O que o handler faz com isso",
        "",
        "`estrategia.lista_formacionesClick` (`0x00409aa0`) **não tem número**:",
        "ele aponta quatro ponteiros (`0x00434224`, `0x28`, `0x2c`, `0x30`) para",
        "dentro do registro escolhido e chama duas auxiliares. Uma calcula as",
        "seis tabelas da animação e liga o `reloj`; a outra pinta os onze",
        "`etiqposN`.",
        "",
        "O item **1** (`DEFAULT`) é o outro ramo: em vez da tabela, ele lê o",
        "buffer da formação viva do time (`0x00432e88`), que é preenchido por",
        "`0x0040a0b4` — rotina de abertura do formulário, portada como",
        "`PreencheTelaDeTatica` na `wte_tatica.pas` (CORR-WTE-082).",
        "",
        "## As três conferências que abortam",
        "",
        f"1. **Faixa.** `papel` cabe nas 22 abreviaturas e `zona` nas 11 zonas",
        "   do `wte_zonas.pas` — outra fonte, gerada por outro script.",
        f"2. **O destino cabe no `campo`**, que o `.lfm` diz ser",
        f"   {largura}×{altura}. O jogador 0 fica de fora: as três rotinas do",
        "   original iteram `1..10`, e vários registros trazem `x = y = 0`, que",
        "   daria `(−2, −12)`.",
        "3. **O destino cai na grade do arrasto.** `x × 8 − 2` é ≡ 6 (mod 8), e",
        "   a grade do `rectanguloDragOver` tem passo 8 e fase 5 com raio 7 —",
        "   `5 − 7` também é ≡ 6 (mod 8). No Y, `5k − 7` é ≡ 3 (mod 5). As",
        "   posições que a formação impõe caem **exatamente** onde o arrasto",
        "   solta a bola, e as duas leituras vieram de rotinas diferentes.",
        "",
        "## O passo da animação",
        "",
        f"`{PASSO_VA:#010x}` guarda um `long double` de 80 bits que vale",
        f"**{passo}**. Com os quatro quadros do `relojTimer` isso cobre",
        f"**{int(passo * 4 * 100)}%** do trajeto; o ramo de encaixe dá o último",
        f"quinto de uma vez. Não é correção de arredondamento de um pixel.",
        "",
        "## As 18 formações",
        "",
        "Posição do jogador 1 (o mais recuado dos dez de campo), para dar",
        "tamanho; a tabela inteira está no `.tsv`.",
        "",
        "| # | Nome | Papéis (0..10) | Zonas (0..10) |",
        "|--:|---|---|---|",
    ]
    abrev = abreviaturas()
    for i, f in enumerate(formacoes):
        papeis = " ".join(abrev[p] for p in f["papel"])
        zonas = " ".join(str(z) for z in f["zona"])
        fora.append(f"| {i} | `{nomes[i]}` | {papeis} | {zonas} |")
    fora.append("")
    return "\n".join(fora)


def cores_de_radar(pe) -> list[int]:
    """As oito palavras BGR555 de `0x00423624`, na ordem do combo."""
    o = pe.off(VA_CORES_RADAR)
    return [pe.data[o + 2 * i] | (pe.data[o + 2 * i + 1] << 8)
            for i in range(CORES_RADAR_N)]


def pas(formacoes, nomes, passo, radar) -> str:
    linhas = [
        "{ wte_formacoes -- as 18 formacoes predefinidas do campinho tatico.",
        "",
        "  GERADO por wte/tools/dump_formacoes.py a partir de",
        "  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai",
        "  no gerador, e depois se regenera.",
        "",
        f"  E a tabela que o `estrategia.FormCreate` monta em {TABELA:#010x} a",
        "  partir de quatro blobs de `.data`, e que o",
        "  `estrategia.lista_formacionesClick` indexa. Cada registro tem 44",
        "  bytes: quatro colunas de 11.",
        "",
        "  `x` e `y` NAO sao pixel: viram destino por",
        "  `DestinoX = x*8 - 2` e `DestinoY = ((y - 3) div 2)*5 - 7`, que e o",
        "  que o `0x004097d4` faz. `zona` indexa o `wte_zonas.pas`; `papel`",
        "  indexa as abreviaturas de posicao do `wte_legendas.pas`. }",
        "unit wte_formacoes;",
        "",
        "{$mode objfpc}{$H+}",
        "",
        "interface",
        "",
        "type",
        "  TFormacao = record",
        "    nome: string;",
        f"    papel: array[0..{JOGADORES - 1}] of Byte;",
        f"    x: array[0..{JOGADORES - 1}] of Byte;",
        f"    y: array[0..{JOGADORES - 1}] of Byte;",
        f"    zona: array[0..{JOGADORES - 1}] of Byte;",
        "  end;",
        "",
        "const",
        f"  FORMACOES_TOTAL = {FORMACOES};",
        f"  FORMACAO_JOGADORES = {JOGADORES};",
        "",
        "  { O `long double` de 80 bits em "
        f"{PASSO_VA:#010x}, decodificado. }}",
        f"  PASSO_DA_ANIMACAO = {passo};",
        "",
        "  { As 22 abreviaturas de posicao de 0x00423b8c, que a coluna",
        "    `papel` indexa. Elas NAO saem daqui: saem do `legendas.tsv`, do",
        "    `dump_legendas.py`, que ja as varria como tabela `resto` -- e",
        "    este gerador aborta se nao achar as 22. Uma cadeia, um dono. }",
        f"  POSICOES_TOTAL = {len(abreviaturas())};",
        "",
        "  POSICOES: array[0..POSICOES_TOTAL - 1] of string = (",
        "    " + ", ".join(f"'{t}'" for t in abreviaturas()),
        "  );",
        "",
        "  { AS OITO CORES DE RADAR de "
        f"{VA_CORES_RADAR:#010x}, em BGR555 -- uma por item dos dois combos",
        "    do `estrategia`. O `0x0040A0B4` NAO as usa como paleta: ele",
        "    percorre a tabela procurando o par de bytes que a imagem trouxe, e",
        "    o indice que casar e o item que o combo seleciona. O que importa",
        "    aqui e a ORDEM. }",
        f"  CORES_DE_RADAR_TOTAL = {CORES_RADAR_N};",
        "",
        "  CORES_DE_RADAR: array[0..CORES_DE_RADAR_TOTAL - 1] of Word = (",
        "    " + ", ".join(f"${v:04X}" for v in radar),
        "  );",
        "",
        "  FORMACOES: array[0..FORMACOES_TOTAL - 1] of TFormacao = (",
    ]
    for i, f in enumerate(formacoes):
        def vec(k):
            return "(" + ", ".join(str(v) for v in f[k]) + ")"
        fim = "," if i < FORMACOES - 1 else ""
        linhas += [
            f"    (nome: '{nomes[i]}';",
            f"     papel: {vec('papel')};",
            f"     x: {vec('x')};",
            f"     y: {vec('y')};",
            f"     zona: {vec('zona')}){fim}",
        ]
    linhas += [
        "  );",
        "",
        "implementation",
        "",
        "end.",
        "",
    ]
    return "\n".join(linhas)


def gera() -> dict[Path, str]:
    if not EXE.exists():
        raise DumpError(
            f"{REL_EXE} nao esta no disco. A pasta e do usuario e nao entra no "
            f"repositorio -- ver o CLAUDE.md.")
    pe = PE(EXE.read_bytes(), REL_EXE)
    formacoes, passo = varre(pe)
    confere(formacoes, passo)
    nomes = nomes_da_lista()
    return {
        OUT_RE / TSV_NAME: tsv(formacoes, nomes),
        OUT_RE / MD_NAME: md(formacoes, nomes, passo),
        OUT_PAS: pas(formacoes, nomes, passo, cores_de_radar(pe)),
    }


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: diverge do gerado")
        else:
            print(f"dump_formacoes: {rel}: ok")
    if ruins:
        print("ERRO: a arvore nao corresponde ao gerador:", file=sys.stderr)
        for r in ruins:
            print(f"  {r}", file=sys.stderr)
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
