---
id: KITS-TASK-20
---

# KITS-TASK-20 — Fechamento da fase 4 — a janela mínima

## Goal

A fase 4 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` na HEAD com os nomes dos alvos
- [x] Captura refeita na HEAD
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-02

Na máquina Linux, HEAD `d9ca8d6`, com o `:98` sem `-auth`.

O critério 1, com imagem e tela, e sem a imagem:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed   41.35 sec
2/4 Test #19: kits_image .......................   Passed   25.74 sec
3/4 Test #20: kits_gen .........................   Passed    0.02 sec
4/4 Test #21: kits_ui ..........................   Passed    7.11 sec
100% tests passed, 0 tests failed out of 4
$ env -u WE2002_LOOKS_IMAGE ctest --test-dir build -R kits
2/4 Test #19: kits_image .......................***Skipped   0.05 sec
4/4 Test #21: kits_ui ..........................***Skipped   0.08 sec
```

O critério 2 — a captura do estado da KITS-TASK-19 refeita na HEAD, contra a do Linux daquela task e contra a do Windows:

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin \
    --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux-head.png
  wrote work/kits-ui-linux-head.png, 980x640
  window up, at -32000,-32000
$ python3 tools/kits/ui_check.py --compare work/kits-ui-linux.png work/kits-ui-linux-head.png | tail -1
0 of 627200 pixels differ (0.00 %)
$ python3 tools/kits/ui_check.py --compare \
    /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux-head.png | tail -1
12224 of 627200 pixels differ (1.95 %)
```

A captura do Windows não foi refeita na HEAD — esta máquina é a Linux. Não precisa: nada que a janela desenha mudou desde ela.

```
$ git log --oneline 19a3e73..HEAD -- tools/kits/ui tools/kits/core tools/looks
$                                    # vazio
```

O critério 3:

```
$ rite check --cycle kits --json | tail -4
  "errors": 0,
  "warnings": 0,
  "findings": []
```

As verificações da fase 4 no perfil: `tools/kits/ui/` importa só `argparse`, `os`, `sys`, `__future__`, `core.api` e `PySide6` (`grep -hn '^\s*\(import\|from\)' tools/kits/ui/*.py`); `kits_ui` verde e com os dois controles de estilo vermelhos dentro dele (corrida da KITS-TASK-19, na HEAD dela); a janela sobe em `-32000,-32000` no `:98`.

