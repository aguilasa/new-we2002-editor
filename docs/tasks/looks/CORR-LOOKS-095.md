---
id: CORR-LOOKS-095
title: O ritmo do ui_check tem de ficar vermelho com a taxa errada
origin: LOOKS-TASK-33
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-095 — O ritmo do ui_check tem de ficar vermelho com a taxa errada

Origin: [LOOKS-TASK-33](/docs/tasks/looks/33-a-janela-animada.md)

## Problem

No `--animate-for 2.574` do `ui_check.py`, o `measure_walk` calcula o `want`
em linha reta (68,0) e aceita `WALK_PASS_SLACK = 3` passadas. A contagem
exata em 2,574 s é 67. Um relógio a 60, 62, 62,5 ou 63 quadros por segundo
cai em 68 a 71 passadas, e todos passam. A outra asserção de taxa compara a
taxa que a janela relata, que é o próprio `WalkClock.rate` — o mesmo atributo
que o relógio usaria. Um relógio convertendo a 60 Hz nominais, ou até ~5%
rápido, fica verde; o perfil descreve o gate como "`--animate-for` no ritmo
medido", e ele não confere isso.

## Evidência

```text
$ cd tools/looks && WE2002_LOOKS_IMAGE=../../roms/japanese-shift-jis.bin python - <<'EOF'
import scene
c = scene.walk_cycle(2)
for r in (57.0, 59.817, 60.0, 62.0, 62.5, 63.0):
    k = scene.WalkClock(c, rate=r, running=True, now=0.0)
    print(r, k.pass_now(2.574), 'within slack 3 of want 68.0:', abs(k.pass_now(2.574) - 68.0) <= 3)
EOF
57.0 64 within slack 3 of want 68.0: False
59.817 67 within slack 3 of want 68.0: True
60.0 68 within slack 3 of want 68.0: True
62.0 70 within slack 3 of want 68.0: True
63.0 71 within slack 3 of want 68.0: True
$ grep -n "WALK_PASS_SLACK = \|want = WALK_RUN_SECONDS" tools/looks/ui_check.py
```

## Root cause

A corrida de relógio de parede é ruidosa, e a folga foi dimensionada para o
tremor. Nada mostrou depois que a folga ainda separa a taxa medida da taxa
errada mais plausível (60 Hz nominais, ou 60/1,001): um defeito plantado de
"taxa errada em alguns por cento" nunca entrou em `WALK_BREAKS`.

## Fix

Em `tools/looks/ui_check.py`, `measure_walk`: calcular o `want` por
`scene.WalkClock(cycle).pass_now(seconds)` na taxa medida, e julgar a taxa
por uma corrida mais longa ou pelo relato do próprio relógio (quadros
decorridos sobre segundos), não por contagem de passadas com 3 de folga.
Acrescentar a `WALK_BREAKS` uma terceira entrada que planta 60 Hz no
`scene.WalkClock.frames` e exigir o vermelho.

## Arquivos a criar ou modificar

- tools/looks/ui_check.py

## Verificação

`python tools/looks/ui_check.py` imprime uma linha
`negative: breaking the frame rate reddens the walk`; com `rate=60.0` no
`WalkClock.frames` numa cópia da árvore, o `measure_walk` devolve `bad` não
vazio.

## Log de Execução
