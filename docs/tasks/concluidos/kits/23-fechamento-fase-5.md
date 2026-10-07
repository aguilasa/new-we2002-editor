---
id: KITS-TASK-23
---

# KITS-TASK-23 — Fechamento da fase 5 — as duas mudanças no `looks`

## Goal

A fase 5 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R looks` na HEAD, os quatro pelo nome
- [x] `ctest -R kits` na HEAD
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-03

Na máquina Linux, HEAD `10aba5a`, com o `:98` sem `-auth`, o venv, os dois discos e os dois states:

```
$ export DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
         WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
$ ctest --test-dir build -R 'looks|kits'
1/8 Test #14: looks_selftest ...................   Passed   14.05 sec
2/8 Test #15: looks_image ......................   Passed    2.98 sec
3/8 Test #16: looks_ui .........................   Passed  243.68 sec
4/8 Test #17: looks_live .......................   Passed    8.15 sec
5/8 Test #18: kits_selftest ....................   Passed   45.85 sec
6/8 Test #19: kits_image .......................   Passed   25.13 sec
7/8 Test #20: kits_gen .........................   Passed    0.04 sec
8/8 Test #21: kits_ui ..........................   Passed    8.10 sec
100% tests passed, 0 tests failed out of 8
```

As verificações da fase 5 no perfil, na mesma HEAD:

```
$ python3 tools/looks/selftest.py | grep 'controls red'
  ..... 114 of 114 controls red
$ python3 tools/looks/scene.py --check-image | grep -E 'set 1|check-image'
      TEX_A4 set 1 samples [48], set 2 samples [10796]
      TEX_A4 set 1 9b9410e6d2591824, set 2 9b9410e6d2591824: the same picture
      TEX_00 set 1 samples [48], set 2 samples [10556]
      TEX_00 set 1 66f166d86fa5a396, set 2 9a44dba5ad6145df: another picture
      TEX_98 set 1 samples [48], set 2 samples [11400]
      TEX_98 set 1 4a8089cb1a6b6a5a, set 2 b9c612c97571e98b: another picture
scene --check-image: ok
```

Suplente do `TEX_A4` = titular; tag que difere, quadro diferente; e sem argumento novo o `Builder` veste o `TEX_A4`, conjunto 1 (self-check do `scene`, dentro do `looks_selftest`).

```
$ rite check --cycle kits --json | tail -4
  "errors": 0,
  "warnings": 0,
  "findings": []
```
- **Closed** — commit `1c3308c` (2026-10-03): docs(kits): close phase 5 -- looks and kits ctest and rite check at HEAD
  - Files (`git show --name-status 1c3308c`):
    - `M docs/tasks/kits/23-fechamento-fase-5.md`
- **Reviewed** (2026-10-03) at `0f204d2`: no finding
