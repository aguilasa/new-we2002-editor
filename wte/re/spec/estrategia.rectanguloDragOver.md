---
handler: rectanguloDragOver
formulario: estrategia
endereco: 0x00409644
veredito: implementado
---

# estrategia.rectanguloDragOver

O movimento durante o arrasto: aceita sempre, prende a bola a uma grade e
arrasta o rótulo junto. **316 bytes**.

## Entrada

- **`X`, `Y`** — e a armadilha está aqui: eles chegam **relativos ao
  `rectangulo`**, não ao `campo`. O alvo do arrasto é o retângulo, e é por isso
  que a conversão começa somando a diferença entre as duas origens. Tratá-los
  como se já fossem do campo desloca a bola pela posição da zona — erro que
  cresce com a zona e **desaparece na zona 0**, que é onde um teste apressado
  olharia;
- **`0x00434340`** e **`0x00434344`** — a bola e o rótulo em foco.

**Evidência:** disassembly lido

## Saída

```text
Accept := True                     ' incondicional, na primeira instrucao

gx := rectangulo.Left - campo.Left + X
gy := rectangulo.Top  - campo.Top  + Y

' eixo X: grade de 8 com FASE 5 -- os pontos validos sao 5, 13, 21, ...
resto := gx mod 8
se resto = 5            -> gx
senao se 1 < resto < 5  -> gx += 5 - resto
senao se resto > 5      -> gx -= resto - 5
senao                   -> gx -= resto + 3

' eixo Y: grade de 5 sem fase, empate descendo
resto := gy mod 5
se resto = 0            -> gy
senao se resto > 2      -> gy += 5 - resto
senao                   -> gy -= resto

bola.Left := campo.Left + gx - 7
bola.Top  := campo.Top  + gy - 7
etiqjug.Left := bola.Left - 24
etiqjug.Top  := bola.Top  + 16
```

**A fase 5 do eixo X é o detalhe que se perde.** A grade não é "múltiplo de 8":
é múltiplo de 8 **mais 5**. Arredondar para o múltiplo de 8 mais próximo daria
posições três pixels fora em todo o campo, e nenhum teste de "a bola se move"
pegaria isso.

O original escreve o resto com `and 0x80000007` seguido de correção de sinal,
que é como o C++Builder emite `%` de potência de dois com sinal. O `mod` do
Pascal já segue o sinal do dividendo, igual ao `idiv` — a correção não tem
equivalente escrito no port, e isso é equivalência, não simplificação.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Quatro chamadas, todas `SetLeft`/`SetTop`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `Accept` é escrito antes de qualquer coisa, então arrastar sempre é
aceito — inclusive fora do retângulo, e é o
[`bolaEndDrag`](estrategia.bolaEndDrag.md) que cobre esse caso.

**Evidência:** disassembly lido

## Notas

`gx` e `gy` são **globais** no original (`0x00433e54`, `0x00433e58`), não locais
do handler. Mantidos globais no port: não há leitor conhecido fora daqui, mas
transformar global em local é o tipo de arrumação que esconde um leitor ainda
não lido.
