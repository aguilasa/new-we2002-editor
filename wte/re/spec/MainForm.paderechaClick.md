---
handler: paderechaClick
formulario: MainForm
endereco: 0x0040e5e8
veredito: implementado
---

# MainForm.paderechaClick

A seta `>` entre os dois painéis: move **um** jogador do time da esquerda para
o da direita. **312 bytes.**

É o representante da família de quatro — `paderecha`, `paizquierda`,
`paderecha2`, `paizquierda2` são cópias literais que trocam quais combos entram
e qual buffer é qual. As quatro specs dizem a mesma coisa; esta é a que traz a
medição inteira.

## Entrada

- `lista_equipos_1.ItemIndex`, `lista_jugadores_1.ItemIndex` — a origem (campos
  `+0x390` e `+0x388`, pelo [`campos.tsv`](../campos.tsv)).
- `lista_equipos_2.ItemIndex`, `lista_jugadores_2.ItemIndex` — o destino
  (`+0x384` e `+0x38c`).
- O arquivo aberto, na global `0x00432e58` — passado como argumento de pilha às
  duas rotinas de jogador.
- `WORD[0x004335c0]` — o contador de blocos livres de Master League.

**Evidência:** disassembly lido

## Saída

```text
guarda := lista_jugadores_2.ItemIndex          ' o DESTINO, antes de repovoar

0x004046e8(lista_equipos_1.ItemIndex,
           lista_jugadores_1.ItemIndex, buffer := 1, arquivo)
codigo := 0x00404820(buffer := 1,
                     lista_equipos_2.ItemIndex,
                     lista_jugadores_2.ItemIndex, arquivo)

se codigo >= 0:
    0x0040b2d8(lista_equipos_2, lista_jugadores_2)   ' repovoa o destino
    lista_jugadores_2.Update                          ' VMT +0x88
    lista_jugadores_2.ItemIndex := guarda             ' VMT +0xcc
    0x004046e8(lista_equipos_2.ItemIndex,
               lista_jugadores_2.ItemIndex, buffer := 2, arquivo)

casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
0x00403e20(codigo)                                    ' a mensagem, se houver
```

**Os três slots de VMT não são inferência.** Saíram do `vcl60.bpl` pelo método
do [`sonda_dorsal.py`](../../tools/sonda_dorsal.py) — achar o VMT da classe pelo
nome em `[vmt - 0x2c]` e ler o slot: `TComboBox +0xc8` é
`TCustomCombo::GetItemIndex`, `+0xcc` é `SetItemIndex` e `+0x88` é
`TWinControl::Update`.

**Evidência:** disassembly lido

## Bytes tocados

**Grava**, e a gravação não está neste corpo: está dentro da `0x00404820`, que
escreve 10 bytes de nome, 12 de atributos e o byte condicional no destino, mais
o número de camisa quando o slot é o 48. Que offset exatamente, por ramo, é o
que a [WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md) precisa
medir — é lá que existe gate por byte.

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se há time selecionado nos dois lados, não confere se
há jogador selecionado, não confere se a imagem está aberta. O que segura o
handler é a tela: as duas setas nascem desabilitadas e a carga de time as
habilita.

O port **acrescenta** o teste de `ItemIndex >= 0` nos quatro combos, divergência
de robustez registrada nas Notas.

**Evidência:** disassembly lido

## Comportamento de erro

Duas recusas, as duas vindas do código de retorno da `0x00404820` e traduzidas
em mensagem pela `0x00403e20`:

| código | mensagem, literal do binário |
|---|---|
| `-2` | `It's the same player in both teams...` (`0x00424767`) |
| `-1` | `You need at least 1 memory block free to do that` (`0x0042478d`) |
| `0`, `1`, `2` | nenhuma |

`0x00403e20` soma 2 ao código e indexa uma tabela de salto de cinco entradas em
`0x00403e46`; a comparação é **sem sinal**, então qualquer código fora de
`-2..2` cai na saída em vez de indexar fora da tabela. A mensagem vai para o
`etiq1` do `ficha_error` (campo `+0x2f8`, pelo [`campos.tsv`](../campos.tsv)) e
o formulário sobe como modal.

O `-2` é a comparação de identidade descrita abaixo. O `-1` sai do ramo em que
o destino é um slot de clube de ML que ainda não tem bloco próprio e
`WORD[0x004335c0]` vale zero — é a
[WTE-TASK-33](../../../docs/tasks/concluidos/33-slots-de-master-league.md) aparecendo por
dentro deste lote.

**Evidência:** disassembly lido

## Notas

### O buffer de 44 bytes, e por que o índice não quer dizer origem

`0x004335ec` guarda registros de 44 bytes. O argumento `1`/`2` que este corpo
passa **não é modo de operação** — a sexta passagem da
[WTE-TASK-26](../../../docs/tasks/concluidos/26-handlers-de-edicao.md) leu assim e estava
errado. É índice de buffer, e o buffer acompanha o **lado da tela**: 1 é o
esquerdo, 2 é o direito, 0 é o destino que a rotina de gravação prepara para si.
As duas chamadas a `0x004046e8` são **leituras**: a primeira carrega a origem,
a segunda recarrega o lado que acabou de mudar.

O layout foi confirmado por duas leituras independentes — a leitora
`0x004046e8` e a escritora `0x00404820` —, e os oito deslocamentos batem:

| campo | do lado da leitura | do lado da escrita |
|---|---|---|
| nome, 10 B | `0x004335ec + 44*i` | `+0x00` |
| atributos, 12 B | `0x004335f6 + 44*i` | `+0x0a` |
| identidade, 2 B | — | `+0x16`, `+0x17` |
| condicional, 1 B | `0x00433604 + 44*i` | `+0x18` |
| tipo | — | `+0x19` |
| offset do nome | `0x00433608 + 44*i` | `+0x1c` |
| offset dos atributos | `0x0043360c + 44*i` | `+0x20` |
| offset do condicional | `0x00433614 + 44*i` | `+0x28` |

### A identidade é um par de bytes, e o que ele significa depende do time

`0x00404374` (881 bytes) preenche identidade, tipo e as três colunas de offset.
Para seleção (índice `< 63`) a identidade é literalmente `(time, slot)`. Para
clube de Master League ela é o **par de vínculo** que a imagem guarda, lido do
arquivo byte a byte — o mesmo par que o `ResolveMlLink` do `we2002_core`
consome, e o segundo byte `>= 23` é o mesmo `slot > 22` de lá, separando
vínculo de bloco próprio.

Daí sai a regra do `-2`: dois clubes de ML que apontem para o mesmo jogador de
seleção têm a **mesma identidade**, e mover um para o outro é recusado. Há uma
válvula, e é do original: `BYTE[0x00423168]` desliga a checagem. Ela nasce zero
e o `.text` inteiro tem **uma** escrita nela — `mov BYTE ds:0x423168,1` em
`0x0040fd7a`, dentro do corpo do `mostrar_jugadorClick`
(`0x0040f8d4`..`0x00410220`).

### O campo condicional: a regra fecha nos dois oráculos e o endereço não

`0x00404374` zera a coluna `+0x28` — "este jogador não tem o campo na imagem" —
quando o índice do time cai entre `0x35` e `0x38` exclusive, isto é, **54 ou
55**. Quando ela é zero, `0x004046e8` escreve o literal **50** no lugar de ler.

O `we2002_database.pas` gerado pula, ao carregar `cost`, exatamente os
jogadores 1704..1749 — que é `462 + 54*23` até `462 + 56*23 - 1`, os mesmos
dois times. **Dois oráculos independentes concordam sobre quais jogadores não
têm o campo.**

E discordam sobre **onde ele está**. O `wte.exe` calcula
`0x2ece0c + 23*time + slot + 2*(time div 56)`; o `we2002_core` lê a partir de
`OFS_COST_NATIONAL = 3067404 = 0x2ecc0c`, com o furo depois do time 53 e não
depois do 55. Medido na cópia da ROM europeia, os 64 bytes em `0x2ecc0c` e em
`0x2ece0c` são **diferentes**. Um dos dois está errado sobre o formato, e o
`we2002_core` é o que já é byte-idêntico ao `ed.exe`.

Isso é pergunta da [WTE-TASK-32](../../../docs/tasks/concluidos/32-preco-do-jogador.md), e
está anotado como pergunta. Nesta task nada lê o valor: o port enche o campo a
partir do `cost` do modelo — mesmo papel, mesma largura, mesma ausência — e
quem levar isso à imagem tem de responder antes.

### Veredito `implementado`

O Pascal está escrito
([`../../src/impl/ep2002_mainform.paderechaClick.inc`](../../src/impl/ep2002_mainform.paderechaClick.inc))
e a gravação fechou em duas metades. A primeira, **destino de seleção**, em
2026-08-19, com golden verde
([`golden-09-mover`](../../tests/roteiros/golden-09-mover.txt)). A segunda,
**destino de Master League**, em 2026-08-20.

Fechado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md): o ramo de
**destino de Master League** da `0x00404820` foi portado, com golden verde
([`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt)) e o
contador de blocos livres vindo da
[WTE-TASK-33](../../../docs/tasks/concluidos/33-slots-de-master-league.md). Com ele a
recusa `-1` passou a ser alcançável e o `casilla_xmlibres` mostra o número de
verdade.

### O destino de Master League grava outra coisa, e é isso que o separa

No destino de seleção o slot guarda um jogador, e a gravação põe 10 bytes de
nome, 12 de atributos e o condicional em cima dele. No destino de Master League
o slot guarda um **par de vínculo de dois bytes**, e o que se move é para onde
ele aponta. Daí as três saídas onde a outra metade tem uma:

| situação | o que faz | código |
|---|---|---|
| origem vazia, destino divide o bloco com outro | aloca bloco livre, grava o jogador nele, aponta o vínculo | `0` |
| os dois lados com identidade | só reescreve o vínculo | `1` |
| destino é dono único do bloco, origem vazia | grava o jogador direto no bloco, sem alocar | `1` |
| destino é dono único, origem com identidade | reescreve o vínculo e **libera** o bloco | `2` |

A última é o único lugar do programa que **devolve** bloco, e é o caminho que
o `golden-10-mover-ml` exercita: medido, o oráculo escreve exatamente 2 bytes,
em `2012734..2012735`.

**Divergências deliberadas do port**
([WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md)):

1. sai sem fazer nada se qualquer um dos quatro `ItemIndex` for negativo;
2. no caminho de `0x00404d73` o original decrementa
   `ocupacao[bloco_do_destino]` sem ter calculado o índice quando o destino é
   do tipo 3, e escreve onde calhar. Não é alcançável — o `0x00404374` só põe
   tipo 3 nos buffers de descarte e o destino é sempre o buffer 0 —, e o port
   guarda contra isso de vez.
