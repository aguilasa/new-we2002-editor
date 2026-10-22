---
id: DMCP-TASK-22
---

# DMCP-TASK-22 — `looks`: `Oracle` sobre `Session`, e o `OneSession` some

## Goal

`looks.oracle.Oracle` passa a envolver `duckmcp.Session`: `pause`, `step`, `press`, `capture`, `read_ram`, `load_looks` delegam; `hide_window`/`size_window` e os caminhos de estado vêm da lib; o `OneSession` sai, e o controle `oracle-session-never-renewed` do `looks` migra para o `duckmcp/controls.py`. `main` mapeia `Fail`, `NotRunning` e `ToolError` (§4.3).

## Arquivos a criar ou modificar

- In:
  - `Oracle`, `OneSession`, `hide_window`, `size_window`, `emulator_states_dir`
  - o import de `OneSession`/`hide_window` em `tools/kits/oracle.py`
  - os controles reapontados
- Out:
  - as esperas e os laços de breakpoint (DMCP-TASK-23)

## Done criteria

- [ ] `python3 tools/looks/oracle.py --check-live` passa antes e depois, as duas saídas no Log, com `WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE` absolutos no comando
- [ ] `python3 tools/looks/selftest.py` sai 0, com a contagem de controles colada antes e depois (a diferença é o controle que migrou)
- [ ] `grep -n 'class OneSession' tools/looks/oracle.py` não acha nada
- [ ] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue

## Notes

`kits/oracle.py` importa `OneSession` e `hide_window` do `looks`: o import passa para a lib nesta task, ou o `kits_selftest` quebra.

## Log de Execução
