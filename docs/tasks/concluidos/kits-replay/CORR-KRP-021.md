---
id: CORR-KRP-021
---

# CORR-KRP-021 — Parágrafo da fase 3 lista como diferença do plano o que o plano já previa

Origin: [KRP-TASK-11](/docs/tasks/concluidos/kits-replay/11-fechamento-da-fase-3.md)

## Problem

O parágrafo novo "Feito na fase 3" da §3.2 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.2)
diz que "o que difere do texto de cima" é:

- o `replay.py` ganhou `head (--player, …)`;
- o `check` passou a julgar as cabeças contra `HEAD_EXPECT`;
- o `confront --tab` ganhou `--player`.

O plano de antes da fase já previa `replay head <captura> [--player <registro>]`. A checagem contra
`HEAD_EXPECT` e o `confront --tab --player` já estão descritos na mesma §3.1 e §3.2, logo acima do
parágrafo. Só `--drawn` e `--plant-hair-column` são desvios de fato, então a frase exagera a
diferença.

## Evidência

```text
$ git show 9303ddc9~1:docs/PLAN-KITS-REPLAY.md | sed -n '/^## 3\./,/^## 4\./p' | grep -n "head"
10:A medição: o subcomando `replay head <captura> [--player <registro>]` decodifica estilo, pele,
$ sed -n 279,284p docs/PLAN-KITS-REPLAY.md
**Feito na fase 3** ([KRP-TASK-09](/docs/tasks/kits-replay/09-medir-a-regra-da-cabeca-estilo-pele-cabelo-e.md)
a [11](/docs/tasks/kits-replay/11-fechamento-da-fase-3.md)). A regra fechou inteira, e por isso a
§3.2 desenha tudo o que a §3.1 mediu, sem parte deixada no default. O que difere do texto de cima:
o `replay.py` ganhou `head` (`--player`, `--drawn`, `--plant-hair-column`), o `check` passou a
julgar a cabeça de toda figura seguida contra `HEAD_EXPECT`, e o `confront --tab` ganhou
`--player`. O jogador real no seletor continua no [§6](#6).
```

## Root cause

(Hipótese.) O parágrafo listou o que a fase 3 acrescentou, não o que se afasta do plano tal como foi
escrito.

## Fix

Em `docs/PLAN-KITS-REPLAY.md`, perto das linhas 279-284: dizer que o `head --player` planejado saiu
como escrito, e listar como desvios só `--drawn` (relatório, não gate, conforme a CORR-KRP-018) e
`--plant-hair-column`. Ou tirar a frase, já que a §3.1 e a §3.2 descrevem tudo isso.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`

## Verificação

`sed -n 279,284p docs/PLAN-KITS-REPLAY.md` não lista mais `head (--player…)` nem `HEAD_EXPECT`
como diferença do texto de cima.

## Log de Execução

### 2026-10-16

Reprodução (`rite reproduce`, HEAD `397e9817`): o plano de antes da fase já trazia
`` `replay head <captura> [--player <registro>]` `` (linha 10 da §3 em `9303ddc9~1`), e o parágrafo
"Feito na fase 3" (linhas 279-284) listava `head` (`--player`, …), `HEAD_EXPECT` e o
`confront --tab --player` como "o que difere do texto de cima".

Conserto: o parágrafo agora diz que o `head --player`, o julgamento contra `HEAD_EXPECT` e o
`confront --tab --player` saíram como o texto de cima descreve, e lista como desvio só `--drawn`
(relatório, não gate, pela CORR-KRP-018) e `--plant-hair-column`.

Verificação:

```text
$ sed -n 279,285p docs/PLAN-KITS-REPLAY.md
**Feito na fase 3** ([KRP-TASK-09](/docs/tasks/kits-replay/09-medir-a-regra-da-cabeca-estilo-pele-cabelo-e.md)
a [11](/docs/tasks/kits-replay/11-fechamento-da-fase-3.md)). A regra fechou inteira, e por isso a
§3.2 desenha tudo o que a §3.1 mediu, sem parte deixada no default. O `head --player`, o
julgamento contra `HEAD_EXPECT` e o `confront --tab --player` saíram como o texto de cima descreve.
O que se afasta dele são duas opções do `head`: `--drawn`, que é relatório e não gate
([CORR-KRP-018](/docs/tasks/kits-replay/CORR-KRP-018.md)), e `--plant-hair-column`, a planta com
dado real. O jogador real no seletor continua no [§6](#6).
```
- **Closed** — commit `8a2ab7dd` (2026-10-16): docs(kits): phase 3 paragraph lists only the real departures from the plan
  - Files (`git show --name-status 8a2ab7dd`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/CORR-KRP-021.md`
