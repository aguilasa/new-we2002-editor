---
id: K3D-TASK-03
---

# K3D-TASK-03 — Fechamento da fase 1

## Goal

A fase 1 conferida na HEAD.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [x] as verificações da Fase 1 do perfil, cada uma com o comando e a saída colados no Log
- [x] `rite check --cycle kits-3d`: 0 erros
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

Conferência na HEAD `b384a0f` (2026-10-07), com `export DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`.

**Fase 1, item 1 — ctest 4/4, sem *skipped*:**

```
$ ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed  117.99 sec
2/4 Test #19: kits_image .......................   Passed   26.46 sec
3/4 Test #20: kits_gen .........................   Passed    0.11 sec
4/4 Test #21: kits_ui ..........................   Passed   83.97 sec
100% tests passed, 0 tests failed out of 4
```

**Fase 1, item 2 — controles vermelhos, plantas novas no catálogo:**

```
$ python3 tools/kits/controls.py
controls: 29 of 29 red
$ python3 tools/kits/controls.py --list
  cli-kit-swapped              kits/cli.py :: module constant
controls: 29 catalogued
```

As duas plantas de janela da fase estão no catálogo `PLANTS` do `ui_check.py` e ficam vermelhas:

```
$ python3 tools/kits/ui_check.py
        plant 'kit 1 labelled first': figure 0 en-US: the kit selector says 'Kit: first | Away', not 'Kit: Home | Away'; ...
  ok    plant 'kit 1 labelled first' fails the dressing boxes judge
        plant 'Kit combo keeps its first width': en-US to pt-BR: set_box field 39 px, its longest item 'Visitante' 50 px
  ok    plant 'Kit combo keeps its first width' fails the combo width judge
kits_ui: 0 failure(s)
```

**Fase 1, item 3 — chaves nas duas línguas, rótulos lidos nas duas.** A fase não criou chave
nova (reusou `kit_set`, `set_first`, `set_second`); a paridade das chaves e o rótulo lido:

```
$ python3 tools/kits/selftest.py --no-plant
  ok    en-US and pt-BR have the same keys and the same fields
$ python3 tools/kits/ui_check.py
  ok    the dressing boxes: ... and the kit selector Kit Home/Away, Uniforme Casa/Visitante, in en-US and pt-BR
  ok    every combo is as wide as its longest item after a live switch, both ways (field/longest px: en>pt tag_box 223/218, ... en>pt set_box 55/50, en>pt figure_box 115/108, ...)
```

**Fase 1, item 4 — `--kit` e `--set` dão o mesmo digest:**

```
$ python3 tools/kits/selftest.py --image
  ..... cli.py figure TEX_00 figure 0: --kit home ab81491bd0f6, --set 1 ab81491bd0f6, --kit away cdc020a505c8, --set 2 cdc020a505c8
  ok    cli.py figure --kit home draws --set 1's digest and --kit away --set 2's, and the two differ
$ python3 tools/kits/selftest.py --no-plant
  ok    cli.py figure --kit home is --set 1 and --kit away is --set 2
```

**`rite check`:**

```
$ rite check --cycle kits-3d --json
  "errors": 0,
  "warnings": 0,
```
- **Closed** — commit `ae0f2cb` (2026-10-07): docs(kits): record the phase 1 checks of kits-3d at HEAD
  - Files (`git show --name-status ae0f2cb`):
    - `M docs/tasks/kits-3d/03-fechamento-fase-1.md`
- **Reviewed** (2026-10-07) at `448ea7b`: no finding
