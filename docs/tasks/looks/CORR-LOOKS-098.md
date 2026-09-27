---
id: CORR-LOOKS-098
title: "Reconciliar a lista de abertos da §0 com o veredito da (o) na §10.3"
origin: LOOKS-TASK-35
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-27
done_commit: 3e1f3abc
---

# CORR-LOOKS-098 — Reconciliar a lista de abertos da §0 com o veredito da (o) na §10.3

Origin: [LOOKS-TASK-35](/docs/tasks/looks/35-fechamento-da-v2.md)

## Problem

A §0 do plano ("A v2, percorrida em 2026-09-26") põe "a fonte da caixa de
ajuda (§10.3 (o))" entre o que ficou **aberto**, "com razão e destravamento".
A tabela de vereditos que a LOOKS-TASK-35 acrescentou à §10.3 marca a (o)
**fechada**, e o texto da (o) não traz "destrava…" nem "aberta" em lugar
nenhum — nenhum destravamento está escrito. Dois vereditos para a mesma
incógnita contradizem o critério 4 da task.

## Evidência

```text
$ sed -n 132,134p docs/PLAN-LOOKS-PY.md
O que ficou **aberto**, com razão e destravamento: o giro do close-up e a
animação de `FOOT` (§10.3 (p)), a fonte da caixa de ajuda (§10.3 (o)), e as
$ grep -n "^| (o)" docs/PLAN-LOOKS-PY.md
2554:| (o) o painel e o cenário | **fechada**; a caixa de ajuda fica numa fonte de apoio, ...
$ awk 'NR>=3134 && NR<=3415' docs/PLAN-LOOKS-PY.md | grep -ci "destrav\|aberta"
0
```

## Root cause

Hipótese: a §0 foi escrita antes da tabela de vereditos, e as duas não foram
lidas uma contra a outra.

## Fix

Em `docs/PLAN-LOOKS-PY.md`, uma de duas: tirar a fonte da ajuda da lista de
abertos da §0 e nomeá-la como decisão sob a (o) fechada; ou marcar a (o)
aberta para a fonte da caixa de ajuda na tabela e escrever na (o) a razão e o
que a destrava (por exemplo, os texels do ladrilho ■ não rastreados, "não foi
medido").

## Arquivos a criar ou modificar

- docs/PLAN-LOOKS-PY.md

## Verificação

`sed -n 132,134p docs/PLAN-LOOKS-PY.md; grep -n "^| (o)" docs/PLAN-LOOKS-PY.md`
dão o mesmo veredito para a (o); se ela for aberta, `grep -ci destrav` sobre o
trecho da (o) dá pelo menos 1.

## Log de Execução

- 2026-09-27 — Reproduzido: `sed -n 132,134p` pôs "a fonte da caixa de ajuda
  (§10.3 (o))" entre os abertos, `grep -n "^| (o)"` deu a linha 2554
  **fechada**, e `awk 'NR>=3134 && NR<=3415' … | grep -ci "destrav\|aberta"`
  deu `0`. Consertado pela primeira opção, que é a que o resto do repositório
  já diz (a lista de abertos do `CLAUDE.md` só nomeia a (p)): a §0 tira a fonte
  da ajuda da lista de abertos e a nomeia como decisão sob a (o) fechada, com
  a razão (texto da ROM do console, fora do disco e do repositório) e o custo
  medido pelo `confront.py --outside`. Verificação: a §0 (linhas 132-137) e a
  linha `| (o)` (2557) dão o mesmo veredito, fechada; nenhuma outra linha de
  plano, perfil ou `CLAUDE.md` a lista como aberta. `rite gates --cycle looks`
  verde.
- **Closed** — commit `3e1f3abc` (2026-09-27): docs(looks): take the help-box font off the plan's open list
  - Files (`git show --name-status 3e1f3abc`):
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/tasks/looks/CORR-LOOKS-098.md`
