---
handler: bolaMouseDown
formulario: estrategia
endereco: 0x00408f00
veredito: aberto
---

# estrategia.bolaMouseDown

Começa o arrasto de uma bola no campinho. **456 bytes**, ligado às dez bolas
por `OnMouseDown`.

## Entrada

- **`Button`** — o corpo inteiro está sob `if Button = mbLeft`. O original
  testa `cl` na terceira instrução e sai sem tocar em nada para qualquer outro
  botão;
- **`X`, `Y`** — a posição do clique, em coordenada do formulário;
- **`Sender.Name`**, cortado como no
  [`bolaMouseMove`](estrategia.bolaMouseMove.md), e convertido a inteiro;
- **o vetor bola→zona** por trás de `0x00434230`;
- **a tabela de zonas** em `0x00433e5c` — ver [`../zonas.md`](../zonas.md).

**Evidência:** disassembly lido

## Saída

```text
se Button <> esquerdo entao sai

[0x434340] := Sender
i := StrToInt(SubString(Sender.Name, 5, 2))

' os dois pontos em coordenada de TELA
[0x43434c],[0x434350] := ClientToScreen(X, Y)
[0x434354],[0x434358] := ClientToScreen(bola.Left + 7, bola.Top + 7)

z := [0x434230]^[i]
rectangulo.Left   := campo.Left + zonas[z].x1
rectangulo.Top    := campo.Top  + zonas[z].y1
rectangulo.Width  := zonas[z].x2 - zonas[z].x1 + 1
rectangulo.Height := zonas[z].y2 - zonas[z].y1 + 1

bola.BeginDrag(True, 0)
bola.Enabled := False              ' VMT[0x64], o SetEnabled virtual
[0x434344].Visible := False
rectangulo.Visible := True
```

O `+ 7` é o raio da bola (15 × 14 no `.lfm`), e ele **tem de continuar batendo
com o `- 7`** do [`rectanguloDragOver`](estrategia.rectanguloDragOver.md): é
esse par que faz a bola não pular no instante em que o arrasto começa.

O `+ 1` na largura e na altura é do original — o retângulo é inclusivo nas duas
pontas.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** O inventário de chamadas dos 456 bytes não alcança escritora
nenhuma: são `SubString`, a conversão para inteiro, `ClientToScreen`,
`SetLeft`/`SetTop`/`SetWidth`/`SetHeight`, `BeginDrag`, `SetVisible` e o
`SetEnabled` virtual. A tática só vai ao disco pelo botão de gravar, que é da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

Só o botão. Não confere índice, não confere zona.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Índice fora da faixa indexaria o vetor de zonas fora dele.

**Evidência:** disassembly lido

## Notas

### As duas tabelas que ele lê, e quem as preenche

**A geometria das zonas** (`0x00433e5c`, 11 registros de 16 bytes) não existe
no arquivo: é `.bss`, montada pelo `estrategia.FormCreate`. Está extraída em
[`../zonas.md`](../zonas.md) pelo
[`dump_zonas.py`](../../tools/dump_zonas.py) e portada em
[`../../src/wte_zonas.pas`](../../src/wte_zonas.pas).

**O `0x00434230` não é um vetor: é um ponteiro**, e a CORR-WTE-062 corrigiu
isto em 2026-08-18. Ele aponta para os 11 bytes de zona do registro da
formação escolhida, dentro da tabela de 18 × 44 de `0x00433f0c` — extraída em
[`../formacoes.md`](../formacoes.md). É o que faz a mesma bola ter zona
diferente conforme a formação.

Quem o aponta é o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md), **portado
desde 2026-08-18**, e no port a zona sai de `ZonaDaBola(i)`, que lê a formação
aplicada.

**O que sobra é outra coisa, e o dono é outro.** No original quem aponta os
quatro ponteiros ao **abrir** o formulário é `0x0040a0b4`, a rotina que enche a
tela de tática — chamada pelo `MainForm.mostrar_estrategiaClick`, do grupo de
carga, e não portada. Enquanto ela não existir, o port abre a tela com toda
bola na zona 0 e só acerta depois de um clique na lista. O retângulo aparece,
com a geometria correta de *uma* zona — que é visivelmente diferente de não
aparecer, e por isso a falha não passa por "não implementado".

### O que ele guarda e ninguém lê ainda

`0x00434354`/`0x00434358` — o centro da bola em coordenada de tela — é escrito
aqui e lido pelo `relojTimer`, que não é desta passagem. O port escreve assim
mesmo: deixar de escrever seria a divergência.
