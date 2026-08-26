#!/usr/bin/env python3
"""Desenha o ícone do WE2002 - Lazarus Editor em wte/packaging/icons/.

Produto da WTE-TASK-39, e irmão do `tools/make_icon.py` do `newWe2002`: mesma
oficina (desenho em 16× e reamostragem LANCZOS, tamanho pequeno desenhado
simplificado em vez de reescalado), assunto diferente.

## Por que uma bandeirinha, e não outra camisa

O irmão já é uma camisa. Dois ícones do mesmo repositório que são a mesma
silhueta em cores parecidas não são dois ícones: são um ícone e uma cópia mal
feita. A bandeirinha de escanteio tem silhueta própria — poste vertical e
triângulo — e continua legível em 16 px, que é onde tudo colapsa.

E ela é do assunto: bandeira e uniforme 2D são as duas telas que o editor do
Obocaman tem e o `ed.exe` não, e são o motivo de a WTE-TASK-29 existir.

## As cores saem do próprio app, e não de gosto

| Cor | De onde |
|---|---|
| `#76B6FF` | o fundo do `MainForm` em tempo de execução (`$00FFB676`, posto pelo `FormShow`) |
| `#418FE6` | o fundo de `jugador`, `estrategia` e `ficha_color` (`$00E68F41`) |
| `#DC3C3C` | o vermelho dos dois `ficha_warning` (`$003C3CDC`) |

Os três estão medidos em [`../re/arranque.md`](../re/arranque.md) e conferidos
na tela pelos dois lados em [`../re/carregado.tsv`](../re/carregado.tsv). O
ícone é a única coisa gerada aqui que teste nenhum julga — usar cor que o
próprio programa mostra é o que sobra de disciplina.

## Sem `--check`, e é decisão herdada

A saída do PIL não é byte-determinística entre versões, e um guard que quebra o
build quando o Pillow sobe é pior que nenhum. **Ao mexer no ícone, olhe o
resultado.**

    python3 wte/tools/make_icon.py
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "wte" / "packaging" / "icons"

TAMANHOS = [16, 24, 32, 48, 64, 128, 256]
#: Abaixo disto a bandeirinha sai sem a faixa branca e com o poste mais grosso.
SIMPLES_ABAIXO = 32
#: Superamostragem. 16 basta para a hipotenusa do triângulo sair limpa.
SS = 16

FUNDO_TOPO = (118, 182, 255)   # $00FFB676 -- o MainForm
FUNDO_BASE = (65, 143, 230)    # $00E68F41 -- jugador, estrategia, ficha_color
FUNDO_BORDA = (28, 84, 150)
PANO = (220, 60, 60)           # $003C3CDC -- os dois ficha_warning
POSTE = (247, 250, 248)
FAIXA = (247, 250, 248)

#: O poste, em frações do lado.
POSTE_X, POSTE_TOPO, POSTE_BASE = 0.300, 0.150, 0.860
POSTE_LARGURA = 0.062
POSTE_LARGURA_SIMPLES = 0.094

#: O pano: um triângulo que sai do topo do poste. O bico não chega à borda --
#: sobra de margem é o que impede o ícone de encostar no vizinho na barra.
PANO_PONTOS = [(0.330, 0.180), (0.812, 0.330), (0.330, 0.480)]

#: A faixa branca dentro do pano, paralela à hipotenusa. Some abaixo de 32 px:
#: ali ela mede meio pixel e vira sujeira cinza.
FAIXA_PONTOS = [(0.360, 0.300), (0.560, 0.362), (0.360, 0.408)]

#: A base do poste, um disco achatado -- sem ela a bandeirinha parece flutuar.
BASE_RX, BASE_RY = 0.110, 0.040


def _gradiente(lado: int) -> Image.Image:
    img = Image.new("RGBA", (lado, lado))
    d = ImageDraw.Draw(img)
    for y in range(lado):
        t = y / max(1, lado - 1)
        cor = tuple(int(a + (b - a) * t)
                    for a, b in zip(FUNDO_TOPO, FUNDO_BASE))
        d.line([(0, y), (lado, y)], fill=cor + (255,))
    return img


def _ladrilho(lado: int) -> Image.Image:
    raio = int(lado * 0.22)
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [0, 0, lado - 1, lado - 1], radius=raio, fill=255)
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    img.paste(_gradiente(lado), (0, 0), mascara)
    ImageDraw.Draw(img).rounded_rectangle(
        [0, 0, lado - 1, lado - 1], radius=raio,
        outline=FUNDO_BORDA + (255,), width=max(1, int(lado * 0.016)))
    return img


def _bandeirinha(lado: int, simples: bool) -> Image.Image:
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.polygon([(x * lado, y * lado) for x, y in PANO_PONTOS],
              fill=PANO + (255,))
    if not simples:
        d.polygon([(x * lado, y * lado) for x, y in FAIXA_PONTOS],
                  fill=FAIXA + (255,))

    largura = POSTE_LARGURA_SIMPLES if simples else POSTE_LARGURA
    d.rectangle([(POSTE_X - largura / 2) * lado, POSTE_TOPO * lado,
                 (POSTE_X + largura / 2) * lado, POSTE_BASE * lado],
                fill=POSTE + (255,))
    d.ellipse([(POSTE_X - BASE_RX) * lado, (POSTE_BASE - BASE_RY) * lado,
               (POSTE_X + BASE_RX) * lado, (POSTE_BASE + BASE_RY) * lado],
              fill=POSTE + (255,))
    return img


def icone(tamanho: int) -> Image.Image:
    lado = tamanho * SS
    img = _ladrilho(lado)
    img.alpha_composite(_bandeirinha(lado, tamanho < SIMPLES_ABAIXO))
    return img.resize((tamanho, tamanho), Image.LANCZOS)


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for tamanho in TAMANHOS:
        caminho = SAIDA / f"we2002Lazarus-{tamanho}.png"
        icone(tamanho).save(caminho, optimize=True)
        print(f"  {caminho.relative_to(RAIZ)}  {caminho.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
