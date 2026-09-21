---
id: LOOKS-TASK-38
title: "O alinhamento dos valores — a caixa do objeto de texto no `screen.json`, e o valor à direita"
type: implementação
category: ui
phase: 10
depends_on: ["LOOKS-TASK-37"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
---

# LOOKS-TASK-38: O alinhamento dos valores

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o).
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário.
- **Medido na terceira passada da 31, e não aplicado:** o objeto de texto dos
  valores que o `SCREEN_PRINT` recebe é uma caixa de largura 296 a partir de
  x 176 — borda direita em 472 —, e os valores terminam contra ela (`23`
  começa em 448, `TYPE` em 425, `Unknown` em 392). A janela os escreve a
  partir da esquerda da caixa do cursor.
- **O `screen.json` é gerado**, pelo `oracle.py --screen --write` (~12 min), e
  não se edita à mão: a caixa do objeto entra pelo gerador, e o `--screen`
  remede.
- **Depois da 37**, porque a largura de cada glifo decide onde um valor
  alinhado à direita começa; com a fonte do Qt o alinhamento sairia certo na
  borda e errado em todo o resto.

---

## Objetivo

Cada texto da janela fica onde o jogo o põe dentro da caixa do objeto — os
valores encostados na borda direita.

---

## Critério de conclusão

- [ ] O gerador grava a caixa (x, largura) e o modo de alinhamento de cada
      objeto de texto; `screen.py --check` confere, e `--screen` remede com
      0 diferença.
- [ ] A janela alinha por essa caixa; o ponto inicial de cada valor bate com
      o do sprite do jogo, nos dois slots, ao longo de `oracle.py --keys`.
- [ ] Um controle plantado (o alinhamento pela esquerda) fica vermelho.

---

## Log de Execução

*(preencher ao executar)*
