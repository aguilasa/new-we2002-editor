---
handler: gradienteClick
formulario: ficha_color
endereco: 0x004063b0
veredito: implementado
---

# ficha_color.gradienteClick

Interpola entre as cores das duas pontas da faixa e preenche o **miolo**. É o
handler que a §9 do plano nomeia como o risco médio do projeto, e a causa que
ela nomeia — arredondamento — está medida em
[`render2d.md`](../render2d.md).

**Evidência:** disassembly lido

## Entrada

- `0x00433dcc` (`faixa_ini`) e `0x00433dd0` (`faixa_fim`), base **um**, escritos
  pelas duas trilhas;
- o vetor `0x00433dd4`, 16 palavras de 32 bits, base **zero**;
- `boton0.Checked` e `boton1.Checked`, no fim.

**Evidência:** disassembly lido

## Saída

```text
n := faixa_fim - faixa_ini
a[c] := canal c de vetor[faixa_ini-1], em CINCO bits
b[c] := canal c de vetor[faixa_fim-1], em CINCO bits
passo[c] := Single(b[c] - a[c]) / Single(n)      ' precisao SIMPLES
acumulado[c] := 0

para i := faixa_ini + 1 ate faixa_fim - 1:       ' o MIOLO, pontas de fora
    acumulado[c] := acumulado[c] + passo[c]
    palavra := vetor[faixa_ini-1]
             + trunca(acumulado[0])
             + trunca(acumulado[1]) shl 5
             + trunca(acumulado[2]) shl 10
    0x00405bc8(i, palavra)                       ' pinta a amostra i

<poe as tres barras na cor da amostra selecionada>
se boton0.Checked: 0x00405b48(); 0x00405270()
se boton1.Checked: 0x00405b48(); 0x004056c8([0x4335cc], lista_col1.ItemIndex)
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem. Ver a nota do [`barraChange`](ficha_color.barraChange.md).

**Evidência:** disassembly lido

## Pré-condições

`faixa_fim > faixa_ini`, garantida pelas duas trilhas — ver
[`barra2Change`](ficha_color.barra2Change.md). Sem ela a divisão por `n` seria
por zero.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

### As pontas **não** são reescritas

O laço do original é `for (i = faixa_ini + 1; i < faixa_fim; i++)`
(`cmp ebx,[0x433dd0]` com `jl`), e portanto preenche `n - 1` entradas. Escrever
`n` apagaria a cor que o usuário escolheu na ponta de cima — foi o off-by-one
que a segunda passagem desta task pegou antes do teste, relendo o laço para
escrever o cabeçalho da função.

### Truncar, e não arredondar — as duas causas do risco da §9

1. o passo e o acumulador são `Single` (`fstp DWORD PTR [esi]`), e não `Double`;
2. a conversão para inteiro passa pelo `__ftol` da RTL (`0x00419d80`), que põe
   `0xc01` no control word do 387 — bits 10–11 em `11`, que é *round toward
   zero*.

Escrever `Round` desloca a rampa inteira de um degrau em metade dos casos, e o
[`dump_render2d.py`](../../tools/dump_render2d.py) **recusa** emitir se a
unidade Pascal contiver `Round(acumulado`.

### A soma é sobre a palavra de partida, e não canal a canal

O original não recompõe `R|G|B`: soma os três deslocamentos truncados **sobre a
palavra inicial inteira**. Escrever isso como "interpola cada canal e
reempacota" dá o mesmo resultado quase sempre, e diferente exatamente onde o
truncamento morde.
