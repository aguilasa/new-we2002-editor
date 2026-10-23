---
id: DMCP-TASK-25
---

# DMCP-TASK-25 — `kits`: `dump_slot`, `matrix_stops`, `pose_capture`, `read_frame` e `vram` sobre a lib

## Goal

`dump_slot` passa a `Session` (e ganha a guarda de joystick que não tinha); `matrix_stops` e `pose_capture` usam `duckmcp.debug`; `read_frame` usa o `frame_commands` do `looks` em vez da cópia; o empacotamento BGR555 vem do `duckmcp.vram`.

## Arquivos a criar ou modificar

- In:
  - as funções nomeadas
  - `tools/duckmcp/selftest.py`: encolher no mesmo commit as entradas do `PENDING` da regra (b) que esta task remove; sem isso o check de entrada velha fica vermelho (CORR-DMCP-023)
- Out:
  - controles e monkeypatch (DMCP-TASK-26)

## Done criteria

- [ ] `ctest --test-dir build -R kits_replay` com o ambiente do perfil do `kits` no comando: mesmo veredito antes e depois, colado no Log
- [ ] `grep -cE 'client\.call\(' tools/kits/*.py` dá 0
- [ ] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [ ] `python3 tools/kits/selftest.py` sai 0

## Notes

## Log de Execução
