---
id: K2D-TASK-17
---

# K2D-TASK-17 — CLI de escrita: set-palette, set-model, set-radar, apply

## Goal

A CLI escreve pela fachada: `set-palette`, `set-model`, `set-radar` montam o `Edit` e `apply` grava na cópia.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/cli.py`
  - `tools/kit2d/selftest.py`
- Out:
  - —

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kit2d/cli.py` continua só com `core.api` do núcleo
- [ ] uma corrida `set-palette … apply` numa cópia e o `cmp -l` contra o original, colados no Log
- [ ] `apply` apontado para `roms/` sai com erro, visto vermelho

## Notes

—

## Log de Execução
