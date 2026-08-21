---
handler: lista_col0Change
formulario: ficha_color
endereco: 0x0040688c
veredito: implementado
---

# ficha_color.lista_col0Change

O combo de **forma** da bandeira. Nove instruções, e a mais interessante é a
segunda.

**Evidência:** disassembly lido

## Entrada

`lista_col0.ItemIndex` (`[this+0x39c]`) — de 0 a 94, um por time. O `.dfm` traz
95 itens, todos com nome de país ou clube.

**Evidência:** disassembly lido

## Saída

```text
byte[0x00432f15] := byte[0x004231e8 + lista_col0.ItemIndex]
0x00405270()                     ' redesenha a bandeira em vigor
```

```asm
40688f:  mov eax,[ebx+0x39c]      ; lista_col0
406897:  call [edx+0xc8]          ; GetItemIndex
40689d:  mov cl,[eax+0x4231e8]    ; FORMA_PADRAO[ItemIndex]
4068a3:  mov ds:0x432f15,cl       ; a forma EM VIGOR
4068a9:  call 0x405270            ; desenha
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

`ItemIndex >= 0`. O combo é o único dos quatro com `Enabled` verdadeiro no
`.dfm`.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata: `ItemIndex = -1` leria `byte[0x004231e7]`, que é o final da tabela
anterior. O port sai sem fazer nada.

**Evidência:** disassembly lido

## Notas

### O combo **indexa** a tabela em vez de digitar a forma

São 95 itens para 53 formas distintas, e é por isso: cada item é um time, e o
que vai para a forma em vigor é `FORMA_PADRAO[time]`. A consequência prática é
que **os oito índices sem arquivo (44..51) nunca são pedidos** — nenhum time os
usa, então nenhum item os alcança. A assimetria está na seção 3.2 do
[`assets.md`](../assets.md), e é o único consumidor daquela tabela: o desenho
lê a forma do disco, não dela.

### Onde a forma em vigor mora no port

`0x00432f15` é o *slot 1* do par de bytes de forma (`0x00432f14` é o slot 0). O
port não tem os dois slots: ele grava em `flag_shape` do `Jogo`, pela mesma
razão que a `SalvaPaleta` grava as cores ali — ver o cabeçalho de
[`wte_cor.pas`](../../src/wte_cor.pas). Quem precisaria do slot 0 é o desfazer
do `BitBtn1`, que ainda não foi portado.
