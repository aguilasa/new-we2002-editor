---
id: CORR-KITS-007
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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `7c6c8309`)

```text
$ sed -n 329,356p docs/PLAN-KITS-PY.md | grep -n 'zonas'
7:retângulo do mapa de zonas. Se a manga longa e a braçadeira forem outra
$ grep -n 'cruza essa lista com o mapa de zonas' docs/PLAN-KITS-PY.md
422:em x 48–63. A fase 3 cruza essa lista com o mapa de zonas.
```

REPRODUCED. Causa raiz confirmada: o fecho do §4.3 dava como aberta só a geometria da manga longa e da braçadeira.

### O que foi feito

Frase nova no fim do §4.3: a pergunta do mapa de zonas continua aberta, e quem a responde é o cruzamento do §4.6, na KITS-TASK-16 (`source_of_truth: /docs/PLAN-KITS-PY.md#4.6`).

### Verificação

A faixa fixa da seção Verificação (`sed -n 329,360p`) deixou de cobrir o fim do §4.3: a CORR-KITS-005, que rodou antes nesta mesma leva, pôs sete linhas nele. Por isso a conferência vai pelos cabeçalhos:

```text
$ sed -n '/^### 4.3/,/^### 4.4/p' docs/PLAN-KITS-PY.md | grep -c 'mapa de zonas'
2
$ sed -n 329,360p docs/PLAN-KITS-PY.md | grep -c 'mapa de zonas'
1
```
- **Closed** — commit `d197ec19` (2026-09-30): docs(kits): say in plan 4.3 that the zone-map half is answered by 4.6
  - Files (`git show --name-status d197ec19`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-007.md`
