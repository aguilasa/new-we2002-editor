#!/usr/bin/env python3
"""As duas tabelas de campo de bit do `wte.exe`, contra o `Player.Decode` do port.

Gera `wte/re/bitfields.md` e `wte/re/bitfields.tsv` — produto da WTE-TASK-26,
décima primeira passagem.

## O que ele mede

O `0x0040756c` — a rotina que preenche a ficha do jogador — não tem os
deslocamentos de bit no código. Ele percorre **duas tabelas de registros de 12
bytes** em `.data` e chama o extrator `0x00403278` com cada uma:

| tabela | endereço | registros | o que descreve |
|---|---|---|---|
| habilidades | `0x00423648` | 16 | os atributos de 3 bits (ataque, defesa, …) |
| aparência   | `0x00423708` | 12 | posição, cabelo, barba, altura, idade, … |

Cada registro é `{ byte, bit inicial, largura }`, os três `int32`. O
`0x00403278` extrai `largura` bits a partir de `bit inicial`, atravessando para
o byte seguinte quando não cabem.

## Por que ele existe

O `we2002_player.pas` — gerado do `we2002_core`, que já é byte-idêntico ao
`ed.exe` — desempacota os mesmos 12 bytes com `shr`/`and` escritos à mão pelo
autor de 2002 do OUTRO editor. As duas descrições do formato são independentes:
uma é tabela de dados do `wte.exe`, a outra é expressão de código herdada do
`ed.exe`.

**Se elas concordam, o port não precisa de lógica de bit nova para a ficha** — e
essa é a economia que a décima primeira passagem da WTE-TASK-26 mediu. Se
alguém mexer num dos dois lados, este script para o build em vez de deixar a
ficha mostrar atributo trocado, que é um erro sem sintoma: um número plausível
no campo errado.

O que a conferência NÃO diz é qual controle da tela recebe qual campo — a
ordem dos registros é a ordem em que a rotina os consome, e casá-la com os
controles é leitura do corpo do `0x0040756c`, que continua por fazer.

## Como refazer

    python3 wte/tools/check_bitfields.py
    python3 wte/tools/check_bitfields.py --check

Sem o `we-team-editor/` presente ele avisa e sai 0, como o `dfm_extract.py`
faz com os blobs (CORR-WTE-004): a pasta é do usuário e não é versionada.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
PLAYER = ROOT / "wte" / "src" / "we2002_player.pas"
SAIDA_MD = ROOT / "wte" / "re" / "bitfields.md"
SAIDA_TSV = ROOT / "wte" / "re" / "bitfields.tsv"

# As duas tabelas, como o `0x0040756c` as percorre: `esi` recebe o endereco,
# `add esi,0xc` a cada volta, e o `cmp edi,<n>` fecha o laco.
#
# O terceiro endereco que a rotina carrega -- `0x00423798`, no segundo laco --
# NAO entra: lido com este mesmo layout de 12 bytes ele sai todo zero, o que
# quer dizer que o layout nao vale ali. O que ele e continua por medir, e esta
# escrito assim no `.md` em vez de virar uma terceira tabela inventada.
TABELAS = (
    ("habilidades", 0x00423648, 16),
    ("aparencia", 0x00423708, 12),
)

REGISTRO = 12  # bytes por registro; o `add esi,0xc` do laco


class ChecagemError(Exception):
    pass


def _pe(caminho: Path):
    """Reusa o leitor de PE do dump_auxiliares.py -- um so na arvore."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    argv = sys.argv
    sys.argv = [argv[0]]
    try:
        import dump_auxiliares as da
    finally:
        sys.argv = argv
    return da.PE(caminho.read_bytes(), caminho.name)


def ler_tabelas() -> list[tuple[str, int, int, int, int, int]]:
    """(tabela, indice, endereco do registro, byte, bit inicial, largura)."""
    dados = EXE.read_bytes()
    pe = _pe(EXE)
    saida = []
    for nome, base, n in TABELAS:
        off = pe.off(base)
        if off is None:
            raise ChecagemError(f"tabela {nome} ({base:#x}) fora das secoes")
        for i in range(n):
            b, s, w = struct.unpack_from("<iii", dados, off + REGISTRO * i)
            if not (0 <= b <= 11):
                raise ChecagemError(
                    f"{nome}[{i}]: byte {b} fora dos 12 de atributo -- "
                    "o endereco da tabela ou o passo de 12 esta errado")
            if not (0 <= s <= 7) or not (1 <= w <= 8):
                raise ChecagemError(
                    f"{nome}[{i}]: bit {s} largura {w} impossivel")
            saida.append((nome, i, base + REGISTRO * i, b, s, w))
    return saida


def expressoes(b: int, s: int, w: int) -> list[str]:
    """Como o `Player.Decode` do port extrai esse mesmo campo.

    A forma e mecanica, e por isso ela pode ser comparada com o arquivo em vez
    de com a memoria de quem escreveu o documento:

      cabe num byte:  `(raw_attributes[b] shr s) and $mm`, sem o `shr` se s = 0
      atravessa:      mais `(raw_attributes[b+1] shl (8-s)) and $mm`
    """
    mascara = (1 << w) - 1
    if s + w <= 8:
        if s == 0:
            return [f"raw_attributes[{b}] and ${mascara:02x}"]
        return [f"(raw_attributes[{b}] shr {s}) and ${mascara:02x}"]
    baixa = (1 << (8 - s)) - 1
    alta = mascara - baixa
    return [
        f"(raw_attributes[{b}] shr {s}) and ${baixa:02x}",
        f"(raw_attributes[{b + 1}] shl {8 - s}) and ${alta:02x}",
    ]


def corpo_do_decode() -> str:
    if not PLAYER.exists():
        raise ChecagemError(f"{PLAYER} nao existe")
    texto = PLAYER.read_text(encoding="utf-8")
    m = re.search(r"procedure TPlayer\.Decode.*?\nend;", texto, re.S)
    if not m:
        raise ChecagemError(f"{PLAYER.name}: TPlayer.Decode nao encontrado")
    return m.group(0)


def conferir(linhas) -> list[str]:
    """Os campos cuja extracao NAO aparece no `Decode`."""
    corpo = corpo_do_decode()
    faltando = []
    for nome, i, _end, b, s, w in linhas:
        for e in expressoes(b, s, w):
            if e not in corpo:
                faltando.append(f"{nome}[{i}] (byte {b}, bit {s}, {w} bits): "
                                f"`{e}` nao esta no TPlayer.Decode")
    return faltando


def render(linhas, faltando) -> tuple[str, str]:
    tsv = ["tabela\tindice\tendereco\tbyte\tbit_inicial\tlargura\textracao"]
    for nome, i, end, b, s, w in linhas:
        tsv.append(f"{nome}\t{i}\t{end:#010x}\t{b}\t{s}\t{w}\t"
                   + " + ".join(expressoes(b, s, w)))

    a = []
    a.append("# Os campos de bit da ficha do jogador — duas descricoes, "
             "uma so resposta")
    a.append("")
    a.append("GERADO por `wte/tools/check_bitfields.py`. **Nao editar a mao.**")
    a.append("")
    a.append("Produto da WTE-TASK-26, decima primeira passagem. O "
             "`0x0040756c` — a rotina que preenche a ficha do jogador — nao "
             "traz deslocamento de bit nenhum no codigo: ele percorre as duas "
             "tabelas abaixo e chama o extrator `0x00403278` com cada "
             "registro.")
    a.append("")
    a.append("| tabela | endereco | registros | passo |")
    a.append("|---|---|---|---|")
    for nome, base, n in TABELAS:
        a.append(f"| `{nome}` | `{base:#010x}` | {n} | {REGISTRO} B |")
    a.append("")
    a.append("O terceiro endereco que a rotina carrega — `0x00423798`, no "
             "segundo laco — **nao** entra aqui: lido com este mesmo layout de "
             "12 bytes ele sai todo zero, o que quer dizer que o layout nao "
             "vale ali. O que ele e continua por medir.")
    a.append("")
    a.append("## A conferencia")
    a.append("")
    a.append("Cada registro descreve `{byte, bit inicial, largura}` dentro dos "
             "12 bytes de atributo. O `we2002_player.pas` — gerado do "
             "`we2002_core`, que ja e byte-identico ao `ed.exe` — desempacota "
             "os mesmos 12 bytes com `shr`/`and`. **As duas descricoes sao "
             "independentes**: uma e tabela de dados do `wte.exe`, a outra e "
             "expressao de codigo herdada do outro editor.")
    a.append("")
    if faltando:
        a.append(f"**{len(faltando)} campo(s) sem correspondencia.**")
    else:
        a.append(f"**Os {len(linhas)} registros batem, um a um.** O port nao "
                 "precisa de logica de bit nova para a ficha: a camada de "
                 "dados ja a tem.")
    a.append("")
    a.append("| tabela | # | endereco | byte | bit | bits | extracao no "
             "`TPlayer.Decode` |")
    a.append("|---|---|---|---|---|---|---|")
    for nome, i, end, b, s, w in linhas:
        e = " + ".join(f"`{x}`" for x in expressoes(b, s, w))
        a.append(f"| {nome} | {i} | `{end:#010x}` | {b} | {s} | {w} | {e} |")
    a.append("")
    a.append("## O que isto NAO diz")
    a.append("")
    a.append("Qual controle da tela recebe qual campo. A ordem dos registros e "
             "a ordem em que a rotina os consome, e casa-la com os controles e "
             "leitura do corpo do `0x0040756c` — que continua por fazer.")
    a.append("")
    a.append("O campo `number` do `TPlayer` (byte 3, bit 2, 5 bits) **nao tem "
             "registro** em nenhuma das duas tabelas: o numero de camisa tem "
             "tela propria (`ficha_dorsal`), e a ficha do jogador nao o mostra.")
    a.append("")
    return "\n".join(a), "\n".join(tsv) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true",
                   help="confere o commitado em vez de reescrever")
    args = p.parse_args()

    if not EXE.exists():
        print(f"check_bitfields: {EXE.name} ausente -- nada medido")
        return 0

    try:
        linhas = ler_tabelas()
        faltando = conferir(linhas)
    except ChecagemError as e:
        print(f"check_bitfields: {e}", file=sys.stderr)
        return 2

    if faltando:
        print("check_bitfields: as duas descricoes do formato DIVERGEM:",
              file=sys.stderr)
        for f in faltando:
            print(f"  {f}", file=sys.stderr)
        print("  Enquanto isto valer, a ficha do jogador pode mostrar um "
              "atributo no campo de outro -- e um numero plausivel no lugar "
              "errado nao tem sintoma.", file=sys.stderr)
        return 2

    md, tsv = render(linhas, faltando)
    if args.check:
        rc = 0
        for caminho, texto in ((SAIDA_MD, md), (SAIDA_TSV, tsv)):
            atual = caminho.read_text(encoding="utf-8") if caminho.exists() else None
            rel = caminho.relative_to(ROOT)
            if atual != texto:
                print(f"check_bitfields: {rel}: DIVERGE -- rode sem --check",
                      file=sys.stderr)
                rc = 2
            else:
                print(f"check_bitfields: {rel}: ok")
        if rc == 0:
            print(f"check_bitfields: {len(linhas)} registros conferidos contra "
                  "TPlayer.Decode")
        return rc

    SAIDA_MD.write_text(md, encoding="utf-8")
    SAIDA_TSV.write_text(tsv, encoding="utf-8")
    for caminho in (SAIDA_MD, SAIDA_TSV):
        rel = caminho.relative_to(ROOT)
        print(f"  {rel}: {len(caminho.read_text(encoding='utf-8').splitlines())} "
              f"linhas, {caminho.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
