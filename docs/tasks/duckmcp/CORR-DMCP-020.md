---
id: CORR-DMCP-020
---

# CORR-DMCP-020 — Colar inteira no Log da 15 a transcrição do duckmcp_live

Origin: [DMCP-TASK-15](/docs/tasks/duckmcp/15-fechamento-fase-3.md)

## Problem

O critério 3 pede a saída "colada no Log". O bloco colado deixa de fora as linhas `fork <pid> on :98`,
`window <id>` e `duckstation-mcp 1.0.0 answering` sem reticências nem nota, e se lê como saída inteira
sem ser.

## Evidência

```text
$ DUCKSTATION_TEST_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= ctest --test-dir build -R duckmcp_live -V | grep '^25:'
25:   fork 600608 on :98, log .../work/looks-disc/duckstation-fork.log
25:   window 4194311
25:   duckstation-mcp 1.0.0 answering
25:   tools declared: 95
$ grep -n "answering\|window " docs/tasks/duckmcp/15-fechamento-fase-3.md
(nenhuma saída)
```

## Root cause

Hipótese: a transcrição foi aparada à mão ao ser colada.

## Fix

No Log da `docs/tasks/duckmcp/15-fechamento-fase-3.md`, colar a saída `-V` inteira da corrida.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/15-fechamento-fase-3.md`

## Verificação

`grep -c "answering" docs/tasks/duckmcp/15-fechamento-fase-3.md` dá ao menos 1 (hoje 0).

## Log de Execução
