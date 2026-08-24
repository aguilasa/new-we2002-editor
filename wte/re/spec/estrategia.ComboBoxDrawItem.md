---
handler: ComboBoxDrawItem
formulario: estrategia
endereco: 0x0040adec
veredito: nao portado
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

## Justificativa

**A decisão que este corpo exige pertence, por escrito, a outra fase — e a
espera era circular.**

`OnDrawItem` da LCL entrega `TCanvas` e `TRect` como a VCL, mas o momento e o
estado do canvas não são os mesmos, e desenho é a categoria em que a diferença
aparece como "quase igual" — o pior resultado possível para comparar. O corpo
depende de escolher entre **o port desenhar** e **deixar a LCL desenhar**, e
essa é a pergunta da conferência de UI da
[WTE-TASK-37](../../../docs/tasks/37-reconferencia-de-ui.md), que olha os 18
formulários com a lógica ligada e dado carregado.

**O ciclo, medido em 2026-08-24:** a WTE-TASK-37 é fase 6 e depende da
[WTE-TASK-34](../../../docs/tasks/34-bateria-golden-completa.md), que depende da
[WTE-TASK-31](../../../docs/tasks/31-fechamento-fase-4.md), que é o fechamento
da fase 4 e exige que este veredito deixe de ser `aberto`. Manter `aberto`
travava as três para sempre.

**Por que a razão é de escopo e não de dificuldade** — que é o que o critério
da fase 4 exige distinguir. O corpo tem 422 bytes e a Saída acima já o descreve:
dois `Rectangle` com `TColor` diferentes e o texto por cima. Não falta medida, e
o Pascal seria curto. O que falta é a **decisão de política de desenho**, que
vale para os dois combos desta tela e para qualquer outro *owner-draw* que
apareça, e tomá-la aqui — dentro do fechamento de uma fase que não implementa —
a tomaria no lugar errado, com um caso só à vista.

**O efeito no port, para não ficar implícito:** os dois combos são
`csOwnerDrawFixed` no `.lfm`, como no DFM, e o handler é stub. A LCL desenha o
item pelo padrão dela. É diferença visível de tela, não de byte — este handler
não toca a imagem, como a seção *Bytes tocados* mede.

Entrada da WTE-TASK-37, e a decisão que ela tomar vira ou um corpo aqui, ou uma
linha na [WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md).

## Notas

O `estrategia` inteiro só fica alcançável pelo `mostrar_estrategiaClick`, e a
tela de tática é da [WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md).
