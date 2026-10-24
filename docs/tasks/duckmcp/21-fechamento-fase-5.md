---
id: DMCP-TASK-21
---

# DMCP-TASK-21 — Fechamento da Fase 5 — a migração do pes2

## Goal

A Fase 5 (a migração do pes2) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 5 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 5 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/pes2/selftest.py` sai 0
- [x] `python3 tools/duckmcp/audit.py` sem sítio do `pes2`
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-23 — HEAD de fechamento `14a47ee6`. Nenhum código mudou nesta task.

**Status.** `rite status --cycle duckmcp` → `tasks: 20 done, 0 in-progress, 12 pending, 0 blocked, 0 skipped (32 total)`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. No `progress.json`: `DMCP-TASK-19 done 2026-10-23` e `DMCP-TASK-20 done 2026-10-23`, as duas com `reviewed_on`. As CORR que saíram delas — CORR-DMCP-025 e 027 (origem 19), 026 e 028 (origem 20) — estão `done`.

**Gates.**

```text
$ python3 tools/pes2/selftest.py | tail -1; echo "exit=${pipestatus[1]}"
OK
exit=0
$ python3 tools/duckmcp/audit.py | tail -5
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 139 site(s) in 5 file(s) (import 7, client 128, sys.path 4)
by category: import 11, client 151, sys.path 7
audit: 169 raw site(s) in 10 file(s)
$ python3 tools/duckmcp/audit.py | grep -c 'tools/pes2/'
0
$ ctest --test-dir build -R tasks
1/1 Test #6: tasks ............................   Passed    5.50 sec
100% tests passed, 0 tests failed out of 1
```

**Verificações da Fase 5 do perfil**, uma a uma:

- PNG de `team-select`, `edit`, `result`, `replay` com o mesmo `sha256sum` antes e depois — medido na DMCP-TASK-19 (Log: as três primeiras antes do bloqueio, `result` depois da CORR-DMCP-025, `result.png` `7ea1a9e4…` dos dois lados). Não refeito aqui: o fechamento confere, não remede, e a árvore de `mcp_drive.py` só mudou depois disso pelas CORR, que trazem a própria verificação.
- `grep -nE 'class (Fail|Skip)|^SKIP = ' tools/pes2/*.py` → nada, `grep=1`. `pes2_selftest` e `pes2_boot` com o veredito de antes (os dois `Passed` na DMCP-TASK-20), refeitos aqui:

```text
$ PES2_IMAGE="$PWD/work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" DISPLAY=:98 XAUTHORITY= ctest --test-dir build -R 'pes2_selftest|pes2_boot'
1/2 Test  #7: pes2_selftest ....................   Passed    2.18 sec
2/2 Test #13: pes2_boot ........................   Passed   67.08 sec
100% tests passed, 0 tests failed out of 2
```

  `cli.py procs` → `pids: []` depois.
- O `audit.py` não lista mais sítio do `pes2`: não há seção `pes2` e o `grep -c` dá 0.

A Fase 5 está fechada.
- **Closed** — commit `d0915337` (2026-10-23): docs(duckmcp): close phase 5
  - Files (`git show --name-status d0915337`):
    - `M docs/tasks/duckmcp/21-fechamento-fase-5.md`
- **Reviewed** (2026-10-24) at `f3d617b3`: no finding
