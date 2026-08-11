---
handler: ComboBoxDrawItem
formulario: estrategia
endereco: 0x0040adec
veredito: aberto
---

# estrategia.ComboBoxDrawItem

Desenho por conta própria (*owner-draw*) dos dois combos da tela de tática.
422 bytes. Ligado a `ComboBox1.OnDrawItem` **e** a `ComboBox2.OnDrawItem` — os
dois compartilham o corpo, e é a coluna `componente` do
[`../published_methods.tsv`](../published_methods.tsv) que diz isso.

## Entrada

O item a desenhar e o retângulo, que a VCL passa nos argumentos, mais
`ComboBox1` para descobrir o texto.

**Evidência:** disassembly lido

## Saída

Pinta no canvas do combo: duas chamadas a `Rectangle` com `TColor` diferentes
antes e depois, e o texto por cima. É desenho, não estado — nada fora do
canvas muda.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não abre arquivo nem lê a imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma no corpo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto`, e a razão é de framework, não de medição.** `OnDrawItem`
da LCL entrega `TCanvas` e `TRect` como a VCL, mas o momento e o estado do
canvas não são os mesmos, e desenho é a categoria em que a diferença aparece
como "quase igual" — que é o pior resultado possível para comparar. O corpo
depende de decidir se o port desenha ou deixa a LCL desenhar, e essa decisão
pertence à conferência de UI da
[WTE-TASK-37](../../../docs/tasks/37-reconferencia-de-ui.md), que olha a tela
com a lógica ligada.

O `estrategia` inteiro só fica alcançável pelo `mostrar_estrategiaClick`, e a
tela de tática é da [WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md).
