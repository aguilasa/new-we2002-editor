---
handler: barra1Change
formulario: ficha_color
endereco: 0x00406358
veredito: implementado
---

# ficha_color.barra1Change

A trilha do **início** da faixa que o gradiente, o escurecer e o clarear
percorrem. Onze instruções.

**Evidência:** disassembly lido

## Entrada

`barra1.Position` (`[this+0x364]`) e `barra2.Position` (`[this+0x360]`), campo
`FPosition` em `+0x228` do `TTrackBar`. As duas trilhas são `Min = 1`,
`Max = 16` no `.dfm` — **base um**, a mesma do vetor do original, onde
`faixa_fim` é o elemento zero (ver o cabeçalho de
[`wte_cor.pas`](../../src/wte_cor.pas)).

**Evidência:** disassembly lido

## Saída

```text
se barra2.Position <= barra1.Position:
    barra1.Position := barra2.Position - 1
0x004062b4()
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Com `barra2.Position = 1` a correção pediria `0`, abaixo do `Min`, e
o `TTrackBar` satura em 1 nos dois widgetsets — a invariante fica violada e
ninguém reclama. É defeito do original e está reproduzido.

**Evidência:** disassembly lido

## Notas

### Quem cede é o próprio controle

Este handler abaixa a **`barra1`**, e o `barra2Change` sobe a **`barra2`** —
cada um corrige o controle que o usuário acabou de mexer. Trocar isso faria a
faixa andar sozinha quando uma ponta é empurrada contra a outra.

A correção reentra no handler (escrever `Position` dispara `OnChange`), e a
segunda passagem já acha a invariante valendo. É o que faz a recursão parar.

### A `0x004062b4` — `AtualizaFaixa`

Ela é chamada pelos dois handlers de trilha e por mais ninguém. Lê as duas
posições para os globais e move os três indicadores da faixa:

```text
0x00433dcc (faixa_ini) := barra1.Position
0x00433dd0 (faixa_fim) := barra2.Position

seleccion.Left         := faixa_ini*32 - 11
seleccion.Width        := 0x1f7 - 32*(15 - faixa_fim + faixa_ini)
flecha_izquierda.Left  := faixa_ini*32 - 19
flecha_derecha.Left    := 0x1ff - 32*(16 - faixa_fim)
```

O `32` é a largura de uma amostra; os outros quatro números são coordenadas de
tempo de projeto e não se derivam de nada. **A única régua deles é a tela.**

Os três alvos saem da *published field table*: `0x2f0` é `seleccion`, `0x2f4` é
`flecha_izquierda` e `0x2f8` é `flecha_derecha` — ver
[`campos.tsv`](../campos.tsv). Contar componentes na ordem do `.dfm` daria os
mesmos três aqui, mas não dá em geral, e a tabela é a fonte.
