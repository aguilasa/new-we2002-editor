---
id: DMCP-TASK-01
---

# DMCP-TASK-01 — Esqueleto de tools/duckmcp/: __init__, errors.py, env.py e duckmcp_selftest

## Goal

Existe o pacote `tools/duckmcp/` com `errors.py` (`SKIP = 77`, `Fail`, `Skip`, `NotRunning`, `ToolError`, `SessionLost`) e `env.py` (as variáveis `DUCKSTATION_*` com fallback `PES2_*`, `display()`, `x_env()`, `fork_home()`, `appimage()`, `data_dir()`, `savestates_dir()`, `state_path(serial, slot)`, `is_roms()`), um `selftest.py` que roda os self-checks deles, e o alvo `duckmcp_selftest` no `ctest`, que nunca pula. Nenhum projeto muda ainda.

## Arquivos a criar ou modificar

- In:
  - os quatro arquivos de `tools/duckmcp/` e o `add_test` em `tests/CMakeLists.txt`
- Out:
  - `client.py`, `fork.py` e o resto do §3.1 (fases 1 a 4)
  - qualquer arquivo de `tools/pes2/`, `tools/looks/`, `tools/kits/`

## Done criteria

- [ ] `git merge-base --is-ancestor f21182ea HEAD` sai 0 (a PES2-TASK-03 está na base, §2 decisão 4)
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest afirma: `DUCKSTATION_MCP_PORT` ganha de `PES2_MCP_PORT`; só `PES2_MCP_PORT` definida vale; nenhuma das duas dá `2346`
- [ ] o selftest afirma: `x_env(':98')` tem `XAUTHORITY == ''` e `x_env(':1')` não toca no `XAUTHORITY` herdado
- [ ] uma planta (inverter a precedência de uma variável no `env.py`) deixa o selftest vermelho, visto no Log
- [ ] `ctest --test-dir build -R duckmcp_selftest` passa, sem *skipped*

## Notes

Modelo de forma: `tools/kit2d/selftest.py` e o alvo `kit2d_selftest`. O `drive.py` zera `XAUTHORITY` em todo display; a regra certa é a do `fork.env_for` (só `:98`), §4.3.

## Log de Execução
