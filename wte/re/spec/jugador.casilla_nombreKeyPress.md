---
handler: casilla_nombreKeyPress
formulario: jugador
endereco: 0x00408af8
veredito: implementado
---

# jugador.casilla_nombreKeyPress

Filtro de tecla do campo de nome da ficha do jogador. 88 bytes.

## Entrada

`Key`, por referência.

**Evidência:** disassembly lido

## Saída

```text
se Key = #13:
    casilla_dorsal.SetFocus          ' VMT slot 0xc0, incondicional

se Key nao esta em { ' ', '.', #8, '0'..'9', 'A'..'Z', 'a'..'z' }:
    Key := #0
```

Primeiro o foco, depois o filtro — mesma ordem, e mesma razão, do
[`casilla_dorsalKeyPress`](jugador.casilla_dorsalKeyPress.md).

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Ao contrário do irmão, o `SetFocus` aqui **não** é condicionado a
tabela nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Tecla recusada vira `#0`, sem aviso.

**Evidência:** disassembly lido

## Notas

**O conjunto aceito é o mesmo do filtro de exibição de nome.** Letra, dígito,
ponto e espaço — exatamente as quatro classes que a rotina `0x0040b2d8` deixa
passar ao montar a lista de jogadores, medida na
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md). O autor filtrou a
entrada com a mesma régua que usa na saída; a diferença é que ali byte acima de
`z` vira `?` e aqui a tecla simplesmente não entra.

As comparações são de faixa, escritas à mão (`0x30..0x39`, `0x41..0x5a`,
`0x61..0x7a`), e não `isalnum` — ao contrário do irmão, que chama `isdigit` da
RTL. Sem consequência prática em ASCII; registrado porque a assimetria é do
original.

**Não há limite de comprimento aqui.** O truncamento vem do `MaxLength` do
`TEdit` e do buffer de gravação, e inventariar isso é a
[WTE-TASK-36](../../../docs/tasks/36-buffers-e-truncamento.md).

Pascal em
[`../../src/impl/ep2002_jugador.casilla_nombreKeyPress.inc`](../../src/impl/ep2002_jugador.casilla_nombreKeyPress.inc).
