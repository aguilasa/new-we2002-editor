---
handler: FormCreate
formulario: estrategia
endereco: 0x004090fc
veredito: implementado
---

# estrategia.FormCreate

## Entrada

Nada da tela e nada da imagem. Como o `jugador.FormCreate`, os rótulos são
achados **por nome** com `TComponent::FindComponent`, a partir dos prefixos
`etiqestr`, `jugador` e `etiqpos` (literais em `0x00424b66`, `0x00424b6f`,
`0x00424b77`).

**Evidência:** disassembly lido

## Saída

Forma `composto` do [`../arranque.md`](../arranque.md), 1351 bytes — o maior
dos 18. O que está medido:

- `Color := $00E68F41` (`0x00409361`);
- **a tabela de zonas do campinho**, em `0x00409168`…`0x0040930b`: 11 registros
  de 16 bytes escritos como imediatos, `(x1, y1, x2, y2)` em coordenada do
  `campo`. É o retângulo em que cada bola pode ser solta, e o
  [`bolaMouseDown`](estrategia.bolaMouseDown.md) o lê para dimensionar o
  `rectangulo`. Extraída em [`../zonas.md`](../zonas.md);
- quatro cópias de 51 dwords cada (`rep movs`) de `0x00423be4`, `0x00423cb0`,
  `0x00423d7c` e `0x00423e48` para a **pilha** — não para a tabela de zonas.
  Quem as lê não foi medido;
- quatro laços curtos de 11 iterações (`cmp ecx,0xb`) **antes** da zebra, em
  `0x004092fe`…`0x00409344`;
- uma zebra sobre `etiqestr<i>`, `jugador<i>` e `etiqpos<i>` com o mesmo teste
  de paridade do `jugador.FormCreate` (`and eax,0x80000001` em `0x00409378`):
  um ramo pinta os três de `$00D78228`, o outro de `$00E68F41`;
- três campos publicados alcançados no fim — `bola0`, `etiqjug0` e
  `lista_formaciones`, pelo [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

> **Esta lista estava incompleta, e a WTE-TASK-26 a corrigiu.** Escrita na
> WTE-TASK-25, ela descrevia as cores da zebra e chamava os blocos de
> `0x00409168` em diante de "quatro laços curtos" — que é o que se enxerga
> quando se procura pintura. O **produto principal** da rotina é a tabela de
> zonas: sem ela o `bolaMouseDown` desenha um retângulo de tamanho zero, e o
> sintoma não é "o retângulo está errado", é "o retângulo não apareceu".
>
> A lição não é sobre esta rotina. É que spec de `FormCreate` escrita a partir
> da pergunta *"o que ele pinta?"* responde só isso, e a ausência não se anuncia.

## Bytes tocados

**Nenhum.** Os importados chamados são `TControl::SetColor` e
`TComponent::FindComponent`; não há I/O de arquivo no corpo.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma checada.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata, como o `jugador.FormCreate`.

**Evidência:** disassembly lido

## Notas

## O veredito passou a `implementado` em 2026-08-24

**Os quatro laços eram a única pergunta em aberto, e a resposta não era a que se
supunha.** Esta seção dizia: *"11 é o número de jogadores em campo, e o
`estrategia` é a tela do campinho tático — eles muito provavelmente arrumam as
11 bolas e os 11 rótulos de posição. Mas 'provavelmente' não é spec"*. Bem
suspeitado e errado.

Lidos no disassembly pela
[CORR-WTE-093](../../../docs/tasks/CORR-WTE-093.md), os quatro copiam 11 bytes
cada para `esi+0`, `esi+0x0b`, `esi+0x16` e `esi+0x21` — quatro colunas de 11
**intercaladas num registro de 44** —, e o laço de fora fecha a conta:

```text
0x00409355   add esi,0x2c
0x0040935b   cmp DWORD PTR [ebp-0x5c],0x12
0x0040935f   jl  0x4092f8
```

**18 registros de 44 bytes: é a tabela de formações de `0x00433f0c`.** As
quatro cópias de 51 dwords que esta spec já listava *"sem saber quem as lia"*
são as quatro colunas, e o produto delas é exatamente o que o
[`dump_formacoes.py`](../../tools/dump_formacoes.py) já extrai para
[`wte_formacoes.pas`](../../src/wte_formacoes.pas). O port não reproduz os
laços porque teria a mesma tabela montada à mão.

**E o slot virtual do fim foi medido, não suposto.** A rotina termina com
`call DWORD PTR [ecx+0xcc]` e `edx=1` sobre a `lista_formaciones`; lendo o VMT
de `TListBox` no `vcl60.bpl`, o slot `0xcc` guarda
`@Stdctrls@TCustomListBox@SetItemIndex$qqrxi` — é `ItemIndex := 1`, o mesmo
`FORMACAO_DEFAULT` que a `wte_tatica` já declarava por outro caminho.

O corpo está em
[`../../src/impl/ep2002_estrategia.FormCreate.inc`](../../src/impl/ep2002_estrategia.FormCreate.inc)
e faz o que sobra: a cor do formulário, a zebra dos onze trios, os dois
ponteiros de foco, e a cor e o item inicial da lista. Os gates de tática
(`golden-17-tatica` e `golden-21-arrasto`) seguem byte-idênticos depois dele —
o que era de esperar, porque ele não toca a imagem, e o que precisava ser
conferido porque ele mexe no `ItemIndex` que alimenta o ` Accept`.

### O registro de quando o veredito era `aberto`

A leitura completa cabe junto com o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md) e o
`ComboBoxDrawItem`, que são os outros dois handlers de carga deste formulário e
mexem nos mesmos controles — separá-los faria medir a mesma coisa duas vezes.

O que **não** falta: a certeza de que ele não toca a imagem. Isso está medido, e
é o que o gate precisa saber para não confundir esta tela com gravação.
