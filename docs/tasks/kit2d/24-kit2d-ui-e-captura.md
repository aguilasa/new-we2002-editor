---
id: K2D-TASK-24
---

# K2D-TASK-24 — kit2d_ui no ctest, make kit2d / kit2d-98 / make.ps1 kit2d e captura nas duas plataformas

## Goal

O `ctest` ganha `kit2d_ui` (venv e tela, pula 77), os alvos de abrir a janela existem nas duas plataformas e a captura sai igual no Windows e no Linux (definição de pronto 5 do [§0](/docs/PLAN-KIT2D-PY.md#0)).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui_check.py`
  - `tests/CMakeLists.txt`
  - `Makefile`
  - `make.ps1`
- Out:
  - —

## Done criteria

- [ ] `ctest --test-dir build -R kit2d_ui` passa no `:98`, e sem venv pula imprimindo por quê (as duas saídas no Log)
- [ ] `make kit2d-98` abre a janela sobre uma cópia, captura citada no Log
- [ ] captura do Windows (−32000) e do Linux comparadas por `ui_check.py`, resultado colado; se o Windows não for medido nesta task, o Log diz e a definição de pronto fica aberta

## Notes

—

## Log de Execução
