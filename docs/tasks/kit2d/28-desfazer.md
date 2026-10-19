---
id: K2D-TASK-28
---

# K2D-TASK-28 — QUndoStack: desfazer e refazer dentro da sessão

## Goal

Cor, modelo e radar entram num `QUndoStack`; desfazer até o começo deixa o buffer limpo.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui/app.py`
- Out:
  - —

## Done criteria

- [ ] `ui_check.py`: três edições, três desfazer, buffer limpo; três refazer, `diff()` igual ao de antes (contagens no Log)

## Notes

—

## Log de Execução
