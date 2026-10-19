---
id: KRP-TASK-11
---

# KRP-TASK-11 — Fechamento da fase 3

## Goal

A fase 3 (a cabeça por jogador) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 3 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no plano (o resto só reroda e corrige escrituração)
- Out:
  - código novo

## Done criteria

- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [x] a regra da cabeça escrita no §3.1 sai de `replay.py head`, não de sonda
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **done** (2026-10-16): fechamento da fase 3 na HEAD `a8b403db`, com as correções da fase (CORR-KRP-016 a 019) fechadas (`rite status`: `open fixes: critical 0, high 0, medium 0, low 0`). A regra e o desenho já estavam escritos no §3.1 e no §3.2. O plano ganhou só o parágrafo "Feito na fase 3", no fim do [§3.2](/docs/PLAN-KITS-REPLAY.md#3.2). Esta task não acrescenta controle: os 80 do catálogo são os da fase.

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  353.19 sec
2/5 Test #19: kits_image .......................   Passed   30.34 sec
3/5 Test #20: kits_gen .........................   Passed    0.02 sec
4/5 Test #21: kits_ui ..........................   Passed  236.69 sec
5/5 Test #22: kits_replay ......................   Passed   11.88 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 80 of 80 red
$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

A regra do §3.1 sai do `replay.py head`, rerodado na HEAD (resumo das duas corridas; as linhas por foco são as do Log da KRP-TASK-09):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-9-capture.json --player all --drawn
24 of 24 drawn head(s) sample the game's CLUT on every primitive
22 of 22 distinct player(s) match their disc record
exit=0
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-10-capture.json --player all --drawn
24 of 24 drawn head(s) sample the game's CLUT on every primitive
22 of 22 distinct player(s) match their disc record
exit=0
```

Nas três de perto (`replay-9-3`, `replay-10-2`, `replay-9`), o mesmo comando dá `1 of 1` nas duas linhas.
- **Closed** — commit `5a3e0df4` (2026-10-16): docs(kits): close phase 3 of kits-replay with the gates rerun at HEAD
  - Files (`git show --name-status 5a3e0df4`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/11-fechamento-da-fase-3.md`
- **Reviewed** (2026-10-16) at `37c92fb0`: CORR-KRP-020, CORR-KRP-021
