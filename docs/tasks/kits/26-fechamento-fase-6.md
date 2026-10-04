---
id: KITS-TASK-26
---

# KITS-TASK-26 — Fechamento da fase 6 — o 3D

## Goal

A fase 6 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` na HEAD
- [x] `controls.py` na HEAD
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-04

Na máquina Linux, HEAD `0595613`, `:98` sem `-auth`, `WE2002_LOOKS_IMAGE` na japonesa.

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed   56.30 sec
2/4 Test #19: kits_image .......................   Passed   24.54 sec
3/4 Test #20: kits_gen .........................   Passed    0.02 sec
4/4 Test #21: kits_ui ..........................   Passed   24.43 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py | tail -1
controls: 23 of 23 red
$ rite check --cycle kits --json | tail -4
  "errors": 0,
  "warnings": 0,
  "findings": []
```

As verificações da fase 6 no perfil, na mesma HEAD:

```
$ python3 tools/kits/selftest.py | grep -E 'scene \(|geometry'
  ok    with no geometry disc, api.figure says why
  ok    lone TEX: with no geometry path, the figure takes WE2002_LOOKS_IMAGE
  ok    only core/figure.py imports the looks scene (section 3.1)
$ python3 tools/kits/selftest.py --image | grep -E 'TEX_00 set . figure .: 486|figure:'
  ok    TEX_00 set 1 figure 0: 486/488 swapped draws the other figure's colours
  ok    TEX_00 set 2 figure 0: 486/488 swapped draws the other figure's colours
  ok    TEX_00 set 1 figure 1: 486/488 swapped draws the other figure's colours
  ok    TEX_00 set 2 figure 1: 486/488 swapped draws the other figure's colours
figure: 0 failure(s)
$ python3 tools/kits/ui_check.py | grep -E '3D|kits_ui:'
  ok    3D TEX_00: the four combinations draw a figure, and set 1 is not set 2 for either figure (…)
  ok    with no geometry disc the 3D tab is off with the sentence, and Plan is the same
  ok    plant '3D set ignored' fails the 3D judge
  ok    plant '3D tab never off' fails the 3D off judge
  ok    plant 'Plan changes without geometry' fails the 3D off judge
kits_ui: 0 failure(s)
```

Texto novo da aba 3D no catálogo nas duas línguas: o `kits_selftest` afirma chaves e campos iguais (`en-US and pt-BR have the same keys and the same fields`), dentro do verde acima.
- **Closed** — commit `7355894` (2026-10-04): docs(kits): close phase 6 -- kits ctest, controls and rite check at HEAD
  - Files (`git show --name-status 7355894`):
    - `M docs/tasks/kits/26-fechamento-fase-6.md`
- **Reviewed** (2026-10-04) at `4856994`: no finding
