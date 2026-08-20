---
handler: paizquierda2Click
formulario: MainForm
endereco: 0x0040e85c
veredito: implementado
---

# MainForm.paizquierda2Click

A seta `<<`: move os **vinte e três** jogadores do time da direita para o da
esquerda. **316 bytes**, espelho do
[`paderecha2Click`](MainForm.paderecha2Click.md).

## Entrada

- `lista_equipos_2.ItemIndex` — a origem; o slot é o contador do laço, 0..22.
- `lista_equipos_1.ItemIndex`, `lista_jugadores_1.ItemIndex` — o destino.
- `_ficha_movertodos` (`0x00432e48`), o arquivo aberto (`0x00432e58`) e
  `WORD[0x004335c0]`.

**Evidência:** disassembly lido

## Saída

```text
guarda := lista_jugadores_1.ItemIndex
se ficha_movertodos.ShowModal <> 6: sai

para slot := 0 ate 22:
    0x004046e8(lista_equipos_2.ItemIndex, slot, buffer := 2, arquivo)
    0x00404820(buffer := 2, lista_equipos_1.ItemIndex, slot, arquivo)

0x0040b2d8(lista_equipos_1, lista_jugadores_1)
lista_jugadores_1.Update
lista_jugadores_1.ItemIndex := guarda
0x004046e8(lista_equipos_1.ItemIndex,
           lista_jugadores_1.ItemIndex, buffer := 1, arquivo)

casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
```

**Evidência:** disassembly lido

## Bytes tocados

**Grava vinte e três vezes**, dentro da `0x00404820`. Offset por ramo é da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

Só o `mrYes` do `ficha_movertodos`. O port acrescenta o teste de
`ItemIndex >= 0`.

**Evidência:** disassembly lido

## Comportamento de erro

**Nenhum** — os 23 códigos são descartados e a `0x00403e20` não é chamada, como
no `paderecha2Click`.

**Evidência:** disassembly lido

## Notas

**Veredito `implementado`:** o Pascal
([`../../src/impl/ep2002_mainform.paizquierda2Click.inc`](../../src/impl/ep2002_mainform.paizquierda2Click.inc))
faz tudo, gravação inclusive.

Fechado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md): o ramo de
**destino de Master League** da `0x00404820` foi portado, com golden verde
([`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt)) e o
contador de blocos livres vindo da
[WTE-TASK-33](../../../docs/tasks/33-slots-de-master-league.md). Com ele a
recusa `-1` passou a ser alcançável e o `casilla_xmlibres` mostra o número de
verdade.

Corpo compartilhado com o `paderecha2Click` na `MoveTodosOsJogadores` do
[`.aux.inc`](../../src/impl/ep2002_mainform.aux.inc).
