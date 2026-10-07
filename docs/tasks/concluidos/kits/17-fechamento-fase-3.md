---
id: KITS-TASK-17
---

# KITS-TASK-17 — Fechamento da fase 3 — plano e zonas, sem janela

## Goal

A fase 3 conferida na HEAD, e ainda sem arquivo em `tools/kits/ui/`.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` e `controls.py` na HEAD, saídas coladas
- [x] `git ls-files tools/kits/ui` vazio
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-02

Na HEAD `b2c3a506`, build fora da árvore (`$TEMP/build-kits08`, reconstruído antes):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir $TEMP/build-kits08 -R kits
1/3 Test #14: kits_selftest ....................   Passed   70.92 sec
2/3 Test #15: kits_image .......................   Passed   65.97 sec
3/3 Test #16: kits_gen .........................   Passed    0.09 sec
100% tests passed out of 3
$ python tools/kits/controls.py | tail -1
controls: 16 of 16 red
$ git ls-files tools/kits/ui
(vazio)
$ rite check --cycle kits --json
  "errors": 0, "warnings": 0, "findings": []
```

As verificações da fase 3 no perfil:

```
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | grep -E "^figure|verdict"
figure 0: 237 primitive(s) -- 201 in one zone, 7 across zones, 29 in a declared gap, 0 outside the map
figure 1: 429 primitive(s) -- 377 in one zone, 23 across zones, 29 in a declared gap, 0 outside the map
verdict: section 4.6 holds
$ python tools/kits/cli.py zones --negative roms/japanese-shift-jis.bin | tail -1
control red, held: section 4.6 fails on the moved map
$ python tools/kits/cli.py export --work-bitmap --tag 00 --tag A4 --out $TEMP/wb17 roms/japanese-shift-jis.bin
$ sha256sum *.png | cut -c1-16,65-
b3517648a88e779b *TEX_00_set1_keeper.png
70d60662480fdcc4 *TEX_00_set1_player.png
18c0350565201d56 *TEX_00_set2_keeper.png
6401ecddc1b97f74 *TEX_00_set2_player.png
706796b4b1f29fdf *TEX_A4_set1_keeper.png      (os quatro do TEX_A4 iguais)
```

Mapa medido passa, deslocado 1 px reprova; `TEX_A4` titular = suplente, `TEX_00` difere. Fase 3 fechada sem janela.
- **Closed** — commit `d208afca` (2026-10-02): chore(kits): close phase 3 -- gates, controls and phase checks at HEAD
  - Files (`git show --name-status d208afca`):
    - `M docs/tasks/kits/17-fechamento-fase-3.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
- **Reviewed** (2026-10-02) at `cc4bf1fc`: no finding
