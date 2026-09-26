---
id: CORR-LOOKS-096
title: Recontar o atraso e as margens da silhueta escritos nos docs
origin: LOOKS-TASK-33
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-096 — Recontar o atraso e as margens da silhueta escritos nos docs

Origin: [LOOKS-TASK-33](/docs/tasks/looks/33-a-janela-animada.md)

## Problem

Três números escritos não saem da corrida. A docstring do `PASS_LAG` diz
"1, 2 and 3 over the sixteen comparisons of both states, eight of them at 1";
a corrida dá 7 em 1, 5 em 2 e 4 em 3. O log da task diz "o pior da varredura
fica a 2,8x a 5,4x do melhor", mas a linha que ele mesmo cita (slot 1, quadro
118: melhor 325, pior 1797) é 5,53x. A docstring do `FRAME_TICKS` cita
43.597.704 para o segundo ciclo do slot 2; o log da task diz 43597700 para a
mesma leitura, e a corrida do revisor deu 43597690.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue python tools/looks/confront.py --silhouette | grep -o "[0-9] behind" | sort | uniq -c
      7 1 behind
      5 2 behind
      4 3 behind
$ grep -n "of them at 1" tools/looks/confront.py
tools/looks/confront.py:1146:of them at 1.
$ grep -n "5,4x" docs/tasks/looks/33-a-janela-animada.md
docs/tasks/looks/33-a-janela-animada.md:206:mínimo real (`MATCH_MARGIN` 2,5x; o pior da varredura fica a 2,8x a 5,4x do
$ grep -n "43,597,704" tools/looks/layout.py
tools/looks/layout.py:2136:43,597,704 and 43,597,704 ticks
```

## Root cause

Hipótese: as contagens foram escritas de memória de uma corrida, ou de uma
corrida anterior à última mudança de código, e não recontadas da saída
colada.

## Fix

Em `tools/looks/confront.py` (docstring do `PASS_LAG`), escrever "seven of
them at 1". No Log de Execução de `docs/tasks/looks/33-a-janela-animada.md`,
"2,8x a 5,5x". Em `tools/looks/layout.py` (docstring do `FRAME_TICKS`), citar
um par que apareça numa corrida colada, ou a faixa vista (43.597.690 a
43.597.721, dentro do `RHYTHM_TICK_SLACK`).

## Arquivos a criar ou modificar

- tools/looks/confront.py
- tools/looks/layout.py
- docs/tasks/looks/33-a-janela-animada.md

## Verificação

`grep -c "of them at 1" tools/looks/confront.py` concorda com
`confront.py --silhouette | grep -c "1 behind"` (7), e `grep -n "5,4x"
docs/tasks/looks/33-a-janela-animada.md` não imprime nada.

## Log de Execução
