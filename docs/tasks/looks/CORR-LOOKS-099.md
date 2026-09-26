---
id: CORR-LOOKS-099
title: "Corrigir o custo do --pose citado na §4.4 do plano"
origin: LOOKS-TASK-35
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-099 — Corrigir o custo do --pose citado na §4.4 do plano

Origin: [LOOKS-TASK-35](/docs/tasks/looks/35-fechamento-da-v2.md)

## Problem

A §4.4 do plano diz que os comandos de emulador da v2 custam "de 20 s
(`--pose`, `--placement`)". A tabela de gates do perfil diz que o `--pose`
leva ~40 s, e uma corrida levou 37 s; o `--placement` levou ~24 s.

## Evidência

```text
$ grep -n "(\`--pose\`, \`--placement\`)" docs/PLAN-LOOKS-PY.md
1485:  (`--pose`, `--placement`) a 12 min (`--screen`), ...
$ grep -n "oracle.py --pose \[SLOT\]" docs/prompts/perfil-looks.md | cut -c1-120
736:| *(sem alvo ainda)* | as duas variáveis, os dois states e o fork (77 sem eles); ~40 s | `python tools/looks/oracle.py --pose [SLOT]`
$ time python tools/looks/oracle.py --pose
oracle --pose: 0 problem(s)
real	0m37.376s
$ time python tools/looks/confront.py --placement
confront --placement: 0 problem(s) over 2 slot(s)
real	0m24.443s
```

(as duas corridas com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin` e
`WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue`)

## Root cause

Hipótese: o limite inferior foi escrito de memória, não da tabela de custos
medidos do perfil.

## Fix

Na §4.4 de `docs/PLAN-LOOKS-PY.md`, citar a faixa da tabela do perfil: ~25 s
(`--placement`) a 12 min (`--screen`), e o `--pose` em ~40 s.

## Arquivos a criar ou modificar

- docs/PLAN-LOOKS-PY.md

## Verificação

`grep -n "20 s (\`--pose\`" docs/PLAN-LOOKS-PY.md` não imprime nada.

## Log de Execução
