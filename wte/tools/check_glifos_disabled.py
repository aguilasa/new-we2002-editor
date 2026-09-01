#!/usr/bin/env python3
"""Quais glifos a LCL **não consegue** acinzentar, e por quê. Prova disso.

Produto da [CORR-WTE-060](../../docs/tasks/concluidos/CORR-WTE-060.md), que foi aberta
para medir um botão que não acinzentava e terminou medindo uma propriedade da
LCL inteira.

**Não escreve arquivo nenhum** — confere, e sai 2 quando diverge. Mesmo
contrato do `check_lcl_props.py` (CORR-WTE-020) e do `check_barras.py`, pela
mesma razão: o que se mede aqui não tem forma de documento, tem forma de
asserção.

## O que se mede

A LCL desenha o glifo de um botão desabilitado aplicando o efeito
`gdeDisabled`, que é uma **conversão para tons de cinza**. Pixel que já é
cinza (`R = G = B`) é ponto fixo dessa conversão: ele sai igual ao que entrou.

Logo, **um glifo cujos pixels desenhados sejam todos cinza fica idêntico
habilitado e desabilitado** — o botão apaga logicamente e não muda um pixel.
Preto puro e branco puro são cinza por essa definição, e é aí que mora o caso:
glifo de traço preto sobre branco com fundo transparente é invariante.

O Win32 não faz isso. O `comctl32` desenha o glifo desabilitado a partir de uma
máscara monocromática: preto vira sombra e branco vira transparente. Por isso
o mesmo botão muda 518 px no oráculo sob Wine e 0 px no port.

**A divergência é do widgetset, não do port** — e é por isso que este script
confere um conjunto em vez de consertar alguma coisa. O que ele impede é o
conjunto crescer em silêncio: um glifo novo, ou uma troca de cor no
`dfm2lfm.py`, que caia na invariância sem ninguém notar.

## Como o número é obtido

Para cada `TSpeedButton`/`TBitBtn` com `Glyph.Data` nos `.lfm` de
`wte/forms/`:

1. o BMP é decodificado do stream do formulário (24 bpp, `BI_RGB`, bottom-up —
   é o que o C++Builder 6 gravou nos 18 formulários, e o decodificador
   **aborta** se aparecer outra coisa em vez de adivinhar);
2. a **cor transparente** é o pixel inferior-esquerdo, que é o primeiro do
   arquivo num BMP bottom-up — é a regra que a LCL usa em
   `TBitmap.TransparentColor`;
3. conta-se quantos pixels **desenhados** (fora os da cor transparente) são
   **não-cinza**. Esse número é exatamente quantos pixels o botão muda ao
   desabilitar.

O passo 3 foi confirmado contra o app rodando: `boton_nombres2iso` tem 280
pixels não-cinza e muda 280 px no `compara_tela.sh --habilitacao`. Não é
estimativa, é o mesmo número.

## Por que a lista é escrita à mão

`INVARIANTES` é o conjunto medido em 2026-08-18 e **declarado**. Ele existe
para a conferência ter dois lados: um glifo que entre ou saia da invariância
derruba este script, em vez de mudar a tela e ficar por isso mesmo. Não é a
saída do próprio script escrita de volta — isso conferiria a tabela consigo
mesma, que é a armadilha que a CORR-WTE-020 achou no `dfm2lfm.py`.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FORMS = AQUI.parent / "forms"

# Os cinco glifos invariantes sob `gdeDisabled`, medidos em 2026-08-18.
# Chave: (arquivo .lfm, nome do objeto).
INVARIANTES = {
    ("ep2002_color.lfm", "oscurecer"),
    ("ep2002_color.lfm", "aclarar"),
    ("ep2002_mainform.lfm", "iguala_nombres"),
    ("ep2002_mainform.lfm", "parriba"),
    ("ep2002_mainform.lfm", "pabajo"),
}

# O botão de controle: tem glifo colorido, acinzenta, e o número dele foi
# confirmado na tela. Se ele deixar de bater, o decodificador é que quebrou --
# não os glifos.
CONTROLE = ("ep2002_mainform.lfm", "boton_nombres2iso", 280)

OBJETO = re.compile(
    r"object (\w+): (TSpeedButton|TBitBtn)\b(.*?)\n(\s*)end", re.S)
GLIFO = re.compile(r"Glyph\.Data = \{(.*?)\}", re.S)


class CheckError(Exception):
    """Entrada que este script não sabe ler -- aborta em vez de adivinhar."""


def pixels_bmp(bmp: bytes) -> tuple[list[bytes], bytes]:
    """Devolve (pixels, cor_transparente) de um BMP 24 bpp BI_RGB bottom-up.

    Cada pixel é o triplo BGR cru, do jeito que está no arquivo: a comparação
    aqui é de igualdade e de `R == G == B`, e nenhuma das duas precisa da
    ordem dos canais.
    """
    if bmp[:2] != b"BM":
        raise CheckError("stream do glifo nao comeca com 'BM'")
    inicio, = struct.unpack_from("<I", bmp, 10)
    larg, alt = struct.unpack_from("<ii", bmp, 18)
    planos, bpp = struct.unpack_from("<HH", bmp, 26)
    compressao, = struct.unpack_from("<I", bmp, 30)
    if bpp != 24 or compressao != 0 or planos != 1:
        raise CheckError(
            f"glifo {larg}x{alt} e {bpp} bpp/compressao {compressao}/"
            f"{planos} planos -- este script so le 24 bpp BI_RGB")
    if alt < 0:
        raise CheckError("glifo top-down; a regra da cor transparente da LCL "
                         "assume bottom-up")
    passo = (larg * 3 + 3) // 4 * 4
    pix = []
    for y in range(alt):
        base = inicio + y * passo
        linha = bmp[base:base + larg * 3]
        if len(linha) != larg * 3:
            raise CheckError("stream do glifo truncado")
        pix += [linha[x * 3:x * 3 + 3] for x in range(larg)]
    # bottom-up: o primeiro pixel do arquivo e o inferior-esquerdo, que e o
    # que a LCL toma como transparente.
    return pix, pix[0]


def nao_cinza_desenhados(bmp: bytes) -> int:
    """Quantos pixels o botao muda ao desabilitar, pela regra do grayscale."""
    pix, transp = pixels_bmp(bmp)
    return sum(1 for p in pix
               if p != transp and not (p[0] == p[1] == p[2]))


def glifos() -> dict[tuple[str, str], int]:
    """Varre `wte/forms/*.lfm` e mede cada botao com glifo."""
    if not FORMS.is_dir():
        raise CheckError(f"{FORMS} nao existe")
    achados: dict[tuple[str, str], int] = {}
    for lfm in sorted(FORMS.glob("*.lfm"), key=lambda p: p.as_posix()):
        texto = lfm.read_text(encoding="utf-8", errors="replace")
        for m in OBJETO.finditer(texto):
            nome, corpo = m.group(1), m.group(3)
            g = GLIFO.search(corpo)
            if not g:
                continue
            bruto = bytes.fromhex("".join(g.group(1).split()))
            # Os 4 primeiros bytes sao o tamanho do stream, do TFiler; o BMP
            # comeca depois deles.
            achados[(lfm.name, nome)] = nao_cinza_desenhados(bruto[4:])
    if not achados:
        raise CheckError("nenhum glifo encontrado em wte/forms/*.lfm")
    return achados


def conferir() -> tuple[list[str], dict[str, int]]:
    medidos = glifos()
    problemas: list[str] = []

    invariantes = {k for k, v in medidos.items() if v == 0}
    for k in sorted(invariantes - INVARIANTES):
        problemas.append(
            f"{k[0]}:{k[1]} virou invariante sob gdeDisabled e nao esta em "
            "INVARIANTES -- este botao passou a nao acinzentar no port")
    for k in sorted(INVARIANTES - invariantes):
        if k not in medidos:
            problemas.append(f"{k[0]}:{k[1]} esta em INVARIANTES e sumiu dos "
                             ".lfm")
        else:
            problemas.append(
                f"{k[0]}:{k[1]} esta em INVARIANTES mas agora muda "
                f"{medidos[k]} px -- deixou de ser divergencia")

    arq, nome, esperado = CONTROLE
    obtido = medidos.get((arq, nome))
    if obtido != esperado:
        problemas.append(
            f"controle {arq}:{nome} mede {obtido} px, esperado {esperado} -- "
            "o decodificador de BMP quebrou, nao os glifos")

    return problemas, {
        "botoes com glifo": len(medidos),
        "invariantes sob gdeDisabled": len(invariantes),
    }


def main(argv: list[str]) -> int:
    modo_check = "--check" in argv[1:]
    try:
        problemas, contagem = conferir()
    except CheckError as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    if problemas:
        print("ERRO: o conjunto de glifos invariantes sob o gdeDisabled da "
              "LCL mudou:", file=sys.stderr)
        for p in problemas:
            print(f"  {p}", file=sys.stderr)
        return 2
    if modo_check:
        print(f"check_glifos_disabled: {contagem['botoes com glifo']} botoes "
              f"com glifo, {contagem['invariantes sob gdeDisabled']} "
              "invariantes sob gdeDisabled (CORR-WTE-060)")
        return 0
    for (arq, nome), v in sorted(glifos().items()):
        marca = "  <== INVARIANTE (nao acinzenta no port)" if v == 0 else ""
        print(f"{arq:28s} {nome:22s} {v:5d} px mudam ao desabilitar{marca}")
    print("\nsem divergencia")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
