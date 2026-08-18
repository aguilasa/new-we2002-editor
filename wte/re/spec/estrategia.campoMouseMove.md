---
handler: campoMouseMove
formulario: estrategia
endereco: 0x004090c8
veredito: implementado
---

# estrategia.campoMouseMove

Sair de uma bola para o gramado apaga o destaque. **52 bytes** — o menor
handler do grupo de edição.

## Entrada

Só os dois globais `0x00434340` e `0x00434344`. Não olha `Sender`, não olha
`X`/`Y`, não olha `Shift`.

**Evidência:** disassembly lido

## Saída

```text
[0x434340].Brush.Color := $008000
[0x434344].Font.Color  := $C0C0C0
```

São, literalmente, as duas primeiras linhas do
[`bolaMouseMove`](estrategia.bolaMouseMove.md). O original não as fatorou; o
port as tem numa rotina só, no `.aux.inc`.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Duas chamadas, ambas `SetColor`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata — mesmo modo de falha do `bolaMouseMove` com os globais zerados.

**Evidência:** disassembly lido

## Notas

**Este endereço custou uma correção de custo, e vale registrar como se erra.**
O plano de fechamento da task dava a este handler **1.404 bytes**, que é a
distância até o próximo handler *publicado* (`rectanguloDragOver`). Entre um e
outro mora o `estrategia.FormCreate` (`0x004090fc`, 1.352 B), que é publicado
mas não estava na conta. Medir corpo por subtração de endereços vizinhos
**superestima em silêncio** sempre que houver rotina não listada no meio — e o
erro aparece como "este lote é caro demais para uma passagem", que é uma
decisão de escopo tomada sobre número errado.

O corpo real tem 52 bytes.
