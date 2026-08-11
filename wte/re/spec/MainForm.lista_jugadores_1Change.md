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

**Nenhum**, nem neste corpo nem na rotina chamada: `0x0040b188` só mexe em
propriedade de controle. Medida em
[`../auxiliares.md`](../auxiliares.md) — 335 bytes, sem uma única chamada de
leitura ou escrita de arquivo.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não confere `ItemIndex = -1`: com a lista vazia o argumento vira `0`,
e é a rotina chamada que decide o que fazer com isso.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**`0x0040b188` está medida.** É a mesma rotina que o
[`lista_equiposChange`](MainForm.lista_equiposChange.md) chama com `1` no fim
da carga — isto é, "mostrar o jogador 1" —, e ela **marca uma camisa**: apaga a
que estava marcada, acha a nova por nome e a destaca.

```text
se ha camisa marcada (o ponteiro global nao e nulo):
    Font.Size  := 8
    Left       := Left + 5      ; Width  := Width - 10
    Top        := Top + 5       ; Height := Height - 10
    Color      := $808080       ; Font.Color := $C0C0C0
    manda para tras
marcada := MainForm.FindComponent('dorsal' + numero)
    traz para frente
    Left       := Left - 5      ; Width  := Width + 10
    Top        := Top - 5       ; Height := Height + 10
    Color      := $FFFFFF       ; Font.Color := $0000FF   ' vermelho
    Font.Size  := 14
```

As cores estão no `$00BBGGRR` da VCL: `$0000FF` é vermelho puro, e escrevê-lo
como `#0000FF` pintaria de azul. Os nomes de propriedade não são inferência —
saem dos símbolos importados do `vcl60.bpl` (`TControl::SetLeft`, `SetWidth`,
`SetTop`, `SetHeight`, `SetColor`, `BringToFront`, `SendToBack`,
`TFont::SetSize`, `TFont::SetColor`) e do `TComponent::FindComponent`.

**O ponteiro global é o mesmo que derrubava o oráculo.** É o `0x004335e4` da
[`../crash-causa.md`](../crash-causa.md): o resultado do `FindComponent` é
guardado sem conferência, e com a ROM europeia a carga de time o sobrescreve
com dado de tabela vizinha. Aqui está o outro lado da mesma história — a rotina
que grava esse ponteiro.

**Veredito ainda `aberto`, e por decisão de destino, não de medição.** A spec
basta para escrever o Pascal; o que falta é decidir **onde mora** um auxiliar
que não é handler: `wte/src/impl/` guarda um `.inc` por handler, e essa rotina
é chamada por dois. Escolher errado agora custa mais do que esperar a
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md), que traz outros
auxiliares compartilhados e decide a casa dos dois juntos.
