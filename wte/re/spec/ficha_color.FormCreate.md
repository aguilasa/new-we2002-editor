---
handler: FormCreate
formulario: ficha_color
endereco: 0x00405dcc
veredito: implementado
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

**A decisão que este parágrafo adiou foi tomada na quinta passagem da
[WTE-TASK-29](../../../docs/tasks/concluidos/29-camisa-e-bandeira-2d.md), em 2026-08-21.**
Até lá o veredito era `aberto` de propósito: os cinco globais em
`0x00433dc0`…`0x00433dd0` são o estado do editor de cor 2D, e escrever este
corpo antes de decidir onde esse estado mora significaria inventar.

Ele mora em [`wte/src/wte_cor.pas`](../../src/wte_cor.pas), e cada um tem nome:

| global | campo | base |
|---|---|---|
| `0x00433dc4` | `familia` — qual paleta se edita (0..3) | — |
| `0x00433dc8` | `conjunto` — qual jogo dentro dela | — |
| `0x00433dc0` | `entrada` — qual das 16 está selecionada | **zero** |
| `0x00433dcc` | `faixa_ini` — começo da faixa do gradiente | **um** |
| `0x00433dd0` | `faixa_fim` — fim dela, e vale 16 no arranque | **um** |

**As bases não são as mesmas, e a razão é um alias.** O vetor das 16 palavras
fica em `0x00433dd4`…`0x00433e10`, e o pintor de amostra escreve em
`[indice*4 + 0x00433dd0]` com `indice` de 1 a 16 — ou seja **o `faixa_fim` é o
elemento zero do vetor**, e os dois nunca colidem porque o pintor começa em 1.
No port são campos separados, com nome; o alias fica no comentário, mas as
bases têm de ser respeitadas.

O `16` do fim é o tamanho das paletas do formulário — o DFM tem `color1`…
`color16` e `colcop0`…`colcop16`.
