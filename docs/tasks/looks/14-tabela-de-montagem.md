---
id: LOOKS-TASK-14
title: "`assembly.py` — campo de LOOKS → peça + paleta"
type: engenharia-reversa
category: núcleo
phase: 4
depends_on: ["LOOKS-TASK-12", "LOOKS-TASK-13"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-14: A tabela de montagem

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (c).
- **É o coração do projeto e a fase mais cara.** O que liga `HAIR = B3` à peça
  e à paleta certas.
- **Não pode vir antes da Fase 2.** Tabela de índice escrita contra peça não
  identificada produz mapeamento plausível e errado — é a armadilha das oito
  listas de nome de time do PES2 (§6.1 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md)), onde casar por índice gravava no
  time errado e a tela parecia certa.

---

- **Quatro linhas da tabela já estão medidas, e com o mecanismo junto.**
  Das tasks [`08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) e
  [`09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md), por
  `python tools/looks/oracle.py --fields`:

  | campo | peça | o que ele muda na primitiva |
  |---|---|---|
  | `SKIN` | tronco (pescoço), antebraço, coxa, perna | o **CLUT**, `+0x40` por passo |
  | `HAIR` | cabeça (`MODEL.BIN` seção 24) | o **`v`** das quatro quinas, `+0x20` |
  | `H.COL` | cabeça | o **CLUT** |
  | `BOOTS` | pé | o **CLUT** |

  O padrão é o que importa para esta task: **a peça nunca é trocada — o que
  muda é a paleta ou a faixa do atlas.** Uma tabela de montagem que mapeie
  campo → *peça diferente* estaria descrevendo um jogo que não é este.

  **Isso vale dentro de um boneco, e a escolha do boneco vem antes.** Os dois
  não compartilham as peças de braço: medido em 2026-09-15
  ([`CORR-LOOKS-021`](/docs/tasks/looks/CORR-LOOKS-021.md)), braço e antebraço
  têm **malha diferente** entre as duas listas — 30/24 contra 40/34 e 80/78
  contra 88/86 — e só a perna e o pé são de fato a mesma malha. Quem monta
  escolhe **a lista primeiro** (A é o jogador de linha, B é o goleiro) e só
  depois aplica campo; carregar uma malha e trocar só paleta desenha o goleiro
  de manga curta.
- **E as peças têm nome medido**, com o mapa em `tools/looks/pieces.py`: tronco,
  braço, antebraço, coxa, perna, pé (espelhados em `z`) e a cabeça, que mora no
  outro arquivo.

---

- **A metade "paleta" da tabela já tem leitor e regra**, desde 2026-09-15
  ([`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md)): o
  `tools/looks/texture.py` acha as 267 paletas do `DAT2D.BIN` e resolve um CLUT
  id pelo registro que o **cobre**, não pelo que lhe é igual. A distinção é da
  tabela de montagem: as chuteiras são (0, 484), a pele nua (0, 480), e a cabeça
  (16, 480) e (144, 480) — as três últimas **dentro da mesma paleta larga**, de
  modo que "campo → paleta" não é um par de offsets e sim `(x, y, largura)`.
- **E o campo que move a peça move a linha de VRAM inteira:** um passo de `SKIN`
  soma `0x40` ao id, que é uma linha, e leva pele, cabeça e tudo que amostra
  daquela paleta junto. Uma linha de tabela que mande `SKIN` trocar só a pele
  estaria descrevendo outro jogo.

---

- **Mais duas linhas da tabela medidas, e agora com a imagem junto.** Em
  2026-09-15 ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)):

  | campo | peça | primitivas | o que muda | imagem |
  |---|---|---|---|---|
  | `HAIR` | cabeça | 1 e 14 | `v` `+0x20` | `DAT2D.BIN` **3.568** |
  | `FACE` | cabeça | 8 e 13 | `v` `+0x10` | `DAT2D.BIN` **3.568** |

- **Uma linha da tabela precisa de três coisas, não duas:** peça, paleta **e
  imagem** — e a imagem não se deduz da página, porque uma página de 4 bits
  cobre 256 texels e as imagens deste arquivo têm 128. `u` acima de 127 amostra
  a imagem seguinte, e foi exatamente isso que decidiu a §1.8. O
  `tools/looks/atlas.py` resolve `(página, u, v)` para o registro certo; usá-lo
  é mais barato do que repetir a conta.
- **O uniforme não está no arquivo comum.** As 1.039 primitivas de kit amostram
  páginas e paletas que moram em **105 `TEX_*.BIN`**, um por time. Uma tabela de
  montagem que procure o uniforme no `DAT2D.BIN` não acha nada e não diz por
  quê.
- **E é aqui que a escolha da paleta do uniforme fica ambígua.** Cada
  `TEX_*.BIN` tem **cinco** paletas de 256 — duas em (0, 486), duas em (0, 488)
  e uma em (256, 480) que a geometria não nomeia. **"Casa e fora" é hipótese**,
  não medição: ninguém trocou o uniforme do time na tela para ver qual das duas
  de uma id se move ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)).
  O uniforme é o único campo com **duas candidatas por id**, e é desta task
  decidir por medição — escolher "a primeira" desenha perfeitamente, nas cores
  erradas.

---

- **Paleta larga não é uma linha da tabela: é dezesseis.** Medido em
  2026-09-15 pela
  [`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md): um registro
  de 256 entradas é uma fileira de **dezesseis CLUTs de 4 bits**, e os três
  campos de cor são **duas coordenadas** dessa grade — `SKIN` anda a linha
  (a raça, quatro), `H.COL` e `H.F.COL.` andam a coluna (oito cabelos a partir
  da 1, sete barbas a partir da 9). Os três **alcançam** as dezesseis colunas:
  1 + 8 + 7 = 16.

  **E alcance não é identidade — é aqui que esta task erra em silêncio.** A
  coluna 1 não é "cabelo 0": é onde repousam **948 primitivas de 50 seções do
  `MODEL.BIN`**, das quais só **16** são a cabeça, e as colunas 2..8 e 10..15
  não têm primitiva nenhuma no disco
  ([`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)). Escrever
  `coluna 1 → cor de cabelo 0` na tabela dá a 932 primitivas uma cor de cabelo
  que elas não têm, e o boneco **desenha perfeitamente**. Quem preenche uma
  linha desta tabela a partir de campo de tela tem de dizer **a peça também**,
  nunca só a coordenada.

  | campo | peça | primitivas | coordenada | alcance |
  |---|---|---|---|---|
  | `SKIN` | toda pele nua, mais a cabeça | 196 e 326 bytes, por slot | linha | 4 |
  | `H.COL` | cabeça | 0, 1, 4, 9, 14, 16, 17 | coluna | 8 (1..8) |
  | `H.F.COL.` | cabeça | 8 e 13 | coluna | 7 (9..15) |

- **`H.COL` move sete primitivas, não as duas do cabelo.** As duas que o `HAIR`
  reformata estão entre elas; as outras cinco são partes da cabeça pintadas com
  a cor do cabelo. Uma linha de montagem que ligue `H.COL` só ao cabelo deixa
  cinco primitivas com a cor errada.
- **O desempate "registro mais estreito ganha" é o que o console faz**, e agora
  está medido contra a VRAM: as 21 linhas de CLUT do `DAT2D.BIN` batem entrada
  por entrada quando resolvidas pelo `texture.covering`, e a linha 484 — onde
  seis paletas de 16 entradas ficam por cima de uma de 256 — dá **71** entradas
  diferentes se resolvida pelo registro largo. A tabela de montagem pode usar o
  `covering` sem ressalva.

---

## Objetivo

`tools/looks/assembly.py`: dada uma tupla de LOOKS, dizer quais peças desenhar
e com que paleta.

---

## Critério de conclusão

- [ ] Os **32 cabelos** resolvidos: onde mora a malha (ou a textura) de cada
      índice, e como se chega nela a partir do valor do campo.
- [ ] As **4 peles** resolvidas, pelo mecanismo que a LOOKS-TASK-12 decidiu.
- [ ] `FACE`, `H.F.COL.`, `BOOTS` e `BODY` resolvidos, ou **declarados não
      resolvidos com a razão** — melhor um buraco nomeado do que um
      mapeamento inventado.
- [ ] A tabela é **derivada de medição**, e cada linha diz de onde veio.
- [ ] Controle negativo: deslocar a tabela em um índice fica vermelho.
- [ ] Cross-check contra o corpus: ao menos três das 50 tuplas do Superpack
      produzem a mesma escolha de peças que o JPG mostra.

---

## Log de Execução

*(preencher ao executar)*
