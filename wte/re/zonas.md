# `re/zonas.md` — onde cada bola do campinho pode ser solta

Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md).
Gerado por [`../tools/dump_zonas.py`](../tools/dump_zonas.py) a partir
de `we-team-editor/we-team-editor.exe`. **Não editar à mão.** A tabela está em
[`zonas.tsv`](zonas.tsv); a unidade Pascal é
[`../src/wte_zonas.pas`](../src/wte_zonas.pas).

## O que é

Arrastar um jogador no campinho do formulário `estrategia` **não é**
livre. O `bolaMouseDown` desenha o `rectangulo` em volta da área
permitida daquela bola, e o `rectanguloDragOver` prende o movimento a
uma grade dentro dela.

A tabela vive em `0x00433e5c`: 11 registros de 16 bytes,
`(x1, y1, x2, y2)` em coordenadas do `campo`. **No arquivo ela não
existe** — é `.bss`, montada em tempo de execução pelo
`estrategia.FormCreate` (`0x004090fc`), que escreve os
44 imediatos um a um.

> **A spec do `estrategia.FormCreate` não dizia isso.** Escrita na
> WTE-TASK-25, ela descreve as cores da zebra e chama estes quatro
> blocos de "quatro laços curtos de 11 iterações" — que é o que se vê
> quando se procura pintura. O produto principal da rotina é esta
> tabela, e a WTE-TASK-26 corrigiu a spec ao lê-la de novo.

## A tabela

O `campo` tem 395×246 (do `.lfm`), e o gerador **aborta** se
algum retângulo sair dele — as duas medidas vêm de fontes diferentes,
uma do código e outra do formulário.

| Zona | x1 | y1 | x2 | y2 | largura | altura |
|--:|--:|--:|--:|--:|--:|--:|
| 0 | 10 | 63 | 129 | 182 | 120 | 120 |
| 1 | 10 | 63 | 129 | 182 | 120 | 120 |
| 2 | 10 | 3 | 129 | 82 | 120 | 80 |
| 3 | 10 | 163 | 129 | 242 | 120 | 80 |
| 4 | 122 | 63 | 233 | 182 | 112 | 120 |
| 5 | 122 | 3 | 281 | 82 | 160 | 80 |
| 6 | 122 | 163 | 281 | 242 | 160 | 80 |
| 7 | 170 | 63 | 281 | 182 | 112 | 120 |
| 8 | 274 | 63 | 385 | 182 | 112 | 120 |
| 9 | 274 | 3 | 385 | 82 | 112 | 80 |
| 10 | 274 | 163 | 385 | 242 | 112 | 80 |

São 11 registros para 10 retângulos distintos: há
repetição, e ela é esperada — o índice não é o número da bola, é a
**zona** que a formação escolhida atribuiu àquela bola. Quem preenche o
vetor bola→zona é o `estrategia.lista_formacionesClick`.

A largura desenhada é `x2 - x1 + 1`, não `x2 - x1`. O `+ 1` é do
original e está reproduzido.
