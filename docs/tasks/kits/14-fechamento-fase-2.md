---
id: KITS-TASK-14
---

# KITS-TASK-14 — Fechamento da fase 2 — núcleo, lado ROM

## Goal

A fase 2 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `gen_tables.py --check` e `ctest -R kits` na HEAD, saídas coladas
- [x] `cli.py teams` nas duas imagens de `roms/`, contagens coladas
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-01 — na HEAD `e64aabbe`

```
$ python tools/kits/gen_tables.py --check      # exit 0
gen_tables: tools\kits\core\generated\team_names.py is up to date
$ python tools/kits/gen_tables.py --negative | tail -1      # exit 0
control: --check --src <copy> exit 1, 1 generated line(s) differ -- red, held
```

Build fora da árvore (`%TEMP%/build-kits08`, reconfigurado na HEAD):

```
$ ctest -N -R kits
  Test #14: kits_selftest
  Test #15: kits_image
  Test #16: kits_gen
Total Tests: 3
$ WE2002_LOOKS_IMAGE=.../roms/japanese-shift-jis.bin ctest -R kits -V
14:   ..... 12 of 12 controls red
14: kits_selftest: 0 failure(s)
1/3 Test #14: kits_selftest ....................   Passed   61.44 sec
15:   ..... 105 of 105 kits pass the guard
15:   ..... confront 1: 105 of 105 tags equal
15: kits_image: 0 failure(s)
2/3 Test #15: kits_image .......................   Passed   76.42 sec
16: gen_tables: tools\kits\core\generated\team_names.py is up to date
3/3 Test #16: kits_gen .........................   Passed    0.10 sec
100% tests passed out of 3
```

`cli.py teams` nas duas imagens:

```
$ python tools/kits/cli.py teams roms/japanese-shift-jis.bin | tail -1      # exit 0
95 teams: 95 table; 0 empty name(s); 0 with a kit tag
$ python tools/kits/cli.py teams roms/golden-european-deluxe.bin | tail -1      # exit 0
95 teams: 95 rom; 0 empty name(s); 0 with a kit tag
$ python tools/kits/cli.py teams --against $TEMP/core_names_eu.tsv roms/golden-european-deluxe.bin | tail -1
against we2002_core: 95 of 95 ROM names equal (95 lines in core_names_eu.tsv)
```

(o `core_names_eu.tsv` é o dump do `we2002_golden_tool names` da KITS-TASK-13; o `tests/golden_tool.cpp` não mudou desde então.)

```
$ rite check --cycle kits --json
{'errors': 0, 'warnings': 0}
```
- **Closed** — commit `992f0b07` (2026-10-01): docs(kits): close phase 2, checked at HEAD
  - Files (`git show --name-status 992f0b07`):
    - `M docs/tasks/kits/14-fechamento-fase-2.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
