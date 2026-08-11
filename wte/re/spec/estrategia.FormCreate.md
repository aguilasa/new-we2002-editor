---
handler: FormCreate
formulario: estrategia
endereco: 0x004090fc
veredito: aberto
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
- quatro laços curtos de 11 iterações (`cmp ecx,0xb`) **antes** da zebra, em
  `0x004092fe`…`0x00409344`;
- uma zebra sobre `etiqestr<i>`, `jugador<i>` e `etiqpos<i>` com o mesmo teste
  de paridade do `jugador.FormCreate` (`and eax,0x80000001` em `0x00409378`):
  um ramo pinta os três de `$00D78228`, o outro de `$00E68F41`;
- três campos publicados alcançados no fim — `bola0`, `etiqjug0` e
  `lista_formaciones`, pelo [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

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

**Veredito `aberto` de propósito, e o que falta é o Pascal.** Os quatro laços
de 11 iterações que vêm antes da zebra ainda não têm leitura escrita: 11 é o
número de jogadores em campo, e o `estrategia` é a tela do campinho tático —
eles muito provavelmente arrumam as 11 bolas e os 11 rótulos de posição. Mas
"provavelmente" não é spec, e escrever o corpo a partir daí seria inventar.

A leitura completa cabe junto com o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md) e o
`ComboBoxDrawItem`, que são os outros dois handlers de carga deste formulário e
mexem nos mesmos controles — separá-los faria medir a mesma coisa duas vezes.

O que **não** falta: a certeza de que ele não toca a imagem. Isso está medido, e
é o que o gate precisa saber para não confundir esta tela com gravação.
