---
handler: etiqprecioClick
formulario: jugador
endereco: 0x00408bb8
veredito: implementado
---

# jugador.etiqprecioClick

O rótulo `Preco` da ficha. Clicar nele **recalcula** o preço a partir dos
atributos que estão na tela e o escreve no `casilla_precio`. 349 bytes.

É a metade **de tela** da feature de preço; a de byte é o
[`MainForm.base_teamClick`](MainForm.base_teamClick.md), e as duas caem na
mesma fórmula.

## Entrada

- **As dezesseis `barrhab<N>.Position`**, e essa é a parte que a leitura
  apressada erraria. O original não lê o jogador do disco: ele faz
  `FindComponent('barrhab' + N)` para N de 1 a 16 e acumula o campo `+0x20c` de
  cada componente achado, que num `TScrollBar` é a `Position`. Quem põe valor
  lá é a rotina de encher a ficha (`0x0040756c`), como
  `max(atributo − 12, 0)`.
- **`flechasapa1.Position`** (campo `+0x41c`, pelo
  [`../campos.tsv`](../campos.tsv)) — a seta de **posição**. Vale 0 para
  goleiro.

**Consequência medida:** mexer numa barrinha e clicar no rótulo dá o preço do
valor **mexido**, mesmo sem gravar nada.

**Evidência:** disassembly lido

## Saída

```text
s := soma das dezesseis barrhab<N>.Position
preço := s⁴ div 3000000 + s³ div 40000 + s² div 700 + s div 7 + 5
se flechasapa1.Position = 0:  preço := preço * 5 div 3
casilla_precio.Text := preço * 10000
```

A fórmula está em `0x00408c3b`..`0x00408c83`, o `× 5 div 3` em `0x00408c95`, e
o fator de exibição — `imul` de 64 bits por `0x2710` — em `0x00408cb3`.

**O byte que a imagem guarda é o preço SEM o fator.** Quem multiplica por
10.000 é só a exibição; confundir os dois poria 210000 num byte.

Detalhe da fórmula, das três armadilhas dela e da tabela de verdade em
[`../preco.md`](../preco.md).

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Ele lê a tela e escreve na tela. Quem grava preço é o
`MainForm.base_teamClick`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma no corpo. Ficha aberta é pré-condição do formulário, não deste handler.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Componente que `FindComponent` não achasse seria ignorado — no port,
o `if c is TScrollBar` faz o mesmo.

**Evidência:** disassembly lido

## Notas

**A régua deste handler é indireta, e é forte assim.** Ele não grava, então não
há gate de byte para ele; o que existe é melhor: a **mesma fórmula** está no
`base_teamClick`, que grava, e o
[`golden-22-precos`](../../tests/roteiros/golden-22-precos.txt) a mede
byte a byte em 22 jogadores — mais a tabela de verdade de 132 jogadores do
[`check_preco.py`](../../tools/check_preco.py), 100% de acerto.

O que sobra sem medida direta é a **soma vinda da tela**: se as `Position`
estivessem erradas, este handler daria outro número e o do time não. Mas as
`Position` são o que a `PreencheFicha` escreve, e elas já são conferidas contra
o original pelo [`check_bitfields.py`](../../tools/check_bitfields.py), que
compara a ordem das dezesseis com a `TPlayer.Decode`.
