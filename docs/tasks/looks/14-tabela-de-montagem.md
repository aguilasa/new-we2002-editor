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
- **E as peças têm nome medido**, com o mapa em `tools/looks/pieces.py`: tronco,
  braço, antebraço, coxa, perna, pé (espelhados em `z`) e a cabeça, que mora no
  outro arquivo.

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
