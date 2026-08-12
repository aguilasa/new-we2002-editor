---
handler: scroll_dorsalChange
formulario: ficha_dorsal
endereco: 0x00402b58
veredito: implementado
---

# ficha_dorsal.scroll_dorsalChange

A janelinha de escolher número de camisa tem uma barra vertical e um rótulo
grande. Este handler é a ligação entre os dois, e é **uma linha**.

## Entrada

`scroll_dorsal.Position` e `scroll_dorsal.Max` — os campos `0x20c` e `0x214` da
instância de `TScrollBar`, lidos direto, sem getter.

**Evidência:** disassembly lido

## Saída

```text
etiq_dorsal.Caption := IntToStr(Max - Position + 1)
```

**A inversão é o ponto.** A barra é vertical (`Kind = sbVertical` no DFM), e
numa barra vertical a posição cresce para baixo — então o número maior tem de
ficar em cima, e a conta subtrai. Quem escolhe o número é o
[`dorsalClick`](MainForm.dorsalClick.md), que faz a conta ao contrário
(`Position := Max - numero + 1`); as duas se cancelam e o rótulo mostra o
número pedido.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Nem lê nem grava a imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. A faixa é garantida pelo `Min`/`Max` da própria barra — que é onde a
regra de validação do número mora, e não num `if`; ver a
[spec do `dorsalClick`](MainForm.dorsalClick.md).

**Evidência:** disassembly lido

## Notas

**Os deslocamentos de campo do `TScrollBar` foram lidos errado na primeira
tentativa, e o modo de errar vale registrar.** A primeira leitura varreu os
prólogos de `SetMin`/`SetMax`/`SetPosition` atrás de `mov reg,[this+disp]` e
concluiu `FMin = 0x20c`, `FMax = 0x210`, `FPosition = 0x214` — pela interseção
de quais campos cada uma toca. Com esses valores a conta deste handler vira
`Position - Min + 1`, que com `Min = 1` é a identidade, e **a leitura parecia
perfeitamente plausível**.

O que a desmentiu foi a consistência com o `dorsalClick`: ele faz
`Position := [0x214] - numero + 1`, e só sob `[0x214] = FMax` as duas contas se
cancelam e o rótulo mostra o número escolhido. Refeita a leitura pelo caminho
certo — as três não escrevem campo nenhum, são invocações finas do mesmo
`SetParams(Position, Min, Max)`, e a ordem em que cada uma carrega os
argumentos identifica os três sem ambiguidade:

| método | edx | ecx | pilha | conclusão |
|---|---|---|---|---|
| `SetPosition(v)` | `v` | `[0x210]` | `[0x214]` | Position = arg, Min = `0x210`, Max = `0x214` |
| `SetMin(v)` | `[0x20c]` | `v` | `[0x214]` | **Position = `0x20c`** |
| `SetMax(v)` | `[0x20c]` | `[0x210]` | `v` | consistente |

**`FPosition = 0x20c`, `FMin = 0x210`, `FMax = 0x214`.** A lição é a armadilha 1
do projeto por outra porta: interseção de campos tocados é heurística, e
heurística que "fecha" num caso (`Min = 1`) é a que passa despercebida. O que
decide é a semântica cruzada de dois handlers.

Pascal em
[`../../src/impl/ep2002_dorsal.scroll_dorsalChange.inc`](../../src/impl/ep2002_dorsal.scroll_dorsalChange.inc).
