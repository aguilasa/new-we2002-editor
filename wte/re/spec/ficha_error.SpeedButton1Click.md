---
handler: SpeedButton1Click
formulario: ficha_error
endereco: 0x00420f08
veredito: trivial
---

# ficha_error.SpeedButton1Click

O ponto de interrogação da janela de erro: abre o `ficha_info2`, que explica
os blocos livres de Master League. Quatorze bytes.

**Evidência:** disassembly lido

## Entrada

A global `_ficha_info2` — e aqui o endereço é `0x0043B430`, não um dos
`0x00432Exx` dos outros. O `.exe` exporta o nome `_ficha_info2` uma vez só, e
é esse.

**Evidência:** disassembly lido

## Saída

```text
ficha_info2.ShowModal()
```

Resultado descartado.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**O texto do `ficha_info2` está em inglês, e o resto do app em português.** É a
tradução PT-BR do chagas_michel que não chegou nesse formulário; o
[`strings.tsv`](../strings.tsv) mostra os dois idiomas convivendo em vários
lugares. O port copia os rótulos como estão — traduzir seria mudar a tela sem
o original mudar junto.

Quem mostra o `ficha_error` é o `MostraCodigo` do
[`ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc): é a janela
de "não deu para mover o jogador", e o `ficha_info2` explica por que os blocos
acabam.
