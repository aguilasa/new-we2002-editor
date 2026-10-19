---
id: K2D-TASK-16
---

# K2D-TASK-16 — controls.py: os controles negativos plantados do §5

## Goal

Os controles do item 4 do [§5](/docs/PLAN-KIT2D-PY.md#5), plantados por comando numa cópia como o `tools/kits/controls.py`: registro trocado, ponteiro fora dos 190, `roms/`, 17 palavras, base ±10 recusam; radar fora das 8 avisa.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/controls.py`
  - `tools/kit2d/selftest.py`
  - `tests/CMakeLists.txt`
- Out:
  - —

## Done criteria

- [ ] `python3 tools/kit2d/controls.py`: última linha `controls: N of N red`, colada da HEAD
- [ ] cada controle do §5.4 tem um nome no catálogo, listado no Log
- [ ] o radar fora das 8 aparece como aviso e não como recusa

## Notes

—

## Log de Execução
