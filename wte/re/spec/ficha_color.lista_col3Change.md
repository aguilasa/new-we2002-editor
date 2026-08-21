---
handler: lista_col3Change
formulario: ficha_color
endereco: 0x0040690c
veredito: implementado
---

# ficha_color.lista_col3Change

O combo de **padrão de camisa** — `NORMAL`, `ROMBOIDAL`, `EXTRA`. Três casos e
dois bytes por caso, todos literais: não há aritmética nenhuma no corpo.

**Evidência:** disassembly lido

## Entrada

`lista_col3.ItemIndex` (`[this+0x394]`).

**Evidência:** disassembly lido

## Saída

```text
se ItemIndex = 0:        byte[0x004331d8] := 0x00 ; byte[0x004331d9] := 0x65
senao se ItemIndex = 1:  byte[0x004331d8] := 0x28 ; byte[0x004331d9] := 0x61
senao:                   byte[0x004331d8] := 0x00 ; byte[0x004331d9] := 0x64
```

O terceiro caso é o `else` do original, e não um teste de `= 2`: um quarto item
cairia em `EXTRA`.

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem — **e essa foi a segunda leitura, não a primeira.**

`0x004331d8` e `0x004331d9` têm exatamente três referências cada no `.text`, e
todas as seis estão dentro deste handler. A conclusão fácil é "escrita morta", e
ela está errada: o par é indexado em outro lugar, com passo dois —
`mov dl,[eax*2+0x004331d6]` em `0x004050a4`. Ou seja `0x004331d6`/`d7` é o
**slot 0** e `0x004331d8`/`d9` é o **slot 1**, o mesmo par de slots que o resto
do estado visual usa. O slot 0 é lido da imagem em `0x0040517a` e devolvido a
ela em `0x00405255`, dentro da gravação do `BitBtn3`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata; qualquer índice fora de 0 e 1 é `EXTRA`.

**Evidência:** disassembly lido

## Notas

### O par não tem campo na camada de dados

Nem `TTeam` nem `TMlTeam` guardam padrão de camisa, e o `we2002_core` é o
oráculo de formato deste projeto. É a mesma constatação que fez o
[`MainForm.colorearClick`](MainForm.colorearClick.md) deixar este combo no
default do formulário em vez de escolher item — e a divergência de tela
registrada lá continua valendo.

O que mudou é que a **escrita** passou a existir: o port guarda os dois bytes em
`wte_cor.PadraoDaCamisa`, o slot 1. **Nada os lê ainda** — o único consumidor no
original é a gravação do `BitBtn3`, que não foi portada. Guardá-los agora é o
que faz o `BitBtn3` ser possível sem reabrir este handler.

### O combo é `Enabled = False`

Só código o move, e o único código que o moveria é o `colorearClick` — que não
o move, pelo motivo acima. Na prática este handler não dispara hoje em nenhum
dos dois lados.
