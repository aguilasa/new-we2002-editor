---
id: KRP-TASK-13
---

# KRP-TASK-13 — Fechamento da fase 4

## Goal

A fase 4 (o goleiro pela família 13) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 4 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no plano (o resto só reroda e corrige escrituração)
  - `docs/tasks/kits-replay/CORR-KRP-027.md`: o link `#3.3` copiado do plano vira `/docs/PLAN-KITS-REPLAY.md#3.3`, que o `rite check` reprovava
- Out:
  - código novo

## Done criteria

- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [x] a decisão reaberta da K3D-TASK-10 aparece datada no §4 do plano
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **done** (2026-10-18): fechamento da fase 4 na HEAD `06341892`, sem correção aberta (`rite status`: `open fixes: critical 0, high 0, medium 0, low 0`). O §4 já trazia a reabertura datada da K3D-TASK-10 ("**Reaberta em 2026-10-12, por decisão do usuário**") e o "Feito" da KRP-TASK-12; o plano ganhou só a linha "Feito na fase 4", no fim do [§4](/docs/PLAN-KITS-REPLAY.md#4). O `rite check` acusou um link relativo `#3.3` na CORR-KRP-027, copiado do plano; virou `/docs/PLAN-KITS-REPLAY.md#3.3`.

```
$ (DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits 2>&1 | tail -8)
4/5 Test #21: kits_ui ..........................   Passed  259.92 sec
5/5 Test #22: kits_replay ......................   Passed   11.86 sec
100% tests passed, 0 tests failed out of 5
Total Test time (real) = 642.11 sec
$ python3 tools/kits/controls.py
controls: 82 of 82 red
$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay      # antes do conserto
ERROR docs/tasks/kits-replay/CORR-KRP-027.md:76: link '#3.3': no heading/anchor '#3.3' in CORR-KRP-027.md
check: 1 error(s), 0 warning(s) in 1 cycle(s)
$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay      # depois
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

Verificações da fase 4 do perfil, na HEAD. A ordem bate com o item 3 do relatório (`34 13 14 16 92 17 18 20 11 19 21`); o grep do diff da KRP-TASK-12 só acha o laço que lê os vértices da seção:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B
  order 34 13 14 16 15 17 18 20 11 19 21
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B --armband
  order 34 13 14 16 92 17 18 20 11 19 21
$ git show e4b2535e -- tools/kits/core/figure.py | grep "^+" | grep -nE "texcoords|uvs?\b|\.vertices|_Vertex\(|points"
112:+        for v in one.vertices:
117:+            moved.append(_Vertex(*p))
```
- **Closed** — commit `87dc98a6` (2026-10-18): docs(kits): close phase 4 of kits-replay with the gates rerun at HEAD
  - Files (`git show --name-status 87dc98a6`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/13-fechamento-da-fase-4.md`
    - `M docs/tasks/kits-replay/CORR-KRP-027.md`
    - `M docs/tasks/kits-replay/progress.json`
  - **Outside declared files** (`docs/PLAN-KITS-REPLAY.md`, `docs/tasks/kits-replay/CORR-KRP-027.md`):
    - `docs/tasks/kits-replay/progress.json`
- **Reviewed** (2026-10-18) at `2475b135`: no finding
