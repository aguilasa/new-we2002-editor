---
id: KITS-TASK-19
---

# KITS-TASK-19 — Gate `kits_ui` e a mesma captura no Windows e no Linux

## Goal

`kits_ui` julga os PNGs de fora, sem o código sob teste; a captura do mesmo estado sai igual nas duas plataformas.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tests/CMakeLists.txt`

## Done criteria

- [ ] `ctest -R kits_ui` passa com venv e tela, e sai 77 sem eles
- [ ] Controle: tirar o `setStyle("Fusion")` (ou a `QPalette` fixa) numa cópia derruba o `kits_ui`
- [ ] Captura do mesmo estado no Windows e no Linux (`:98`), comparadas por comando versionado; diferença em pixels colada no Log

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4). O Linux é outra máquina: se não estiver à mão, a task fica bloqueada com o comando que a destrava, não fechada.

## Log de Execução
