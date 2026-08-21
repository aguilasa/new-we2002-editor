---
handler: barraChange
formulario: ficha_color
endereco: 0x00405e40
veredito: implementado
---

# ficha_color.barraChange

Um corpo para as três barras `barra_rojo`, `barra_verde` e `barra_azul`. **É o
handler que de fato muda a cor**: os outros da família ou movem seleção, ou
aplicam uma transformação sobre o que este escreveu.

**Evidência:** disassembly lido

## Entrada

- `barra_rojo.Position`, `barra_verde.Position`, `barra_azul.Position`
  (`[this+0x348]`, `+0x34c`, `+0x350`, campo `FPosition` em `+0x20c`) — os três
  em **cinco bits**, com `Max = 31` no `.dfm`;
- `0x00433dc0` (`entrada`), qual das 16 amostras está selecionada, base zero;
- `boton0.Checked` e `boton1.Checked` (`[this+0x388]` e `+0x384`), que decidem
  o que redesenhar.

**Evidência:** disassembly lido

## Saída

```text
color<entrada+1>.Color := (R shl 3 and 0xFF)
                       or ((G shl 3 and 0xFF) shl 8)
                       or ((B shl 3 and 0xFF) shl 16)

0x00433dd4[entrada] := R + (G shl 5) + (B shl 10)

se boton0.Checked:                      ' familia bandeira
    byte[0x00432ef4 + entrada*2]     := lo(palavra)
    byte[0x00432ef5 + entrada*2]     := hi(palavra)
    0x00405270()                        ' redesenha a bandeira

se boton1.Checked:                      ' familia uniforme
    base := 0x00432f56 + lista_col1.ItemIndex * 32
    byte[base   + entrada*2]         := lo(palavra)
    byte[base+1 + entrada*2]         := hi(palavra)
    0x004056c8([0x004335cc], lista_col1.ItemIndex)
```

Os dois `if` são **independentes** — não há `else`. Com `boton2` ou `boton3`
marcados nenhum dos dois corre, e a paleta em vigor não muda: só a amostra e o
vetor de edição.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD.** O destino é a paleta em vigor na memória — o
*slot 1* do original. Quem grava é o `BitBtn3`, e ele grava o slot 0 depois de
copiar o 1 sobre ele.

**Evidência:** disassembly lido

## Pré-condições

`entrada` entre 0 e 15. O `FormCreate` a zera e só o `colorMouseDown` a move,
sempre para o sufixo de um `color<n>` existente.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. O `FindComponent` do `color<entrada+1>` pode devolver nulo em
teoria; na prática `entrada` sempre veio de um nome que existe.

**Evidência:** disassembly lido

## Notas

### Ele grava **uma** entrada, e não as dezesseis

A rotina de apoio `0x00405b48` reescreve as 16 palavras de uma vez e é chamada
de quatorze lugares — mas **não daqui**. Este handler escreve os dois bytes da
entrada corrente direto no destino. O resultado é o mesmo (as outras quinze não
mudaram); o que muda é o custo, e arrastar uma barra dispara este handler a cada
pixel.

### O `and 0xFF` da cor da amostra é do original, e nunca corta

`Max = 31` no `.dfm`, então `v shl 3` cabe em oito bits sempre. O `and` está
aqui porque está lá — a alternativa seria decidir que ele é morto, e ele só é
morto enquanto o `.dfm` disser 31.

### A realimentação que **não** acontece

`PintaUmaAmostra` (`0x00405bc8`) escreve `Position` nas três barras quando pinta
a amostra selecionada, e escrever `Position` dispara `OnChange` nos dois
widgetsets — ou seja, este handler roda três vezes a cada repintura da amostra
selecionada. As duas primeiras vêem um canal novo com os outros dois velhos e
gravam cor intermediária; a terceira fecha certo. **Nenhum chamador depende
disso**, e é por isso que a diferença de widgetset aqui não vira divergência de
tela: o estado final é o mesmo com ou sem o disparo.
