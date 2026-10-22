---
id: DMCP-TASK-07
---

# DMCP-TASK-07 — Fechamento da Fase 1 — o transporte

## Goal

A Fase 1 (o transporte) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 1 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 1 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-22 — HEAD de fechamento `63b4aaad` (depois da CORR-DMCP-004).

- `rite status --cycle duckmcp` → `tasks: 6 done, 1 in-progress, 25 pending`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. No `progress.json`: DMCP-TASK-05 e 06 `done`, `reviewed_on 2026-10-22`; no `fixes.json`: CORR-DMCP-004 (origem 06) `done`, a única dessas duas tasks.
- `python3 tools/duckmcp/selftest.py; echo self=$?` → `duckmcp_selftest: 137 check(s) ran, 0 failure(s)`, `self=0`.
- `python3 tools/pes2/selftest.py >/dev/null 2>&1; echo pes2=$?` → `pes2=0`.
- `ctest --test-dir build -R '^tasks$'` → `1/1 Test #6: tasks ... Passed 4.94 sec`, `100% tests passed, 0 tests failed out of 1`.

Verificações da Fase 1 do perfil, uma a uma:

- Sessão roubada, sem emulador, pelo servidor de teste — linhas do mesmo selftest: `ok    client: a stolen session is recovered once and the call goes through`, `ok    client: a second loss in a row is an error (SessionLost)`, `ok    client: another ToolError passes without a new handshake`, `ok    client: without reclaim a stolen session fails with SessionLost`.
- Shim: `grep -nE '^class|^def' tools/pes2/mcp.py` → só `51:def self_check(verbose=True):`; `python3 tools/pes2/selftest.py` sai 0 (acima). A exceção medida da CORR-DMCP-004 está lá: o import religa `client.process_alive` (`tools/pes2/mcp.py:46-48`), e `python3 tools/pes2/mcp.py --self-check` → `SELF-CHECK OK: 26 checks`, com `ok   the shim's probe reads fork.running_pids() == []` e `ok   the shim's probe reads fork.running_pids() == [4242]`.
- `python3 -c 'import sys; sys.path.insert(0, "tools"); import duckmcp.client; print(sorted(m for m in sys.modules if m.split(".")[0] in ("PIL","PySide6","numpy")))'` → `[]`.

Sweep: nenhum nome, arquivo ou número mudou nesta task — `sweep: none`.
