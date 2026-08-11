---
handler: FormCreate
formulario: ficha_color
endereco: 0x00405dcc
veredito: aberto
---

# ficha_color.FormCreate

## Entrada

Nada da tela e nada da imagem. O corpo só escreve.

**Evidência:** disassembly lido

## Saída

Forma `composto` do [`../arranque.md`](../arranque.md), 116 bytes, em quatro
movimentos:

```text
Color := $00E68F41                  ' RGB(65, 143, 230)
<dois globais do editor 2D> := 0    ' 0x00433dc4 e 0x00433dc0
color1.BringToFront
recuadro2.BringToFront
lista_col1.ItemIndex := 0
lista_col2.ItemIndex := 0
<três globais> := 0, 1, 16          ' 0x00433dc8, 0x00433dcc, 0x00433dd0
```

Os campos saem do [`../campos.tsv`](../campos.tsv): `0x2fc` = `color1`
(`TLabel`), `0x33c` = `recuadro2` (`TBevel`), `0x398` = `lista_col1` e `0x390`
= `lista_col2` (`TComboBox`). O slot `0xCC` do VMT de `TComboBox` é
`Stdctrls::TCustomCombo::SetItemIndex`.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não há chamada de I/O de arquivo no corpo — os importados chamados
são `TControl::SetColor` e `TControl::BringToFront`, mais a chamada virtual do
`ItemIndex`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto` de propósito, e o que falta é o Pascal, não a medição.** Os
cinco globais em `0x00433dc0`…`0x00433dd0` são o estado do editor de cor 2D, e
quem os lê são os outros 16 handlers do `ficha_color` (edição, na
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md)) e o render da
[WTE-TASK-32](../../../docs/tasks/32-camisa-e-bandeira-2d.md). Escrever este
corpo antes deles significaria inventar onde esse estado mora, e a decisão é
das duas tasks que o consomem — não desta.

O que já dá para dizer sobre eles: dois são zerados antes das chamadas de
z-order, e três recebem `0`, `1` e `16` no fim. O `16` é o tamanho das paletas
do formulário — o DFM tem `color1`…`color16` e `colcop0`…`colcop16`.
