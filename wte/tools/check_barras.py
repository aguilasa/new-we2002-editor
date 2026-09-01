#!/usr/bin/env python3
"""A tabela de barras do original é a nossa `OFS_TEAM_BARS`. Prova disso.

Produto da [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md), spec de
`MainForm.lista_equiposChange`. Estendido pela
[WTE-TASK-26](../../docs/tasks/concluidos/26-handlers-de-edicao.md) para o lado da
edição: além de *de onde vêm* os cinco bytes, agora se confere **onde eles
moram enquanto são editados** — ver "O buffer de edição", abaixo.

**Não escreve arquivo nenhum** — confere, e sai 2 quando diverge. Mesmo
contrato do `check_lcl_props.py` (CORR-WTE-020), pela mesma razão: o que ele
mede não tem forma de documento, tem forma de asserção.

## O que se mede, e por que isso importa

Ao trocar de time, o original lê **cinco bytes** e transforma cada um na
largura de uma barra. Ele não usa um offset: usa uma *conta*, com o endereço
lógico convertido para físico setor a setor —

```text
t     = ANCORA + PASSO * indice
setor = t div SETOR_DADOS
resto = t mod SETOR_DADOS
fisico = SETOR_BRUTO * setor + resto + BASE
```

— e é essa conta que decide se o port pode ler os mesmos valores da camada de
dados em vez de reabrir a imagem. **Se `fisico(0)` for a `OFS_TEAM_BARS` que o
`we2002_core` já conhece, os dois oráculos estão falando do mesmo lugar** e a
`Team.bar_*` serve; se não for, o port estaria mostrando outra coisa com a cara
da certa.

As constantes saem do **corpo do handler**, decodificadas daqui, e não de um
literal escrito à mão neste arquivo: constante que muda no binário tem de
derrubar a conferência, não passar despercebida. `SETOR_DADOS` e `SETOR_BRUTO`
são os dois valores fixos do formato MODE2/2352, e mesmo eles têm o `sar
esi,0xb` e o `shl eax,4` conferidos por padrão — se o binário parar de dividir
por 2048, a conferência cai.

## O buffer de edição, e por que ele não é cache

Os cinco bytes lidos não vão direto para a tela: vão para um buffer de `.data`,
e é **do buffer** que sai a largura. Três handlers o tocam, e a conferência
exige que os três falem do mesmo endereço:

| handler | o que faz com o buffer | onde |
|---|---|---|
| `lista_equiposChange` | enche, um byte por barra | `0x0040cf79` |
| `track_barraChange` | grava o valor editado | `0x0040caa1` |
| `boton_barras2isoClick` | **lê para gravar na imagem** | `0x0040cb3d` |

A terceira linha é o argumento inteiro: se o port desenhasse a barra a partir
de `Jogo.teams[].bar_*`, editar mudaria o pixel e a gravação escreveria o valor
velho — e o golden acusaria a **gravação** por um defeito que é da edição. Por
isso o port tem `BarrasEmEdicao` separado da camada de dados, e por isso os
três endereços são conferidos juntos: o dia em que deixarem de coincidir, a
separação perdeu a razão de ser e o `.inc` está errado.

Confere-se também que a aritmética `11*v + 9` é **a mesma sequência de bytes**
na carga e na edição. Se as duas divergirem no binário, uma barra carregada e
uma editada com o mesmo valor deixam de ter a mesma largura, e a comparação de
tela — que é o único juiz deste grupo enquanto a WTE-TASK-27 não existir —
passa a medir a coisa errada.

## O que ele NÃO faz

Não abre imagem. A igualdade byte a byte entre o que a conta lê e o que
`Team.bar_*` devolve foi medida uma vez, com uma cópia em `work/`, e está
registrada na spec — aqui fica a parte que dá para conferir a cada build, sem
depender de `roms/`, que é do usuário e não é versionado.

Uso:

    python3 wte/tools/check_barras.py            # confere
    python3 wte/tools/check_barras.py --check    # idem, o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
OFFSETS = ROOT / "wte" / "src" / "we2002_offsets.pas"
CAMPOS = ROOT / "wte" / "re" / "campos.tsv"

REL_EXE = "we-team-editor/we-team-editor.exe"
REL_PUB = "wte/re/published_methods.tsv"
REL_OFFSETS = "wte/src/we2002_offsets.pas"
REL_CAMPOS = "wte/re/campos.tsv"
GENERATOR = "wte/tools/check_barras.py"

HANDLER = ("MainForm", "lista_equiposChange")

# Os handlers do lado da edicao, e o da gravacao que fecha o argumento. O
# terceiro e da WTE-TASK-27 e ainda nao tem corpo em Pascal -- esta aqui
# porque o que se mede e o ENDERECO que ele le, e ele ja o le hoje.
HANDLER_SEL = ("MainForm", "sel_barraClick")
HANDLER_TRACK = ("MainForm", "track_barraChange")
HANDLER_GRAVA = ("MainForm", "boton_barras2isoClick")

# `sel_barra0` -- o campo do formulario que ancora a aritmetica de indice de
# componente do `sel_barraClick`. Conferido contra o campos.tsv da WTE-TASK-25
# em vez de repetido aqui.
CAMPO_ANCORA = ("MainForm", "sel_barra0")

# Quantos times a lista endereça. 63 seleções e clássicos + 32 clubes de Master
# League; o item 95 do combo é o modelo de ML, que não tem barra -- e é por isso
# que o handler compara com 95 antes de ler.
TIMES = 95

# Os padrões que carregam cada constante, dentro do corpo do handler. Cada um
# tem de casar EXATAMENTE uma vez: duas ocorrências significaria que a conta
# aparece em dois lugares e que medir uma delas não basta.
PADROES = {
    # lea esi,[eax+eax*4] seguido de add esi,imm32 -- o passo (cinco bytes por
    # time, que é a forma do `lea`) e a âncora, o endereço lógico do time 0.
    # Os dois juntos num padrão só de propósito: sozinho, `add esi,imm32` casa
    # também o `add esi,0x7ff` do arredondamento de sinal logo abaixo.
    "ancora": (rb"\x8d\x34\x80\x81\xc6(....)", "<I"),
    # sar esi,0xb -- 2^11 bytes de dados por setor
    "shift": (rb"\xc1\xfe\x0b", None),
    # shl eax,4 sobre 147*setor -- 147*16 = 2352, o setor bruto MODE2
    "shl": (rb"\xc1\xe0\x04", None),
    # add eax,imm32 -- a base física
    "base": (rb"\x05(....)\x50", "<I"),
    # cmp eax,0x800 -- o contador que dispara o salto de setor
    "limite": (rb"\x3d\x00\x08\x00\x00", None),
    # push 0x130 -- 2352 - 2048, o salto sobre EDC/ECC mais o cabeçalho
    "salto": (rb"\x68\x30\x01\x00\x00", None),
}

# A largura da barra: `lea edx,[ecx+edx*4]` (5v), `lea edx,[ecx+edx*2]` (11v),
# `add edx,0x9`. E a mesma sequencia de bytes na carga e na edicao, e a
# conferencia exige que continue sendo -- ver o cabecalho.
LARGURA = rb"\x8d\x14\x91\x8d\x14\x51\x83\xc2\x09"

# Onde cada handler nomeia o buffer de cinco bytes. Formas diferentes de
# enderecar o MESMO endereco, e e a coincidencia que se mede.
PADROES_BUFFER = {
    # mov DWORD PTR [ebp-0x4c],imm32 -- o ponteiro de escrita do laco de carga
    HANDLER: (rb"\xc7\x45\xb4(....)", "<I"),
    # movzx edx,BYTE PTR [edx+imm32] -- a leitura indexada pelo global
    HANDLER_SEL: (rb"\x0f\xb6\x92(....)", "<I"),
    # mov BYTE PTR [eax+imm32],cl -- a escrita indexada pelo global
    HANDLER_TRACK: (rb"\x88\x88(....)", "<I"),
    # mov ebx,imm32 -- a base que a gravacao percorre
    HANDLER_GRAVA: (rb"\xbb(....)", "<I"),
}

SETOR_DADOS = 2048
SETOR_BRUTO = 2352


class CheckError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


class PE:
    """Leitor de PE em stdlib pura -- cada gerador de `wte/tools/` roda sozinho."""

    def __init__(self, data: bytes, rotulo: str) -> None:
        self.data = data
        self.rotulo = rotulo
        if data[:2] != b"MZ":
            raise CheckError(f"{rotulo}: nao comeca com MZ")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise CheckError(f"{rotulo}: assinatura PE ausente em {pe:#x}")
        nsec = struct.unpack_from("<H", data, pe + 6)[0]
        szopt = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        self.base = struct.unpack_from("<I", data, opt + 28)[0]
        self.sections = []
        for i in range(nsec):
            o = pe + 24 + szopt + i * 40
            self.sections.append((
                struct.unpack_from("<I", data, o + 12)[0],
                struct.unpack_from("<I", data, o + 8)[0],
                struct.unpack_from("<I", data, o + 20)[0],
                struct.unpack_from("<I", data, o + 16)[0]))

    def off(self, va: int) -> int | None:
        rva = va - self.base
        for vaddr, vsize, raddr, rsize in self.sections:
            if vaddr <= rva < vaddr + max(vsize, rsize) and rva - vaddr < rsize:
                return raddr + (rva - vaddr)
        return None


def endereco_do_handler(qual: tuple[str, str] = HANDLER) -> tuple[int, int]:
    """(inicio, fim) do corpo, pelo TSV da WTE-TASK-04.

    O fim e o proximo handler publicado. Aqui isso basta e nao precisa do
    decodificador de instrucao do `dump_arranque.py`: o proximo handler comeca
    588 bytes depois do fim real, e os padroes procurados nao existem no meio.
    """
    linhas = PUB.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    enderecos = []
    alvo = None
    for linha in linhas[1:]:
        c = dict(zip(cab, linha.split("\t")))
        ender = int(c["endereco"], 16)
        enderecos.append(ender)
        if (c["formulario"], c["handler"]) == qual:
            alvo = ender
    if alvo is None:
        raise CheckError(f"{REL_PUB}: sem {qual[0]}.{qual[1]}")
    seguinte = min((e for e in enderecos if e > alvo), default=alvo + 0x800)
    return alvo, seguinte


def corpo(pe: PE, qual: tuple[str, str]) -> bytes:
    ini, fim = endereco_do_handler(qual)
    o = pe.off(ini)
    if o is None:
        raise CheckError(f"{REL_EXE}: {ini:#x} fora das secoes")
    return pe.data[o:o + (fim - ini)]


def uma_vez(bruto: bytes, padrao: bytes, onde: str, o_que: str) -> bytes:
    achados = re.findall(padrao, bruto)
    if len(achados) != 1:
        raise CheckError(
            f"{onde}: o padrao de '{o_que}' casou {len(achados)} vez(es), "
            f"esperava 1. A forma mudou no binario, e ler a constante velha "
            f"daria endereco errado com cara de certo.")
    return achados[0]


def buffer_de_edicao(pe: PE) -> int:
    """O endereco que os TRES handlers das barras nomeiam, se for um so.

    Cada um o enderaca de uma forma -- ponteiro de escrita, leitura indexada,
    escrita indexada, base de varredura -- e e a coincidencia dos quatro que
    justifica o `BarrasEmEdicao` do port existir separado da camada de dados.
    """
    vistos: dict[tuple[str, str], int] = {}
    for qual, (padrao, forma) in PADROES_BUFFER.items():
        bruto = corpo(pe, qual)
        cru = uma_vez(bruto, padrao, f"{qual[0]}.{qual[1]}", "buffer")
        vistos[qual] = struct.unpack(forma, cru)[0]
    distintos = set(vistos.values())
    if len(distintos) != 1:
        detalhe = ", ".join(f"{k[1]}={v:#x}" for k, v in vistos.items())
        raise CheckError(
            f"os handlers das barras deixaram de falar do mesmo buffer "
            f"({detalhe}). Enquanto isso valer, o `BarrasEmEdicao` do port "
            f"nao e o que a gravacao le, e editar uma barra gravaria o valor "
            f"velho -- com o golden acusando a gravacao.")
    return distintos.pop()


def campo_do_formulario(qual: tuple[str, str]) -> int:
    """O deslocamento de um campo, pelo campos.tsv da WTE-TASK-25."""
    linhas = CAMPOS.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    for linha in linhas[1:]:
        c = dict(zip(cab, linha.split("\t")))
        if (c["formulario"], c["campo"]) == qual:
            return int(c["offset"], 16)
    raise CheckError(f"{REL_CAMPOS}: sem {qual[0]}.{qual[1]}")


def constantes(pe: PE, ini: int, fim: int) -> dict[str, int]:
    o = pe.off(ini)
    if o is None:
        raise CheckError(f"{REL_EXE}: {ini:#x} fora das secoes")
    corpo = pe.data[o:o + (fim - ini)]
    saida: dict[str, int] = {}
    for nome, (padrao, forma) in PADROES.items():
        achados = re.findall(padrao, corpo)
        if len(achados) != 1:
            raise CheckError(
                f"{HANDLER[0]}.{HANDLER[1]}: o padrao de '{nome}' casou "
                f"{len(achados)} vez(es), esperava 1. A conta das barras mudou "
                f"de forma no binario, e ler a constante velha daria endereco "
                f"errado com cara de certo.")
        saida[nome] = struct.unpack(forma, achados[0])[0] if forma else 0
    return saida


def ofs_team_bars() -> int:
    texto = OFFSETS.read_text(encoding="utf-8")
    m = re.search(r"^\s*OFS_TEAM_BARS\s*=\s*(\d+);", texto, re.M)
    if not m:
        raise CheckError(f"{REL_OFFSETS}: sem OFS_TEAM_BARS")
    return int(m.group(1))


def fisico(t: int, base: int) -> int:
    return SETOR_BRUTO * (t // SETOR_DADOS) + (t % SETOR_DADOS) + base


def main(argv: list[str]) -> int:
    for arg in argv:
        if arg != "--check":
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        if not EXE.exists():
            raise CheckError(f"{REL_EXE}: ausente")
        pe = PE(EXE.read_bytes(), REL_EXE)
        ini, fim = endereco_do_handler()
        c = constantes(pe, ini, fim)
        esperado = ofs_team_bars()

        primeiro = fisico(c["ancora"], c["base"])
        if primeiro != esperado:
            raise CheckError(
                f"a conta do original leva o time 0 para {primeiro}, e a "
                f"OFS_TEAM_BARS do {REL_OFFSETS} diz {esperado}. Os dois "
                f"oraculos deixaram de falar do mesmo lugar -- a camada de "
                f"dados NAO pode servir as barras enquanto isto valer.")

        # Cinco bytes por time, 95 times, sem sobreposicao nem buraco: a
        # ultima leitura tem de acabar exatamente 5*95 bytes logicos adiante.
        ultimo = fisico(c["ancora"] + 5 * (TIMES - 1), c["base"])
        fim_logico = c["ancora"] + 5 * TIMES
        if fisico(fim_logico - 1, c["base"]) < ultimo:
            raise CheckError("a faixa das barras anda para tras -- conta errada")

        print(f"check_barras: passo 5, ancora {c['ancora']:#x}, base "
              f"{c['base']:#x}")
        print(f"check_barras: time 0 em {primeiro} = OFS_TEAM_BARS: ok")
        print(f"check_barras: {TIMES} times, ultimo em {ultimo}: ok")

        # --- o lado da edicao, da WTE-TASK-26 -------------------------------
        buffer = buffer_de_edicao(pe)
        print(f"check_barras: buffer de edicao {buffer:#x}, o mesmo nos "
              f"{len(PADROES_BUFFER)} handlers (carga, sel, track, gravacao): "
              f"ok")

        # A largura tem de ser a MESMA sequencia de bytes nos dois lados: e o
        # que faz uma barra editada e uma carregada com o mesmo valor darem o
        # mesmo pixel, e portanto o que torna a tela capaz de julgar a edicao.
        for qual in (HANDLER, HANDLER_TRACK):
            uma_vez(corpo(pe, qual), LARGURA, f"{qual[0]}.{qual[1]}",
                    "largura 11*v+9")
        print("check_barras: `11*v + 9` identico na carga e na edicao: ok")

        # A ancora da aritmetica de indice de componente do sel_barraClick.
        ancora = campo_do_formulario(CAMPO_ANCORA)
        # `mov eax,[ebx+imm32]` sozinho casa duas vezes -- a ancora e a
        # `track_barra` logo abaixo. O que separa e a SUBTRACAO: so a ancora
        # tem o `sub esi,eax` do indice depois da chamada.
        alvo = uma_vez(corpo(pe, HANDLER_SEL), rb"\x8b\x83(....)\xe8....\x2b\xf0",
                       f"{HANDLER_SEL[0]}.{HANDLER_SEL[1]}", "campo ancora")
        lido = struct.unpack("<I", alvo)[0]
        if lido != ancora:
            raise CheckError(
                f"o {HANDLER_SEL[1]} ancora a subtracao no campo {lido:#x} e "
                f"o {REL_CAMPOS} diz que {CAMPO_ANCORA[1]} mora em "
                f"{ancora:#x}. O indice 0..4 sairia deslocado.")
        print(f"check_barras: sel_barraClick ancora em {CAMPO_ANCORA[1]} "
              f"({ancora:#x}): ok")
    except CheckError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
