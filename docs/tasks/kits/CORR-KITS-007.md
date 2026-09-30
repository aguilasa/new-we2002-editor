---
id: CORR-KITS-007
title: "State in §4.3 where the zone-map half of the question is answered"
origin: KITS-TASK-03
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-007 — State in §4.3 where the zone-map half of the question is answered

Origin: [KITS-TASK-03](/docs/tasks/kits/03-primitivas-por-retangulo.md)

## Problem

O §4.3 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) pergunta "em que retângulo do mapa de zonas" caem as primitivas de cada figura. O veredito novo só dá como aberta a geometria da manga longa e da braçadeira, e não diz nada sobre o retângulo do mapa de zonas. Só o §4.6 diz que "a fase 3 cruza essa lista com o mapa de zonas". A verificação da fase exige que o §4.3 dê veredito ou diga o que está aberto.

## Evidência

```text
$ sed -n 329,356p docs/PLAN-KITS-PY.md | grep -n 'zonas'
7:retângulo do mapa de zonas. Se a manga longa e a braçadeira forem outra
$ grep -n 'cruza essa lista com o mapa de zonas' docs/PLAN-KITS-PY.md
422:em x 48–63. A fase 3 cruza essa lista com o mapa de zonas.
```

## Root cause

O objetivo da task se limitava à "primeira metade", e a frase final do §4.3 só lista como aberta a metade da geometria.

## Fix

Acrescentar ao §4.3 uma frase dizendo que o retângulo do mapa de zonas continua aberto, remetendo ao §4.6 e à KITS-TASK-16.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

```text
$ sed -n 329,360p docs/PLAN-KITS-PY.md | grep -c 'mapa de zonas'
```

Hoje dá 1; depois, pelo menos 2.

## Log de Execução
