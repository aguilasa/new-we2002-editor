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

## As duas malhas de marcador — `malla1MouseDown` e `malla2MouseDown`

*(WTE-TASK-29)* O mesmo formulário tem duas grades. Clicar numa delas
**escolhe a coluna pelo X e move o marcador daquela coluna para a
linha do Y** — o `Left` de cada marcador é fixo, quem anda é o `Top`.

O passo é `24` px na horizontal e `16` na
vertical, e a folga do marcador é `3` px. **Os três são
os mesmos nas duas malhas**, e este gerador aborta se deixarem de ser.

| handler | endereço | malha | prefixo | colunas | linhas |
|---|---|---|---|---:|---:|
| `malla1MouseDown` | `0x00409f4c` | `malla1` | `simboloN` | 4 | 11 |
| `malla2MouseDown` | `0x0040a000` | `malla2` | `tiradorN` | 6 | 11 |

### As quatro contas que o `.lfm` confere

Os três números saem do `.text`; as coordenadas dos marcadores saem do
formulário. As duas fontes são independentes — uma é o código de 2002,
a outra é o formulário de 2002 — e têm de concordar em quatro pontos:

**`malla1`** — 96×176 px em (144, 312):

1. `96 div 24` = **4**, e o `.lfm` declara 4 `simboloN`;
2. `simbolo1.Left` = 147 = `144 + 3`;
3. `simbolo1.Top` = 315 = `312 + 3`;
4. os marcadores andam 24 px em `Left`, que é o passo lido do `.text`.

**`malla2`** — 144×176 px em (368, 312):

1. `144 div 24` = **6**, e o `.lfm` declara 6 `tiradorN`;
2. `tirador1.Left` = 371 = `368 + 3`;
3. `tirador1.Top` = 315 = `312 + 3`;
4. os marcadores andam 24 px em `Left`, que é o passo lido do `.text`.

Uma folga lida errada quebra as duas do meio; um passo errado quebra a
primeira e a quarta.

### O que eles **não** fazem

Nenhum dos dois toca a imagem de CD, e nenhum dos dois lê dado. São 180 e 180 bytes de geometria:
dividir, achar o marcador pelo nome, escrever `Top`.
Quem lê a posição de volta é o `estrategia.BitBtn3Click`
(`0x0040a660`), que é da
[WTE-TASK-30](../../docs/tasks/30-handlers-auxiliares.md); quem a
escreve a partir do dado é a rotina interna `0x0040a0b4`, portada
como `PreencheTelaDeTatica` na `wte_tatica.pas` (CORR-WTE-082).
**O caminho fechou nos dois sentidos** desde a CORR-WTE-081: a ida é
o `PreencheTelaDeTatica` e a volta é o ` Accept`, que grava 45 bytes
por time e tem gate byte a byte no `golden-17-tatica`.

E só o botão esquerdo faz alguma coisa: o original testa `cl` na
entrada e sai sem fazer nada — sem limpar estado — para qualquer outro,
como o `bolaMouseDown` faz.
