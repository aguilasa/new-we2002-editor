---
handler: barra2Change
formulario: ficha_color
endereco: 0x00406384
veredito: implementado
---

# ficha_color.barra2Change

A trilha do **fim** da faixa. Espelho exato do
[`barra1Change`](ficha_color.barra1Change.md), com o sinal invertido.

**Evidência:** disassembly lido

## Entrada

`barra1.Position` (`[this+0x364]`) e `barra2.Position` (`[this+0x360]`).

**Evidência:** disassembly lido

## Saída

```text
se barra1.Position >= barra2.Position:
    barra2.Position := barra1.Position + 1
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

Não trata; satura no `Max = 16` pelo mesmo caminho que o irmão satura no `Min`.

**Evidência:** disassembly lido

## Notas

A comparação é `>=` aqui e `<=` lá, e é isso que impede as duas pontas de
coincidirem: `faixa_fim` é sempre pelo menos `faixa_ini + 1`, e o gradiente
divide por `faixa_fim - faixa_ini` sem nunca dividir por zero. A invariante não
é decorativa — ela é a pré-condição do
[`gradienteClick`](ficha_color.gradienteClick.md).

A rotina de apoio `0x004062b4` está descrita na spec do irmão.
