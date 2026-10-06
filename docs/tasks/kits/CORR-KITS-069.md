---
id: CORR-KITS-069
---

# CORR-KITS-069 — Corrigir a data da medição na partida na §4.7

Origin: [KITS-TASK-42](/docs/tasks/kits/42-medir-numero-partida.md)

## Problem

A §4.7 diz que a medição na partida foi feita em 2026-10-05. O Log de Execução da KITS-TASK-42 e o commit de trabalho a datam de 2026-10-06; 2026-10-05 é a data em que o estado foi salvo e a task aberta.

## Evidência

```text
$ grep -n "Medido numa partida em" docs/PLAN-KITS-PY.md
779:**Medido numa partida em 2026-10-05 ([KITS-TASK-42](/docs/tasks/kits/42-medir-numero-partida.md)),
$ grep -n "^2026-10-0" docs/tasks/kits/42-medir-numero-partida.md
38:2026-10-06. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
$ git log -1 --format='%h %ad' --date=short e1d38dc
e1d38dc 2026-10-06
```

## Root cause

Hipótese: a data foi copiada do parágrafo da KITS-TASK-38 logo acima, ou da data em que o estado foi salvo, em vez do dia da corrida.

## Fix

Trocar "2026-10-05" por "2026-10-06" na linha 779 de `docs/PLAN-KITS-PY.md`.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

```sh
grep -n "Medido numa partida em 2026-10-06" docs/PLAN-KITS-PY.md
```

Sem casamento hoje; um depois do conserto.

## Log de Execução

Reproduzido em 2026-10-06 sobre `008ff95`:

```text
$ grep -n "Medido numa partida em" docs/PLAN-KITS-PY.md
779:**Medido numa partida em 2026-10-05 ([KITS-TASK-42](/docs/tasks/kits/42-medir-numero-partida.md)),
$ git log -1 --format='%h %ad' --date=short e1d38dc
e1d38dc 2026-10-06
```

Conserto: a data da §4.7 passou a ser 2026-10-06, o dia da corrida.

```text
$ grep -n "Medido numa partida em 2026-10-06" docs/PLAN-KITS-PY.md
779:**Medido numa partida em 2026-10-06 ([KITS-TASK-42](/docs/tasks/kits/42-medir-numero-partida.md)),
```
