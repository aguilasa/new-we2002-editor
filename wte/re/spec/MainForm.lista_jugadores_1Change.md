---
handler: lista_jugadores_1Change
formulario: MainForm
endereco: 0x0040f8b8
veredito: aberto
---

# MainForm.lista_jugadores_1Change

O menor handler do `MainForm`: **28 bytes**, e o corpo inteiro é uma chamada.

## Entrada

`lista_jugadores_1.ItemIndex` — o jogador escolhido na lista do time titular.
O campo é o de deslocamento `0x388`, pelo [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

## Saída

Chama a rotina em `0x0040b188` passando `ItemIndex + 1` — um argumento, na
pilha, convenção `cdecl` (o chamador limpa com `pop ecx`). Nada mais: o handler
não toca controle nenhum diretamente.

O `+1` é a única aritmética do corpo, e diz que a rotina numera jogador a
partir de 1 enquanto o combo numera a partir de 0.

**Evidência:** disassembly lido

## Bytes tocados

Nenhum **neste corpo**. O que a rotina chamada faz ainda não foi medido.

**Evidência:** nao medido

## Pré-condições

Nenhuma. Não confere `ItemIndex = -1`: com a lista vazia o argumento vira `0`,
e é a rotina chamada que decide o que fazer com isso.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto` porque a resposta está toda em `0x0040b188`**, que é a
mesma rotina que o
[`lista_equiposChange`](MainForm.lista_equiposChange.md) chama com `1` no fim
da carga — isto é, "mostrar o jogador 1". Ler os dois juntos custa uma medição
em vez de duas, e é o que a próxima passagem da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md) faz.

Handler de 28 bytes cujo veredito depende de uma rotina de fora é o caso que o
gabarito prevê ao permitir `nao medido` numa seção só: a spec diz exatamente
até onde a medição chegou, em vez de fingir que 28 bytes bastam.
