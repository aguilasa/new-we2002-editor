---
id: KRP-TASK-26
---

# KRP-TASK-26 — Desfazer a KRP-TASK-13 e fechar a fase 4a

## Goal

O fechamento da fase 4 sai do plano e a fase 4a fica fechada: a linha "Feito na fase 4" do §4, que a [KRP-TASK-13](/docs/tasks/concluidos/kits-replay/13-fechamento-da-fase-4.md) escreveu, dá lugar ao que a fase 4a deixou (o goleiro do `EDT_MOD.BIN` de volta); a tabela do §10 ganha a linha da 4a; os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 4a do perfil rodam de novo na HEAD.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md` (§4: a linha "Feito na fase 4" substituída pelo resultado da 4a; §10: a linha da fase 4a)
- Out:
  - código novo
  - o conserto do link da CORR-KRP-027 que a KRP-TASK-13 fez: fica

## Done criteria

- [x] `grep -n "Feito na fase 4" docs/PLAN-KITS-REPLAY.md`: toda ocorrência está marcada como desfeita, datada, e o §4 traz "Feito na fase 4a" com o goleiro do `EDT_MOD.BIN`
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **done** (2026-10-19): fechamento da fase 4a na HEAD `f9b31080`. A linha "Feito na fase 4" do §4 virou "Feito na fase 4, e desfeito em 2026-10-19", com as duas lacunas daquela fase ditas no passado, e logo abaixo entrou "Feito na fase 4a", com o goleiro do `EDT_MOD.BIN`. A tabela do §10 marca a fase 4 como desfeita na 4a e ganhou a linha da 4a.

```
$ grep -n "Feito na fase 4" docs/PLAN-KITS-REPLAY.md
386:**Feito na fase 4, e desfeito em 2026-10-19** ([KRP-TASK-12](/docs/tasks/kits-replay/12-goleiro-pela-familia-13-com-a-pose-medida-e-a-92.md)
391:**Feito na fase 4a** ([KRP-TASK-25](/docs/tasks/kits-replay/25-desfazer-a-krp-task-12-goleiro-volta-ao-edt-mod.md)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  337.12 sec
2/5 Test #19: kits_image .......................   Passed   27.32 sec
3/5 Test #20: kits_gen .........................   Passed    0.02 sec
4/5 Test #21: kits_ui ..........................   Passed  243.60 sec
5/5 Test #22: kits_replay ......................   Passed   11.65 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 87 of 87 red
$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

As verificações da fase 4a do perfil (digest de `e4b2535e^`, `match_scene` igual, reversão datada no §4) estão medidas no Log da [KRP-TASK-25](/docs/tasks/concluidos/kits-replay/25-desfazer-a-krp-task-12-goleiro-volta-ao-edt-mod.md); o código não mudou desde ela.
- **Closed** — commit `1d065a8b` (2026-10-19): docs(kits): close phase 4a of kits-replay, the family-13 goalkeeper undone
  - Files (`git show --name-status 1d065a8b`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/26-desfazer-a-krp-task-13-e-fechar-a-fase-4a.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
  - **Outside declared files** (`docs/PLAN-KITS-REPLAY.md`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-19) at `1a40b318`: no finding
