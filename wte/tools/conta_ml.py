#!/usr/bin/env python3
"""Os blocos livres de Master League: a tabela, a conta, e o limite do array.

Gera `wte/re/ml-slots.md`, `wte/re/ml-slots.tsv` e o include Pascal
`wte/src/we2002_ml_tabela.inc` -- insumo da
[WTE-TASK-33](../../docs/tasks/33-slots-de-master-league.md).

    python3 wte/tools/conta_ml.py                  # regera as tres saidas
    python3 wte/tools/conta_ml.py --check          # o que `make -C wte check` roda
    python3 wte/tools/conta_ml.py --medir <copia>  # conta numa imagem

O `--medir` escreve DUAS medicoes: `wte/re/ml-slots-medido.tsv`, uma linha por
imagem, e `wte/re/ml-slots-fora.tsv`, uma linha por indice alcancado fora do
vetor. A tabela de enderecos atropelados do markdown sai da segunda -- ja foi
literal no gerador, e listava um endereco que nenhuma imagem alcanca enquanto
escondia um que a europeia alcanca.

## O que e um bloco livre

O proprio original responde, no `Hint` do controle que mostra o numero
(`casilla_xmlibres`, `wte/re/dfm/MainForm.dfm`): *"Free blocks for new Master
League players"*. E o `we2002_core` nomeia o pool: `PLAYERS_NC = 462`, os
jogadores "non-contract" que ocupam `players[0..461]`, antes dos 1449 de
selecao. Bloco livre e indice de NC que nenhum vinculo de clube de ML reivindica.

## A rotina

`0x004042d4`, chamada de `MainForm.FormShow` (`0x004116df`) e de
`MainForm.boton_dialogo_weClick` (`0x0040c241`), as duas seguidas de
`casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])`:

    memset(0x00433224, 0, 462)          # a tabela de ocupacao -- ver abaixo
    WORD[0x004335c0] = 462
    fseek(arquivo, OFS_LINK_ML, SEEK_SET)
    para par = 0 ate 759:
        salta_fronteira_de_setor()
        b0 = fgetc(); b1 = fgetc()
        se par = 23: segue           # o par de enchimento entre ml_default e o clube 0
        se b1 <= 22: segue           # vinculo para jogador de selecao, nao bloco proprio
        i = prefixo[b0] + b1 - 23
        se WORD[0x00433224 + 2*i] = 0: WORD[0x004335c0] -= 1
        WORD[0x00433224 + 2*i] += 1

`prefixo[t]` e a soma de `CONTAGEM[0..t-1]`, feita a cada chamada pela
`0x0040423c` sobre a tabela de `0x00423424`.

## A tabela, e por que ela ja e conhecida

`0x00423424` sao 120 DWORDs: quantos jogadores NC cada time tem. A soma dos 120
da **462**, que fecha com o `PLAYERS_NC` do `we2002_core`.

O `ed.exe` guarda a MESMA tabela na outra codificacao: o `START_LINK[]` do
`src/core/Tables.cpp` sao os prefixos ja somados, e a formula do
`ResolveMlLink` (`slot + START_LINK[team] - 23`) e letra por letra a
`0x0040423c`. Este script confere as duas e **recusa** se divergirem num time
que tenha algum NC -- e a checagem cruzada entre os dois oraculos, de graca.

Onde elas divergem e onde a tabela nao esta definida: `START_LINK` escreve `0`
(e `-1` nos 32 clubes de ML) para time sem NC nenhum, enquanto o `wte.exe`
soma o prefixo de verdade. Nenhum vinculo valido endereca esses times.

## O array de 462 palavras, e o memset de 462 BYTES

A tabela de ocupacao vai de `0x00433224` a `0x004335bf` -- 462 palavras, 924
bytes -- e o contador mora logo depois, em `0x004335c0`, que e exatamente o
**indice 462**. O `memset` limpa `0x1ce` = 462 **bytes**, ou seja so as 231
primeiras palavras. Ver a secao "O que isso quebra" do markdown gerado.
"""

from __future__ import annotations

import re
import struct
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GERADOR = "wte/tools/conta_ml.py"

EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
REL_EXE = "we-team-editor/we-team-editor.exe"
TABLES = ROOT / "src" / "core" / "Tables.cpp"
REL_TABLES = "src/core/Tables.cpp"

OUT_MD = ROOT / "wte" / "re" / "ml-slots.md"
OUT_TSV = ROOT / "wte" / "re" / "ml-slots.tsv"
OUT_INC = ROOT / "wte" / "src" / "we2002_ml_tabela.inc"
MEDIDO = ROOT / "wte" / "re" / "ml-slots-medido.tsv"
FORA = ROOT / "wte" / "re" / "ml-slots-fora.tsv"

# --- o que o disassembly diz, e onde ---------------------------------------
VA_CONTAGEM = 0x00423424   # 120 DWORDs: NC por time
VA_OCUPACAO = 0x00433224   # a tabela de ocupacao, WORD por bloco
VA_CONTADOR = 0x004335C0   # WORD -- os blocos livres
TIMES = 120                # o tamanho de START_LINK no we2002_core
TOTAL = 462                # o imediato de 0x004042f1, e o PLAYERS_NC do core
PARES = 760                # o `cmp ebx,0x2f8` de 0x00404366
PAR_FILLER = 23            # o `cmp ebx,0x17 / je` de 0x0040432f
SLOT_MIN = 23              # o `cmp esi,0x16 / jle` de 0x00404334
MEMSET_BYTES = 462         # o `push 0x1ce` de 0x004042dd
OFS_LINK_ML = 2012680

# Os DWORDs que o `crash-causa.md` viu indo de `0x0` para `0x00010001` ao vivo,
# com a ROM europeia. Ficam aqui para o gerador CONFRONTAR o modelo com a
# medicao de processo, em vez de o markdown afirmar que os dois concordam.
#
# A transcricao de 2026-08-11 trazia tres, e a lista medida daqui apontou o
# quarto; a sessao refeita em 2026-08-20 (mesmo script, mesmo roteiro, copia
# nova da mesma ROM) mostrou o `0x004335f4` mudando no MESMO instante dos
# outros. Era falha de transcricao, nao de comportamento -- a janela do
# `--vizinhanca` e `0x00433580 + 0xc0` e sempre cobriu o endereco.
CRASH_DWORDS = (0x004335E4, 0x004335F4, 0x00433624, 0x00433628)

# O que se sabe morar em cada endereco atropelado. So o que TEM fonte: o
# `0x004335e4` e o global da rotina de realce (`crash-causa.md`, pergunta 3);
# os dois do bloco de `0x0043362x` sao vizinhos dele na mesma faixa de `.data`.
# O resto sai "nao identificado" em vez de ganhar rotulo inventado.
MORA = {
    0x004335E4: "o ponteiro de time da rotina de realce",
    0x004335E6: "a metade alta do mesmo DWORD",
    0x00433624: "vizinho do mesmo bloco",
    0x00433626: "vizinho do mesmo bloco",
    0x00433628: "vizinho do mesmo bloco",
    0x0043362A: "vizinho do mesmo bloco",
}

SETOR = 2352
DADOS_INICIO = 24
DADOS = 2048


class ContaError(Exception):
    pass


# ------------------------------------------------------------------ leitura --

def secoes(blob: bytes) -> list[tuple[int, int, int]]:
    """(va, tamanho_virtual, offset_no_arquivo) de cada secao do PE."""
    if blob[:2] != b"MZ":
        raise ContaError(f"{REL_EXE}: nao comeca com 'MZ'")
    pe = struct.unpack_from("<I", blob, 0x3C)[0]
    if blob[pe:pe + 4] != b"PE\0\0":
        raise ContaError(f"{REL_EXE}: assinatura PE ausente em {pe:#x}")
    n_sec, = struct.unpack_from("<H", blob, pe + 6)
    tam_opt, = struct.unpack_from("<H", blob, pe + 20)
    base = pe + 24 + tam_opt
    fora = []
    for i in range(n_sec):
        cab = base + 40 * i
        vsize, va, rsize, roff = struct.unpack_from("<IIII", blob, cab + 8)
        fora.append((va, max(vsize, rsize), roff))
    return fora


def le_dwords(blob: bytes, va: int, quantos: int) -> list[int]:
    imagem_base = 0x00400000
    for sec_va, tam, roff in secoes(blob):
        ini = imagem_base + sec_va
        if ini <= va < ini + tam:
            off = roff + (va - ini)
            return list(struct.unpack_from(f"<{quantos}I", blob, off))
    raise ContaError(f"{REL_EXE}: VA {va:#x} fora de toda secao")


def start_link_do_core() -> list[int]:
    if not TABLES.is_file():
        raise ContaError(f"{REL_TABLES} nao existe")
    m = re.search(r"const int START_LINK\[\]\s*=\s*\{(.*?)\};",
                  TABLES.read_text(encoding="utf-8"), re.S)
    if not m:
        raise ContaError(f"{REL_TABLES}: START_LINK[] nao encontrado")
    corpo = re.sub(r"//[^\n]*", "", m.group(1))
    vals = [int(x) for x in re.findall(r"-?\d+", corpo)]
    if len(vals) != TIMES:
        raise ContaError(f"{REL_TABLES}: START_LINK tem {len(vals)} entradas, "
                         f"esperado {TIMES}")
    return vals


# ------------------------------------------------------------------- a conta --

def prefixos(contagem: list[int]) -> list[int]:
    """O que a `0x0040423c` soma a cada chamada."""
    saida = [0] * len(contagem)
    for t in range(1, len(contagem)):
        saida[t] = saida[t - 1] + contagem[t - 1]
    return saida


def confere(contagem: list[int], pref: list[int], core: list[int]) -> None:
    """As duas codificacoes da mesma tabela tem de concordar onde ela existe.

    Separada de `gera()` porque guard que nunca foi visto recusar e guard que
    se SUPOE funcionar -- o `test_conta_ml.py` a chama com tabela plantada.
    """
    if sum(contagem) != TOTAL:
        raise ContaError(
            f"{REL_EXE}: a tabela de {VA_CONTAGEM:#x} soma {sum(contagem)}, "
            f"e o imediato de 0x004042f1 e {TOTAL}. Uma das duas leituras "
            "esta errada -- nao emito tabela que nao fecha.")
    ruins = [t for t in range(TIMES) if contagem[t] and pref[t] != core[t]]
    if ruins:
        raise ContaError(
            f"{REL_EXE} e {REL_TABLES} divergem em times COM jogadores NC: "
            f"{ruins[:8]}. Os dois oraculos tem de concordar onde a tabela "
            "esta definida.")


def indice_do_bloco(pref: list[int], b0: int, b1: int) -> int:
    """`0x0040423c`: prefixo[b0] + b1 - 23.

    `b0 >= 120` NAO e modelado. O original soma `[0x423424 + 4*t]` para todo
    `t < b0`, lendo alem do fim da tabela de 120 -- lixo, e a soma depende do
    que a `.data` guarda depois dela. Nenhuma das duas ROMs chega la -- o
    maior `b0` de cada imagem esta MEDIDO na coluna `max_b0` de
    `wte/re/ml-slots-medido.tsv`, e nao afirmado aqui --, e inventar uma regra
    produziria numero plausivel sem nada que o sustente. Quem chama trata o
    `None`.
    """
    if b0 >= len(pref):
        return None
    return pref[b0] + b1 - SLOT_MIN


def conta(dados: bytes, pref: list[int]) -> dict:
    """A `0x004042d4` sobre uma imagem inteira em memoria, ou um fatiador.

    `dados` responde a `__getitem__` de fatia -- basta um `bytes` ou um objeto
    que leia do arquivo. Devolve o que o contador vale e o que se viu chegar
    la, porque o numero sozinho nao diz se houve escrita fora do array.
    """
    pos = OFS_LINK_ML
    ocupacao: dict[int, int] = {}
    livres = TOTAL
    proprios = 0
    fora: dict[int, list[tuple[int, int, int]]] = {}
    nao_modelado: list[tuple[int, int, int]] = []
    # O maior `b0` entre os pares que CHEGAM a formula -- os que o filler e o
    # `b1 < 23` descartam nunca a alcancam, e um `b0` alto num deles nao diria
    # nada sobre o ramo nao modelado. `-1` quando nenhum par chega la.
    max_b0 = -1
    for par in range(PARES):
        if pos % SETOR == DADOS_INICIO + DADOS:
            pos += SETOR - DADOS
        b0, b1 = dados[pos], dados[pos + 1]
        pos += 2
        if par == PAR_FILLER or b1 < SLOT_MIN:
            continue
        proprios += 1
        max_b0 = max(max_b0, b0)
        i = indice_do_bloco(pref, b0, b1)
        if i is None:
            nao_modelado.append((par, b0, b1))
            continue
        if i >= TOTAL or i < 0:
            fora.setdefault(i, []).append((par, b0, b1))
        if ocupacao.get(i, 0) == 0:
            livres -= 1
        ocupacao[i] = ocupacao.get(i, 0) + 1
    return {"livres": livres, "proprios": proprios,
            "distintos": len(ocupacao), "fora": fora,
            "nao_modelado": nao_modelado, "max_b0": max_b0}


class ArquivoFatiavel:
    """`dados[pos]` lendo do disco, para nao carregar 474 MB."""

    def __init__(self, caminho: Path):
        self._f = caminho.open("rb")

    def __getitem__(self, pos):
        self._f.seek(pos)
        return self._f.read(1)[0]

    def close(self):
        self._f.close()


# ------------------------------------------------------------------- saidas --

COLUNAS_MEDIDO = 9   # ... tela_port, max_b0


def linhas_medidas() -> list[list[str]]:
    if not MEDIDO.is_file():
        return []
    linhas = MEDIDO.read_text(encoding="utf-8").splitlines()
    saida = [ln.split("\t") for ln in linhas[1:] if ln.strip()]
    curtas = [r[0] for r in saida if len(r) < COLUNAS_MEDIDO]
    if curtas:
        raise ContaError(
            f"{MEDIDO.relative_to(ROOT)}: {curtas[:4]} sem as "
            f"{COLUNAS_MEDIDO} colunas -- e medicao velha, de antes da coluna "
            "`max_b0`. Refaca com --medir, com as MESMAS copias e as MESMAS "
            "leituras de tela; nao complete a mao.")
    return saida


def enche(texto: str) -> str:
    """Paragrafo com quebra em 72, sem partir `nome-com-hifen` em crase."""
    return textwrap.fill(texto, width=72, break_on_hyphens=False,
                         break_long_words=False)


def linhas_fora() -> list[list[str]]:
    """Um indice alcancado por linha, como o `--medir` os escreveu."""
    if not FORA.is_file():
        return []
    linhas = FORA.read_text(encoding="utf-8").splitlines()
    return [ln.split("\t") for ln in linhas[1:] if ln.strip()]


def gera_tsv(contagem: list[int], pref: list[int], core: list[int]) -> str:
    saida = ["time\tnc\tprefixo_wte\tstart_link_core\tconcorda"]
    for t in range(TIMES):
        ok = "sim" if pref[t] == core[t] else "nao"
        saida.append(f"{t}\t{contagem[t]}\t{pref[t]}\t{core[t]}\t{ok}")
    return "\n".join(saida) + "\n"


def gera_inc(contagem: list[int]) -> str:
    corpo = []
    for i in range(0, TIMES, 10):
        fatia = ", ".join(f"{v:3d}" for v in contagem[i:i + 10])
        virgula = "," if i + 10 < TIMES else ""
        corpo.append(f"    {fatia}{virgula}   {{ times {i:3d}..{i + 9:3d} }}")
    return (
        "{ GERADO por " + GERADOR + " -- NAO EDITE A MAO.\n"
        "\n"
        f"  Quantos jogadores non-contract cada um dos {TIMES} times tem.\n"
        f"  Lida de `{VA_CONTAGEM:#010x}` do `{REL_EXE}`; a soma dos {TIMES} da\n"
        f"  {TOTAL}, que e o `PLAYERS_NC` do `we2002_core`.\n"
        "\n"
        "  O `wte.exe` soma o prefixo a cada chamada (`0x0040423c`); o\n"
        "  `ed.exe` guarda o prefixo pronto em `START_LINK[]`. O gerador\n"
        "  confere as duas codificacoes e recusa se divergirem onde a tabela\n"
        "  esta definida. }\n"
        "const\n"
        f"  ML_NC_POR_TIME: array[0..{TIMES - 1}] of LongWord = (\n"
        + "\n".join(corpo) + "\n"
        "  );\n")


def gera_md(contagem: list[int], pref: list[int], core: list[int]) -> str:
    divergem = [t for t in range(TIMES) if pref[t] != core[t]]
    com_nc = sum(1 for v in contagem if v)
    palavras = (VA_CONTADOR - VA_OCUPACAO) // 2
    limpas = MEMSET_BYTES // 2
    med = linhas_medidas()
    fora_med = linhas_fora()

    out: list[str] = []
    w = out.append
    w("# Os blocos livres de Master League\n")
    w("**GERADO** por [`conta_ml.py`](../tools/conta_ml.py) a partir de\n"
      f"`{REL_EXE}` e de [`{REL_TABLES}`](../../{REL_TABLES}).\n"
      "Nao edite a mao.\n")
    w("```sh\npython3 wte/tools/conta_ml.py --check\n```\n")

    w("## O que e um bloco livre\n")
    w("O original responde sozinho. O `Hint` do controle que mostra o numero\n"
      "diz **`Free blocks for new Master League players`**\n"
      "([`dfm/MainForm.dfm`](dfm/MainForm.dfm), `casilla_xmlibres`), e o\n"
      "`we2002_core` nomeia o pool: `PLAYERS_NC = 462`, os jogadores\n"
      "*non-contract* que ocupam `players[0..461]` antes dos 1449 de selecao.\n")
    w("> **Bloco livre e um indice de NC que nenhum par de vinculo de Master\n"
      "> League reivindica.**\n")
    w("Nao e byte zero nem nome em branco: e ausencia de referencia. Um bloco\n"
      "com nome preenchido mas sem vinculo apontando para ele conta como\n"
      "livre, e e assim que o original o oferece para jogador novo.\n")

    w("## A rotina, e os dois lugares que a chamam\n")
    w("| endereco | papel |\n|---|---|\n"
      f"| `0x004042d4` | conta os blocos livres e deixa o numero em `{VA_CONTADOR:#010x}` |\n"
      "| `0x0040423c` | `prefixo[time] + slot - 23` -- o indice linear do bloco |\n"
      "| `0x0040427c` | o inverso: do indice linear de volta ao par `(time, slot)` |\n")
    w("As duas chamadas a `0x004042d4` sao `MainForm.FormShow` (em\n"
      "`0x004116df`) e `MainForm.boton_dialogo_weClick` (em `0x0040c241`), e\n"
      "as duas seguem com\n"
      "`casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])` -- o campo\n"
      "`+0x434` do `MainForm`, pelo [`campos.tsv`](campos.tsv).\n")
    w("```text\n"
      f"memset({VA_OCUPACAO:#010x}, 0, {MEMSET_BYTES})\n"
      f"WORD[{VA_CONTADOR:#010x}] = {TOTAL}\n"
      f"fseek(arquivo, {OFS_LINK_ML}, SEEK_SET)          # OFS_LINK_ML\n"
      f"para par = 0 ate {PARES - 1}:\n"
      "    salta_fronteira_de_setor()\n"
      "    b0 = fgetc(); b1 = fgetc()\n"
      f"    se par = {PAR_FILLER}: segue\n"
      f"    se b1 < {SLOT_MIN}: segue\n"
      "    i = prefixo[b0] + b1 - 23\n"
      f"    se WORD[{VA_OCUPACAO:#010x} + 2*i] = 0: WORD[{VA_CONTADOR:#010x}] -= 1\n"
      f"    WORD[{VA_OCUPACAO:#010x} + 2*i] += 1\n"
      "```\n")

    w(f"### Os {PARES} pares, e por que {PARES}\n")
    w("A regiao de vinculo e um vetor unico para quem le pelo fluxo: 23 pares\n"
      "do `ml_default`, **um par de enchimento**, e 32 clubes de 23. Sao\n"
      f"23 + 1 + 736 = {PARES}. O enchimento aparece no `we2002_core` como a\n"
      "distancia entre `OFS_LINK_ML` (2012680) e `OFS_LINK_ML1` (2012728):\n"
      "48 bytes para 46 de conteudo. O `wte.exe` nao tem os dois offsets --\n"
      f"tem o `je` de `0x0040432f`, que pula o par {PAR_FILLER}.\n")
    w("A fronteira de setor cai **entre** pares, e nao dentro de um: de\n"
      "`OFS_LINK_ML` ate o fim do payload do setor 855 vao 352 bytes, 176\n"
      "pares exatos. Importa porque a rotina salta uma vez por iteracao e le\n"
      "os dois bytes seguidos -- um par impar-alinhado leria EDC/ECC no\n"
      "segundo byte.\n")

    w("## A tabela de `0x00423424`, e o mesmo dado no outro oraculo\n")
    w(f"{TIMES} DWORDs, um por time: quantos jogadores NC ele tem. **A soma dos\n"
      f"{TIMES} da {sum(contagem)}**, que fecha com o `PLAYERS_NC` do\n"
      f"`we2002_core`. {com_nc} times tem algum; o resto tem zero.\n")
    w("O `ed.exe` guarda a mesma tabela ja somada, no `START_LINK[]` do\n"
      f"[`{REL_TABLES}`](../../{REL_TABLES}), e o `ResolveMlLink` dele calcula\n"
      "`slot + START_LINK[team] - 23` -- letra por letra a `0x0040423c`.\n"
      "**Os dois concordam em todos os times que tem NC.** O gerador recusa se\n"
      "isso deixar de valer.\n")
    w(f"Divergem em {len(divergem)} times, todos com zero NC: o `START_LINK`\n"
      "escreve `0` (e `-1` nos 32 clubes de ML) onde a tabela nao esta\n"
      "definida, enquanto o `wte.exe` soma o prefixo de verdade. Vinculo\n"
      "valido nao endereca time sem NC -- ver a secao seguinte, que e o caso\n"
      "em que endereca.\n")
    w("A tabela inteira esta em [`ml-slots.tsv`](ml-slots.tsv).\n")

    w("## O que isso quebra: o `memset` limpa metade\n")
    w(f"A tabela de ocupacao vai de `{VA_OCUPACAO:#010x}` a\n"
      f"`{VA_OCUPACAO + 2 * palavras - 1:#010x}` -- {palavras} palavras, "
      f"{2 * palavras} bytes --\n"
      f"e o contador mora em `{VA_CONTADOR:#010x}`, que e **o indice {palavras}**.\n"
      f"O `memset` de `0x004042dd` limpa {MEMSET_BYTES} **bytes**: as {limpas}\n"
      "primeiras palavras, metade da tabela.\n")
    w("Na primeira chamada isso nao aparece -- a regiao esta alem do fim dos\n"
      "dados brutos da secao `.data`, entao o carregador a entrega zerada. Na\n"
      "**segunda** (abrir outra imagem, ou o `FormShow` seguido do botao) a\n"
      "metade de cima guarda a contagem da imagem anterior, o `dec` nao\n"
      "dispara para aqueles blocos, e o contador sai **alto demais**.\n")
    w("Nada disso e teoria: e a mesma classe de erro que o `newWe2002`\n"
      "documenta no `ed.exe` (o slot 64 de um vetor de 63), e a que a\n"
      "WTE-TASK-33 mandou medir em vez de estimar.\n")

    w("## Escrita fora do vetor, e a causa do travamento da ROM europeia\n")
    w("Quando `prefixo[b0] + b1 - 23` passa de 461, o `inc` escreve depois do\n"
      "fim da tabela, em dados vivos. **A tabela abaixo e MEDIDA**, uma linha\n"
      "por indice que as imagens de fato alcancam -- sai de\n"
      "[`ml-slots-fora.tsv`](ml-slots-fora.tsv), que o `--medir` escreve junto\n"
      "com a contagem.\n")
    if fora_med:
        w("| indice | endereco | par (time, slot) | imagem | o que mora la |\n"
          "|---:|---|---|---|---|\n")
        for r in sorted(fora_med, key=lambda x: (int(x[1]), x[0])):
            mora = MORA.get(int(r[2], 16), "nao identificado")
            w(f"| {r[1]} | `{r[2]}` | {r[4]}, {r[5]} | `{r[0]}` | {mora} |\n")
        dwords = sorted({int(r[2], 16) & ~3 for r in fora_med})
        ausentes = [d for d in dwords if d not in CRASH_DWORDS]
        w(enche(
            f"Sao {len(dwords)} DWORDs, que e a granularidade em que o "
            "[`crash-causa.md`](crash-causa.md) le a `.data`: "
            + ", ".join(f"`{d:#010x}`" for d in dwords) + ".") + "\n")
    else:
        w("**Sem medicao**: rode `--medir` sobre copias das duas imagens.\n")
    w(f"O indice {palavras} -- `{VA_CONTADOR:#010x}`, o proprio contador -- e o\n"
      "primeiro endereco depois do vetor, e por isso o alvo mais obvio. **Ele\n"
      "nao aparece acima**: e alcancavel em tese, e nao alcancado por nenhuma\n"
      "das duas imagens. A diferenca importa, porque atropelar o contador\n"
      "falsearia o proprio numero na tela, e nao e o que acontece.\n")
    w(enche(
        "[`crash-causa.md`](crash-causa.md) mediu, ao vivo e com a ROM "
        "europeia, " + ", ".join(f"`{d:#010x}`" for d in CRASH_DWORDS)
        + " mudando de `0x0` para `0x00010001`, e nao mudando com a japonesa, "
        "e encerrou dizendo que nomear a instrucao exigiria um watchpoint de "
        "hardware. **A instrucao e o `inc WORD PTR [eax*2+0x433224]` de "
        "`0x0040435d`**, aqui, e a condicao e vinculo apontando para time sem "
        "NC nenhum.") + "\n")
    if fora_med and not ausentes:
        w(enche(
            f"**Os {len(dwords)} DWORDs previstos sao os {len(dwords)} "
            "medidos ao vivo.** O confronto e feito por este gerador, entre a "
            "lista de `ml-slots-fora.tsv` e a que o `crash-causa.md` registrou "
            "-- e ja recusou concordar uma vez: a transcricao de 2026-08-11 "
            "tinha tres linhas, esta ferramenta apontou a quarta, e a sessao "
            "refeita em 2026-08-20 mostrou `0x004335f4` mudando no mesmo "
            "instante que as outras. Modelo que enumera o conjunto acha a "
            "linha que o olho perde no meio de vinte.") + "\n")
    if fora_med and ausentes:
        w("### Pergunta aberta: "
          + ", ".join(f"`{d:#010x}`" for d in ausentes)
          + "\n")
        w(enche(
            f"O modelo preve {len(dwords)} DWORDs atropelados e a medicao ao "
            f"vivo registrou {len(CRASH_DWORDS)}. Falta "
            + ", ".join(f"`{d:#010x}`" for d in ausentes)
            + ", que esta na tabela acima com par e imagem, e nao aparece no "
            "dump daquela sessao.") + "\n")
        w("Duas hipoteses, nenhuma medida: o dump foi recortado ao ser\n"
          "transcrito -- ele ja elide 16 palavras contiguas --, ou o endereco\n"
          "nao chega a ser escrito ao vivo. **Refazendo o dump, e este o\n"
          "endereco a olhar.** Fica como pergunta com nome, e nao como\n"
          "silencio: a alternativa era a tabela de tres linhas que este\n"
          "gerador escrevia a mao, que nao fechava com o `fora do vetor` da\n"
          "medicao ao lado.\n")
    w(enche(
        "A mesma medicao traz a confirmacao numerica de graca: ela leu "
        f"`{VA_CONTADOR:#010x}` indo a `0x0000000d` com a ROM europeia, e "
        "`0x0d` e **13** -- o mesmo que esta ferramenta calcula e o mesmo que "
        "o rotulo mostra. Um numero lido da memoria do processo em 2026-08-11, "
        "sem saber de quem era, batendo com a conta escrita aqui; a sessao de "
        "2026-08-20 leu o mesmo 13, de outro valor anterior (`0x154` contra "
        "`0xf5`), que e o `memset` de meia tabela deixando lixo diferente a "
        "cada corrida.") + "\n")

    if med:
        w("## Medido\n")
        w("| imagem | proprios | distintos | livres | fora do vetor | "
          "maior `b0` | tela do oraculo | tela do port |\n"
          "|---|---:|---:|---:|---:|---:|:-:|:-:|\n")
        for r in med:
            w(f"| `{r[0]}` | {r[2]} | {r[3]} | **{r[4]}** | {r[5]} | "
              f"{r[8]} | {r[6]} | {r[7]} |\n")
        w("As colunas de numero, ate `maior b0`, saem de\n"
          "`python3 wte/tools/conta_ml.py --medir <copia>`, que escreve\n"
          "[`ml-slots-medido.tsv`](ml-slots-medido.tsv). **Copia** -- `roms/`\n"
          "nao e alvo de ferramenta nenhuma.\n")
        w("As duas ultimas sao o que o rotulo `casilla_xmlibres` mostrou no\n"
          "`:99`, lido da captura: evidencia de **observacao de tela**, e a\n"
          "unica que fecha o circuito entre a conta e o que o usuario ve.\n")
        vistos = [(r[0], int(r[8])) for r in med if int(r[8]) >= 0]
        if vistos:
            maior = max(v for _, v in vistos)
            lista = ", ".join(f"{v} em `{n}`" for n, v in sorted(
                vistos, key=lambda x: -x[1]))
            w(f"### O ramo `b0 >= {TIMES}`, que nenhuma das duas alcanca\n")
            w(enche(
                f"A `0x0040423c` soma `[{VA_CONTAGEM:#010x} + 4*t]` para todo "
                f"`t < b0`. Com `b0 >= {TIMES}` ela le alem do fim da tabela "
                f"de {TIMES}, e a soma passa a depender do que a `.data` "
                "guarda depois dela -- lixo. **O port nao modela esse ramo**, "
                "e a justificativa e medida, nao afirmada: o maior `b0` visto "
                f"e **{maior}** ({lista}), o que deixa {TIMES - maior} de "
                f"folga ate o teto de {TIMES}.") + "\n")
            w("O numero sai da coluna `maior b0` da tabela acima, escrita pelo\n"
              "`--medir` sobre as mesmas copias -- entra no perimetro do\n"
              "`--check` e nao pode envelhecer sozinho. Ele conta so os pares\n"
              f"que CHEGAM a formula: o enchimento e os de `b1 < {SLOT_MIN}`\n"
              "sao descartados antes, e `b0` alto num deles nao diria nada\n"
              "sobre este ramo.\n")
        w("### O `-` da japonesa limpa, e o que ele revelou\n")
        w("**O oraculo altera a imagem ao abri-la**, e a alteracao muda a\n"
          "propria conta. Duas corridas com copia nova da japonesa deixaram o\n"
          "arquivo com DOIS bytes trocados em `2012984` -- o par de vinculo do\n"
          "clube de ML 5, slot 13, de `(102, 23)` para `(0, 27)`. O time 102\n"
          "nao tem NC nenhum, entao `(102, 23)` e referencia pendurada; a\n"
          "troca a aponta para um bloco que ja estava ocupado, e por isso o\n"
          "numero de distintos sobe de 460 para 461 e o de livres cai de 2\n"
          "para 1.\n")
        w("Nao ha como o oraculo mostrar o numero da imagem limpa: quando o\n"
          "rotulo aparece, o arquivo dele ja mudou. O confronto direto esta na\n"
          "linha `ml-jp-pos-oraculo.bin`, que e a copia do arquivo QUE O\n"
          "ORACULO PRODUZIU dada ao port -- os dois mostram `1`.\n")
        w("**Essa escrita ja estava registrada, sem significado.** A spec do\n"
          "[`boton_dialogo_weClick`](spec/MainForm.boton_dialogo_weClick.md)\n"
          "a lista desde a WTE-TASK-25 entre as *duas faixas do arranque que\n"
          "continuam sem explicacao* -- `1921862..1921862` e\n"
          "`2012984..2012985` --, declaradas `conhecida:` no roteiro do gate\n"
          "porque o oraculo as grava e o port nao. O que esta medicao\n"
          "acrescenta e o SIGNIFICADO da segunda: sao os dois bytes de um par\n"
          "de vinculo, e trocar `(102, 23)` por `(0, 27)` custa um bloco\n"
          "livre.\n")
        w("**Quem escreve fechou em 2026-08-20**, na oitava passagem da\n"
          "[WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md):\n"
          "`0x0040c19e` no `boton_dialogo_weClick` e `0x00411616` no\n"
          "`FormShow`, com o endereco IMEDIATO no `.text` (`push 0x1eb738`).\n"
          "E por isso que procurar por `OFS_LINK_ML` nunca os achou -- a unica\n"
          "referencia a esse offset em toda a `.text` e o `push 0x1eb608` de\n"
          "`0x004042fc`, desta rotina, que so LE.\n")
        w("O remendo e condicional (`(102, >22)` vira `(0, 27)`) e portanto\n"
          "idempotente, e fica FORA da guarda da sentinela de injecao: o `je`\n"
          "de `0x0041158e` salta justamente para onde ele comeca. Esta portado\n"
          "no `we2002_estado` como `PatchDeVinculoDeArranque`, e com ele os\n"
          "dois lados passaram a ter o MESMO conjunto de blocos livres -- que\n"
          "e a condicao de o ramo de alocacao da `0x00404820` poder ser\n"
          "medido.\n")

    w("## O port\n")
    w("[`we2002_ml.pas`](../src/we2002_ml.pas), com a tabela em\n"
      "[`we2002_ml_tabela.inc`](../src/we2002_ml_tabela.inc), tambem gerado\n"
      "daqui. Ele reproduz a conta, **e nao reproduz o estouro**: o indice\n"
      f"fora de `0..{TOTAL - 1}` e contado num dicionario a parte, entao o\n"
      "numero na tela e o mesmo do original e nenhuma variavel vizinha e\n"
      "atingida. Divergencia deliberada, para a\n"
      "[WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md).\n")
    return "".join(s if s.endswith("\n") else s + "\n" for s in out)


# --------------------------------------------------------------------- main --

def gera() -> dict[Path, str]:
    if not EXE.is_file():
        raise ContaError(
            f"{REL_EXE} nao existe.\n"
            "     Esse editor nao e versionado; ponha a pasta na raiz.")
    blob = EXE.read_bytes()
    contagem = le_dwords(blob, VA_CONTAGEM, TIMES)
    pref = prefixos(contagem)
    core = start_link_do_core()
    confere(contagem, pref, core)
    return {OUT_TSV: gera_tsv(contagem, pref, core),
            OUT_INC: gera_inc(contagem),
            OUT_MD: gera_md(contagem, pref, core)}


def do_check(files: dict[Path, str]) -> int:
    ruins = []
    for caminho, conteudo in sorted(files.items()):
        rel = caminho.relative_to(ROOT)
        if not caminho.exists():
            ruins.append(f"{rel}: nao existe")
        elif caminho.read_text(encoding="utf-8") != conteudo:
            ruins.append(f"{rel}: difere do que o gerador produz")
    if ruins:
        print("saida de conta_ml.py fora de dia:", file=sys.stderr)
        for r in ruins:
            print("  " + r, file=sys.stderr)
        print(f"rode: python3 {GERADOR}", file=sys.stderr)
        return 2
    print(f"{len(files)} arquivos em dia com {REL_EXE} + {REL_TABLES}")
    return 0


def do_write(files: dict[Path, str]) -> int:
    for caminho, conteudo in sorted(files.items()):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {caminho.relative_to(ROOT)}: {conteudo.count(chr(10))} linhas")
    return 0


def do_medir(caminhos: list[str]) -> int:
    blob = EXE.read_bytes()
    contagem = le_dwords(blob, VA_CONTAGEM, TIMES)
    pref = prefixos(contagem)
    linhas = ["imagem\tbytes\tproprios\tdistintos\tlivres\tfora_do_vetor\t"
              "tela_oraculo\ttela_port\tmax_b0"]
    # Um indice por linha, e nao uma coluna com lista dentro: quem alcanca o
    # que fora do vetor e a tabela que o markdown desenha, e lista espremida
    # numa celula de TSV volta a ser texto para parsear.
    fora_linhas = ["imagem\tindice\tendereco\tpar\tb0\tb1"]
    for c in caminhos:
        # `<copia>[=<tela_oraculo>/<tela_port>]` -- o que o rotulo
        # `casilla_xmlibres` mostrou de cada lado com ESTE conteudo. E
        # observacao de tela, e entra aqui para o markdown nao ter numero
        # digitado a mao. `-` onde nao houve leitura.
        tela_o = tela_p = "-"
        if "=" in c:
            c, telas = c.split("=", 1)
            partes = telas.split("/")
            tela_o = partes[0] or "-"
            tela_p = partes[1] if len(partes) > 1 and partes[1] else "-"
        p = Path(c)
        if not p.is_file():
            print(f"ERRO: {c} nao existe", file=sys.stderr)
            return 2
        if p.resolve().parent == (ROOT / "roms").resolve():
            print(f"ERRO: {c} esta em roms/. Use uma copia -- regra do "
                  "repositorio.", file=sys.stderr)
            return 2
        dados = ArquivoFatiavel(p)
        try:
            r = conta(dados, pref)
        finally:
            dados.close()
        linhas.append(f"{p.name}\t{p.stat().st_size}\t{r['proprios']}\t"
                      f"{r['distintos']}\t{r['livres']}\t{len(r['fora'])}\t"
                      f"{tela_o}\t{tela_p}\t{r['max_b0']}")
        print(f"  {p.name}: livres={r['livres']} proprios={r['proprios']} "
              f"distintos={r['distintos']} fora={len(r['fora'])} "
              f"max b0={r['max_b0']}")
        for i in sorted(r["fora"]):
            print(f"      fora: indice {i} -> {VA_OCUPACAO + 2 * i:#010x} "
                  f"pares {r['fora'][i]}")
            for par, b0, b1 in r["fora"][i]:
                fora_linhas.append(
                    f"{p.name}\t{i}\t{VA_OCUPACAO + 2 * i:#010x}\t{par}\t"
                    f"{b0}\t{b1}")
        if r["nao_modelado"]:
            print(f"      AVISO: {len(r['nao_modelado'])} pares com b0 >= "
                  f"{TIMES} -- fora do que a tabela define, nao contados: "
                  f"{r['nao_modelado'][:4]}")
    MEDIDO.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(f"  {MEDIDO.relative_to(ROOT)}: {len(linhas) - 1} imagens")
    FORA.write_text("\n".join(fora_linhas) + "\n", encoding="utf-8",
                    newline="\n")
    print(f"  {FORA.relative_to(ROOT)}: {len(fora_linhas) - 1} indices")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--medir":
        if len(argv) < 2:
            print(f"uso: {GERADOR} --medir <copia.bin> [...]", file=sys.stderr)
            return 2
        try:
            return do_medir(argv[1:])
        except ContaError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GERADOR} [--check] | {GERADOR} --medir <copia.bin>",
                  file=sys.stderr)
            return 2
    try:
        files = gera()
    except ContaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
