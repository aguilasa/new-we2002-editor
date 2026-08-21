---
handler: malla2MouseDown
formulario: estrategia
endereco: 0x0040a000
veredito: implementado
---

# estrategia.malla2MouseDown

A malha de **seis** colunas, dos `tiradorN`. Instrução por instrução é o
[`malla1MouseDown`](estrategia.malla1MouseDown.md): os dois corpos têm 180 bytes
e a mesma sequência, e o que muda são dois imediatos.

**Evidência:** disassembly lido

## Entrada

Igual à do irmão, com `malla2` (`[this+0x398]`) no lugar de `malla1`.

**Evidência:** disassembly lido

## Saída

```text
se Button <> mbLeft: sai

indice := X div 24 + 1
tirador<indice>.Top := malla2.Top + (Y div 16) * 16 + 3
```

Os dois imediatos que separam os dois handlers:

| | `malla1MouseDown` | `malla2MouseDown` |
|---|---|---|
| cadeia do prefixo | `0x00424bbf` = `"simbolo"` | `0x00424bc7` = `"tirador"` |
| campo da `TImage` | `[this+0x384]` = `malla1` | `[this+0x398]` = `malla2` |

**Evidência:** disassembly lido

## Bytes tocados

Nenhum.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Igual ao do irmão.

**Evidência:** disassembly lido

## Notas

### O original não fatorou, e o port fatorou

Os 180 bytes são duplicados no binário. Aqui os dois handlers chamam
`MoveMarcadorDaMalha` no `.aux.inc`, com prefixo, contagem de colunas e imagem
como argumento. Não é reescrita de comportamento: é a mesma conta com os mesmos
três números, e os dois números que diferem entram por parâmetro.

### A régua mede a `malla1`, e o que ela prende vale para as duas

`compara_tela.sh --malha` clica na `malla1`. Não há modo para a `malla2`, e a
razão está na tabela acima: os dois corpos são a mesma sequência de instruções,
e o que os separa — a cadeia do prefixo e o campo da `TImage` — é conferido
estaticamente pelo [`dump_zonas.py`](../../tools/dump_zonas.py), que **aborta**
se o prefixo ou o campo deixarem de ser os esperados. Um modo de tela para a
`malla2` mediria a mesma aritmética uma segunda vez.

### De qual `TImage` cada um lê, e como isso se sabe

O `.text` diz `[esi+0x384]` e `[esi+0x398]`, e não diz de quem. Quem decide é a
*published field table* — [`campos.tsv`](../campos.tsv) —, e o
[`dump_zonas.py`](../../tools/dump_zonas.py) a consulta e **aborta** se o
deslocamento deixar de nomear a malha esperada. Contar componentes na ordem do
`.dfm` é o atalho que já deu o resultado oposto ao certo no `ficha_color`.
