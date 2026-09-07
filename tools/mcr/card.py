#!/usr/bin/env python3
"""O conteiner do memory card PSX -- diretorio, blocos, quadros e as recusas.

Proveniencia (secao 3.4 do plano):

  conteiner   spec publica do nocash ("Memory Card Data Format"), e o
              `wte/tools/dump_mcr.py` deste repositorio, que ja a implementa
  endereco    NENHUM. Os 17 destinos do save moram em `layout.py`, e so la
              (Regra 1 da secao 3.3). O `0x800` deste modulo nao e um deles:
              ele e DERIVADO do tamanho do quadro e da contagem de quadros de
              diretorio, e por isso e calculado, nao escrito
  semantica   --
  codec       --

O que este modulo existe para impedir, e que o upstream faz: tratar o cartao
como um binario plano de 131.072 bytes. O `Easy MCR` nao menciona diretorio,
quadro, bloco nem estado em lugar nenhum do fonte, e o efeito e triplo -- so
funciona com dump raw, quebra em silencio se o save mudar de bloco, e grava IDs
de um banco privado nos bytes 0..137, que sao o quadro de cabecalho `MC`
inteiro mais o `state`+`size`+`link` da entrada 1. O resultado e um cartao que
nenhum console le. Ver a secao 1.10 do plano.

Uso:

    python3 tools/mcr/card.py <cartao.mcr>
    python3 tools/mcr/card.py <cartao.mcr> --json
    python3 tools/mcr/card.py --self-check
"""

import argparse
import dataclasses
import json
import os
import re
import sys

# --- o conteiner ----------------------------------------------------------
# Numeros da spec publica do nocash, os mesmos quatro que o `dump_mcr.py` ja
# carrega. Nao ha nada de WE2002 aqui: qualquer memory card de PSX e assim.

CARD_BYTES = 0x20000        # 131.072 = 16 blocos
BLOCK_BYTES = 8192
FRAME_BYTES = 128
DIRECTORY_FRAMES = 15       # o quadro 0 e o cabecalho `MC`; os 15 seguintes
                            # descrevem os blocos 1..15
MAGIC = b"MC"

# O primeiro byte que pertence a DADO e nao a estrutura. E o `0x800` da secao
# 1.10 do plano, e ele e derivado de proposito: escrito como constante, ele
# vira mais um numero magico que ninguem sabe de onde veio, e a proxima pessoa
# que mudar FRAME_BYTES o deixa para tras.
HEADER_BYTES = FRAME_BYTES * (DIRECTORY_FRAMES + 1)   # 2048 = 0x800

# Os oito estados de quadro. O nibble alto separa livre de em uso; o baixo diz
# a posicao na cadeia.
FRAME_STATES = {
    0x51: "em uso, primeiro bloco da cadeia",
    0x52: "em uso, bloco do meio",
    0x53: "em uso, ultimo bloco da cadeia",
    0xA0: "livre (formatado)",
    0xA1: "livre (era o primeiro de uma cadeia apagada)",
    0xA2: "livre (era do meio)",
    0xA3: "livre (era o ultimo)",
    0xFF: "sem uso",
}

IN_USE_STATES = (0x51, 0x52, 0x53)
CHAIN_END = 0xFFFF

# O nome do save do WE2002, como ele aparece no quadro de diretorio.
#
# MEDIDO, e so um: `BISLPM-86600WEW-OPT`, na fixture japonesa. O `B` e o
# cabecalho de save do PSX, a letra seguinte e a regiao (I=Japao, E=Europa,
# A=America) e o resto e o codigo de produto mais o nome do arquivo.
#
# As variantes europeia e americana estao no padrao POR FORMA, nao por
# medicao: nenhum cartao SLES ou SLUS passou por aqui, e inventar o numero de
# produto deles seria fabricar dado. O que identifica o save e o sufixo
# `WEW-OPT`; e por ele que se casa, e o prefixo so confere que a coisa tem
# cara de nome de save de PSX.
SAVE_NAME_RE = re.compile(r"^B[A-Z]SL[A-Z]{2}-\d{5}WEW-OPT$")


class CardError(Exception):
    """Cartao que nao e um cartao, ou que nao e o que se pediu."""


class Refused(Exception):
    """Uma escrita que este modulo nao faz, com a razao que um humano precisa."""


def frame_checksum(frame: bytes) -> int:
    """O XOR dos 127 primeiros bytes, que e o que o byte 127 guarda."""
    x = 0
    for b in frame[:FRAME_BYTES - 1]:
        x ^= b
    return x


@dataclasses.dataclass
class DirectoryEntry:
    """Um dos 15 quadros de diretorio, ja lido."""

    frame: int              # 1..15
    block: int              # o bloco que ele descreve -- o mesmo numero
    state: int
    size: int               # tamanho declarado do save, em bytes
    link: int               # proximo da cadeia, 0-based, ou 0xFFFF
    name: str
    stored_checksum: int
    computed_checksum: int

    @property
    def state_name(self) -> str:
        return FRAME_STATES.get(self.state, "desconhecido")

    @property
    def in_use(self) -> bool:
        return self.state in IN_USE_STATES

    @property
    def checksum_ok(self) -> bool:
        return self.stored_checksum == self.computed_checksum

    @property
    def next_frame(self) -> int | None:
        """O quadro seguinte da cadeia, ou `None` se este e o ultimo.

        O `link` e 0-BASED sobre os 15 blocos de dados, e o quadro e 1-based:
        link 1 quer dizer quadro 2. Ler o link como numero de quadro faz a
        cadeia da fixture apontar para si mesma -- o quadro 1 tem link 1 -- e
        um leitor ingenuo entra em laco infinito ou conclui "cadeia de um
        bloco" para um save de 16.384 bytes. E o tamanho declarado que
        desempata, e foi assim que isto foi medido.
        """
        if self.link == CHAIN_END:
            return None
        return self.link + 1


class Card:
    """Os 131.072 bytes de um cartao, com o diretorio por cima.

    Os bytes crus sao normativos (Regra 2 da secao 3.3): este objeto guarda o
    cartao inteiro e edita por read-modify-write no campo. Nada e remontado, e
    e por isso que o round-trip byte-identico e alcancavel.
    """

    def __init__(self, data: bytes, origin: str = "<memoria>"):
        if len(data) != CARD_BYTES:
            raise CardError(
                f"{origin}: {len(data)} bytes, e um memory card de PSX tem "
                f"{CARD_BYTES} ({CARD_BYTES // BLOCK_BYTES} blocos de "
                f"{BLOCK_BYTES}). Formatos com cabecalho -- .gme, .vgs, .mcd de "
                f"emulador -- nao sao dump raw e nao servem aqui.")
        if data[:len(MAGIC)] != MAGIC:
            raise CardError(
                f"{origin}: os dois primeiros bytes sao "
                f"{data[:2].hex(' ')} e nao {MAGIC.decode()} "
                f"({MAGIC.hex(' ')}). Isto nao e um memory card formatado.")
        self.data = bytearray(data)
        self.origin = origin

    # -- leitura ----------------------------------------------------------

    @classmethod
    def from_file(cls, path) -> "Card":
        with open(path, "rb") as fh:
            return cls(fh.read(), origin=str(path))

    def frame(self, index: int) -> bytes:
        return bytes(self.data[index * FRAME_BYTES:(index + 1) * FRAME_BYTES])

    def block(self, index: int) -> bytes:
        return bytes(self.data[index * BLOCK_BYTES:(index + 1) * BLOCK_BYTES])

    def header_checksum_ok(self) -> bool:
        """O quadro 0 tambem tem checksum, e tambem nao se conserta."""
        q = self.frame(0)
        return q[FRAME_BYTES - 1] == frame_checksum(q)

    def directory(self) -> list[DirectoryEntry]:
        out = []
        for i in range(1, DIRECTORY_FRAMES + 1):
            q = self.frame(i)
            out.append(DirectoryEntry(
                frame=i,
                block=i,
                state=q[0],
                size=int.from_bytes(q[4:8], "little"),
                link=int.from_bytes(q[8:10], "little"),
                name=q[10:30].split(b"\0")[0].decode("ascii", "replace"),
                stored_checksum=q[FRAME_BYTES - 1],
                computed_checksum=frame_checksum(q),
            ))
        return out

    def stray_blocks(self) -> list[tuple[int, int, int]]:
        """Blocos com dado que o diretorio nao declara: `(bloco, estado, nao_zero)`.

        MEDIDO na fixture: o bloco 3 tem 41 bytes nao-zero e o diretorio o
        marca `0xA0`, livre. Nao e sujeira -- e onde moram formacao,
        cobradores e tatica. E o que torna "este cartao e valido para o
        console?" uma pergunta em aberto (secao 5.6 do plano), e e por isso
        que esta medicao e um comando e nao um script perdido.
        """
        achado = self.find_save()
        declarados = set(achado[1]) if achado else set()
        out = []
        for b in range(1, DIRECTORY_FRAMES + 1):
            if b in declarados:
                continue
            nz = sum(1 for x in self.block(b) if x)
            if nz:
                out.append((b, self.frame(b)[0], nz))
        return out

    def bad_checksums(self) -> list[int]:
        """Os quadros cujo XOR nao bate -- RELATADOS, nunca consertados.

        Nao recalcular o checksum e comportamento MEDIDO do original, e a
        secao 6 do plano manda reproduzi-lo por ora: divergir sem oraculo
        troca um desconhecido por outro. Quem quiser mudar isso mede primeiro,
        na MCR-TASK-13.
        """
        bad = [] if self.header_checksum_ok() else [0]
        bad += [d.frame for d in self.directory() if not d.checksum_ok]
        return bad

    def chain(self, start_frame: int) -> list[int]:
        """Os quadros de uma cadeia, seguindo o `link` a partir de `start_frame`."""
        seen: list[int] = []
        entries = {d.frame: d for d in self.directory()}
        cur = start_frame
        while cur is not None:
            if cur in seen:
                raise CardError(
                    f"{self.origin}: a cadeia que comeca no quadro "
                    f"{start_frame} volta ao quadro {cur} -- diretorio "
                    f"corrompido, ou o `link` foi lido como numero de quadro "
                    f"em vez de indice 0-based de bloco.")
            if cur not in entries:
                raise CardError(
                    f"{self.origin}: a cadeia que comeca no quadro "
                    f"{start_frame} aponta para o quadro {cur}, fora de "
                    f"1..{DIRECTORY_FRAMES}.")
            seen.append(cur)
            cur = entries[cur].next_frame
        return seen

    def find_save(self, pattern: re.Pattern = SAVE_NAME_RE):
        """O save do WE2002: a entrada, e os blocos em que ele de fato esta.

        Devolve `(entrada, [blocos])`, ou `None` se nao houver.

        DIZER O BLOCO E O PONTO. O upstream assume onde o save esta e, se ele
        estiver noutro lugar, todo endereco se desloca em multiplos de 8192 e o
        resultado continua parecendo plausivel na tela -- e a armadilha 6 do
        perfil. Aqui o bloco e lido do diretorio e devolvido junto.
        """
        for d in self.directory():
            if d.in_use and d.state == 0x51 and pattern.match(d.name):
                return d, self.chain(d.frame)
        return None

    # -- escrita ----------------------------------------------------------

    def write(self, offset: int, payload: bytes) -> None:
        """Grava `payload` em `offset`, ou RECUSA com a razao.

        A recusa abaixo de `0x800` nao e um comentario de cortesia: e o caso de
        controle negativo da secao 5.2 do plano, e ela existe porque o
        `GrabarData` do upstream grava exatamente ali.
        """
        if offset < 0:
            raise Refused(f"offset negativo: {offset}")
        end = offset + len(payload)
        if end > CARD_BYTES:
            raise Refused(
                f"escrita de {len(payload)} bytes em {offset:#07x} passa do "
                f"fim do cartao ({CARD_BYTES:#07x}).")
        if offset < HEADER_BYTES:
            raise Refused(
                f"escrita em {offset:#07x}, abaixo de {HEADER_BYTES:#05x}: "
                f"ali estao o quadro de cabecalho `MC` e os "
                f"{DIRECTORY_FRAMES} quadros de diretorio -- estado, tamanho, "
                f"link, nome e checksum de cada bloco. Um cartao com isso "
                f"sobrescrito nao e lido por console nenhum. E o que o "
                f"upstream faz nos bytes 0..137, e o port nao faz.")
        self.data[offset:end] = payload

    def to_bytes(self) -> bytes:
        return bytes(self.data)


# --- o cartao sintetico, para o self-check --------------------------------

def synthetic_card(save_name: str = "BISLPM-86600WEW-OPT",
                   blocks: int = 2) -> Card:
    """Um cartao valido montado em memoria -- sem fixture, sem disco.

    E o que faz o `mcr_selftest` rodar em qualquer maquina. A cadeia tem
    `blocks` blocos para que o teste do `link` 0-based tenha o que exercitar:
    com um bloco so, ler o link errado passaria despercebido.
    """
    data = bytearray(b"\x00" * CARD_BYTES)
    data[0:2] = MAGIC
    for i in range(1, DIRECTORY_FRAMES + 1):
        q = bytearray(b"\x00" * FRAME_BYTES)
        if i <= blocks:
            q[0] = 0x51 if i == 1 else (0x53 if i == blocks else 0x52)
            q[4:8] = (BLOCK_BYTES * blocks).to_bytes(4, "little")
            # link 0-based: o quadro i aponta para o quadro i+1 com o valor i
            q[8:10] = (CHAIN_END if i == blocks else i).to_bytes(2, "little")
            if i == 1:
                q[10:10 + len(save_name)] = save_name.encode("ascii")
        else:
            q[0] = 0xA0
            q[8:10] = CHAIN_END.to_bytes(2, "little")
        q[FRAME_BYTES - 1] = frame_checksum(q)
        data[i * FRAME_BYTES:(i + 1) * FRAME_BYTES] = q
    data[127] = frame_checksum(data[0:FRAME_BYTES])
    return Card(bytes(data), origin="<sintetico>")


# --- self-check -----------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    """Exercita o modulo contra um cartao sintetico. Devolve o numero de falhas.

    Cada recusa e um CASO VERMELHO: o teste nao pergunta "o modulo aceita o que
    e valido", pergunta "o modulo recusa o que e invalido, e pela razao certa".
    Um guard que nunca ficou vermelho e decoracao -- a licao das CORR-PES2-009
    e -020.
    """
    falhas = []

    def ok(nome, cond, detalhe=""):
        if cond:
            if verbose:
                print(f"  ok    {nome}")
        else:
            falhas.append(nome)
            print(f"  FALHA {nome}  {detalhe}")

    def tenta(nome, fn, default=None):
        """Roda `fn()` e devolve o valor; excecao INESPERADA vira falha.

        Sem isto, um defeito que levanta em vez de devolver errado mata a
        corrida no meio e esconde tudo que vinha depois -- medido: tirar o
        `+1` do `link` fazia o `find_save` estourar no sexto check e os outros
        vinte nunca rodavam. O gate ficava vermelho, mas por traceback, e o
        relatorio nao dizia o que mais estava quebrado.
        """
        try:
            return fn()
        except Exception as e:                        # noqa: BLE001
            falhas.append(nome)
            print(f"  FALHA {nome}: levantou {type(e).__name__}: {e}")
            return default

    def recusa(nome, fn, trecho, excecao=Refused):
        """Exige que `fn()` levante `excecao` com `trecho` na mensagem."""
        try:
            fn()
        except excecao as e:
            if trecho in str(e):
                if verbose:
                    print(f"  ok    {nome} (recusou: {str(e)[:60]}...)")
            else:
                falhas.append(nome)
                print(f"  FALHA {nome}: recusou, mas sem dizer {trecho!r}: {e}")
        except Exception as e:                        # noqa: BLE001
            falhas.append(nome)
            print(f"  FALHA {nome}: levantou {type(e).__name__}, "
                  f"esperado {excecao.__name__}: {e}")
        else:
            falhas.append(nome)
            print(f"  FALHA {nome}: NAO recusou -- o guard esta verde a toa")

    print("card.py self-check")

    c = synthetic_card()

    # --- o que tem de funcionar
    ok("magic e tamanho aceitos", c.to_bytes()[:2] == MAGIC
       and len(c.to_bytes()) == CARD_BYTES)
    ok("checksum do cabecalho bate", c.header_checksum_ok())
    ok("nenhum checksum ruim no sintetico", c.bad_checksums() == [],
       f"ruins={c.bad_checksums()}")
    ok("15 quadros de diretorio", len(c.directory()) == DIRECTORY_FRAMES)

    d = c.directory()
    ok("quadro 1 em uso, primeiro da cadeia", d[0].state == 0x51 and d[0].in_use)
    ok("quadro 1 nomeia o estado", d[0].state_name.startswith("em uso"))
    ok("quadro 3 livre", d[2].state == 0xA0 and not d[2].in_use)

    achado = tenta("acha o save pelo nome", c.find_save)
    ok("acha o save pelo nome", achado is not None)
    if achado:
        entrada, blocos = achado
        ok("diz em que blocos o save esta", blocos == [1, 2], f"blocos={blocos}")
        ok("tamanho declarado bate com a cadeia",
           entrada.size == len(blocos) * BLOCK_BYTES,
           f"size={entrada.size} blocos={len(blocos)}")

    # O link 0-based, exercitado de frente: quadro 1 tem link 1 e aponta para o
    # quadro 2. Lido como numero de quadro, apontaria para si mesmo.
    ok("link 0-based vira o quadro seguinte",
       d[0].link == 1 and d[0].next_frame == 2,
       f"link={d[0].link} next={d[0].next_frame}")
    ok("fim de cadeia e None", d[1].next_frame is None)

    ok("HEADER_BYTES e derivado e vale 0x800", HEADER_BYTES == 0x800)

    # escrita valida, no dado
    antes = c.to_bytes()
    c.write(HEADER_BYTES, b"\xAA\xBB")
    ok("escrita em 0x800 e aceita", c.to_bytes()[0x800:0x802] == b"\xAA\xBB")
    ok("escrita valida so toca o que pediu",
       sum(1 for a, b in zip(antes, c.to_bytes()) if a != b) == 2)

    # --- as recusas: os casos vermelhos
    recusa("recusa escrita em 0x0000",
           lambda: c.write(0, b"\x00" * 138), "abaixo de 0x800")
    recusa("recusa escrita no ultimo byte do diretorio",
           lambda: c.write(HEADER_BYTES - 1, b"\x00"), "abaixo de 0x800")
    recusa("recusa escrita que atravessa o fim do cartao",
           lambda: c.write(CARD_BYTES - 1, b"\x00\x00"), "passa do fim")
    recusa("recusa offset negativo",
           lambda: c.write(-1, b"\x00"), "negativo")

    recusa("recusa arquivo truncado em 1 byte",
           lambda: Card(bytes(CARD_BYTES - 1), origin="<truncado>"),
           "bytes, e um memory card", CardError)
    recusa("recusa arquivo sem MC",
           lambda: Card(b"\x00" * CARD_BYTES, origin="<sem magic>"),
           "nao e um memory card formatado", CardError)

    # checksum divergente e RELATADO, nunca consertado
    sujo = synthetic_card()
    sujo.data[3 * FRAME_BYTES + FRAME_BYTES - 1] ^= 0xFF
    ok("checksum divergente e relatado", sujo.bad_checksums() == [3],
       f"ruins={sujo.bad_checksums()}")
    ok("checksum divergente NAO e consertado",
       sujo.frame(3)[FRAME_BYTES - 1] != frame_checksum(sujo.frame(3)))

    fora = tenta("dado fora da cadeia e calculavel", c.stray_blocks, default=None)
    ok("sintetico nao tem dado fora da cadeia", fora == [], f"fora={fora}")
    sujeira = synthetic_card()
    sujeira.write(3 * BLOCK_BYTES, b"\x01\x02\x03")
    suja = tenta("bloco livre com dado e calculavel", sujeira.stray_blocks)
    ok("dado num bloco livre e denunciado", suja == [(3, 0xA0, 3)], f"fora={suja}")

    # o negativo da secao 5.2: trocar o estado do quadro 1 de 0x51 para 0xA0
    perdido = synthetic_card()
    perdido.data[1 * FRAME_BYTES] = 0xA0
    perdido.data[1 * FRAME_BYTES + FRAME_BYTES - 1] = frame_checksum(
        perdido.frame(1))
    ok("save some quando o quadro 1 vira 0xA0",
       tenta("find_save no cartao sem save", perdido.find_save, "?") is None)

    # cadeia que volta em si -- o sintoma de ler o link como numero de quadro
    laco = synthetic_card()
    laco.data[1 * FRAME_BYTES + 8:1 * FRAME_BYTES + 10] = (0).to_bytes(2, "little")
    recusa("recusa cadeia circular",
           lambda: laco.chain(1), "volta ao quadro", CardError)

    print(f"card.py: {len(falhas)} falha(s)")
    return len(falhas)


# --- CLI ------------------------------------------------------------------

def _report(card: Card) -> dict:
    achado = card.find_save()
    return {
        "origem": card.origin,
        "bytes": CARD_BYTES,
        "magic_ok": True,
        "checksums_ruins": card.bad_checksums(),
        "save": None if achado is None else {
            "nome": achado[0].name,
            "blocos": achado[1],
            "tamanho_declarado": achado[0].size,
            "offset_do_primeiro_bloco": achado[1][0] * BLOCK_BYTES,
        },
        "blocos_fora_da_cadeia": [
            {"bloco": b, "estado": f"{e:#04x}", "bytes_nao_zero": n}
            for b, e, n in card.stray_blocks()
        ],
        "diretorio": [
            {"quadro": d.frame, "estado": f"{d.state:#04x}",
             "estado_nome": d.state_name, "tamanho": d.size,
             "link": f"{d.link:#06x}", "proximo_quadro": d.next_frame,
             "nome": d.name, "checksum_ok": d.checksum_ok}
            for d in card.directory()
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?", help="o .mcr a inspecionar")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    ap.add_argument("--blocks", action="store_true",
                    help="bytes nao-zero por bloco, e o que cai fora da cadeia")
    ap.add_argument("--self-check", action="store_true",
                    help="roda o self-check, sem cartao nenhum")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    if not a.card:
        ap.error("informe um .mcr, ou use --self-check")

    try:
        card = Card.from_file(a.card)
    except (CardError, OSError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2

    if a.blocks:
        achado = card.find_save()
        declarados = set(achado[1]) if achado else set()
        d = {x.frame: x for x in card.directory()}
        print(" bloco  estado  bytes nao-zero")
        for b in range(1, DIRECTORY_FRAMES + 1):
            nz = sum(1 for x in card.block(b) if x)
            marca = "  <-- fora da cadeia declarada" if nz and b not in declarados else ""
            print(f"   {b:2d}   {d[b].state:#04x}   {nz:6d}{marca}")
        return 0

    rel = _report(card)
    if a.json:
        print(json.dumps(rel, indent=2, ensure_ascii=False))
        return 0

    print(f"{card.origin}: {CARD_BYTES} bytes, magic MC")
    ruins = rel["checksums_ruins"]
    print(f"checksums de quadro: "
          f"{'todos batem' if not ruins else f'DIVERGEM nos quadros {ruins}'}"
          f"  (relatado, nunca consertado)")
    if rel["save"]:
        s = rel["save"]
        print(f"save WE2002: {s['nome']!r} nos blocos {s['blocos']}, "
              f"{s['tamanho_declarado']} bytes declarados, "
              f"primeiro bloco em {s['offset_do_primeiro_bloco']:#07x}")
    else:
        print("save WE2002: NAO encontrado neste cartao")
    print()
    print("  q  estado  como                                       tam  link"
          "   nome")
    for d in card.directory():
        print(f" {d.frame:2d}   {d.state:#04x}  {d.state_name:<40} "
              f"{d.size:>6}  {d.link:#06x}  {d.name}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
