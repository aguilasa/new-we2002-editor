---
handler: barrhab_bisScroll
formulario: jugador
endereco: 0x00407bb4
veredito: implementado
---

# jugador.barrhab_bisScroll

As sete últimas barras de habilidade da ficha, `barrhab10..16`. **300 bytes**, e
é cópia literal do [`barrhabScroll`](jugador.barrhabScroll.md) com um número
trocado.

## Entrada

Igual à do irmão, com **`Copy(Sender.Name, 8, 2)`** no lugar de `Copy(..., 8, 1)`
— dois dígitos em vez de um.

**Evidência:** disassembly lido

## Saída

Idêntica à do [`barrhabScroll`](jugador.barrhabScroll.md): largura de
`imghab<n>`, legenda de `valorhab<n>` e a cor pela `0x00406fb4`. O conjunto de
chamadas dos dois corpos é o mesmo, símbolo por símbolo.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum**, pela mesma medição — nenhuma escritora de imagem entre as chamadas.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma no original; o port acrescenta o teste de `Sender is TComponent`.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**O `_bis` do nome é a largura do número, não outra família de controles** — o
`.lfm` tem 16 `barrhab` numerados de 1 a 16 e nenhum `barrhab_bis`. A discussão
inteira, e a medição do `TScrollBar` disparando `OnChange` na LCL, estão na spec
do [`barrhabScroll`](jugador.barrhabScroll.md).

**Veredito `implementado`** pela mesma razão: não grava, o efeito é tela, e a
ordem dos dezesseis é sustentada pelo
[`check_bitfields.py`](../../tools/check_bitfields.py).

Pascal em
[`../../src/impl/ep2002_jugador.barrhab_bisScroll.inc`](../../src/impl/ep2002_jugador.barrhab_bisScroll.inc).
