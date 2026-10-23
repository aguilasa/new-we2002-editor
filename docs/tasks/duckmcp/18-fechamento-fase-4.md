---
id: DMCP-TASK-18
---

# DMCP-TASK-18 — Fechamento da Fase 4 — a depuração

## Goal

A Fase 4 (a depuração) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 4 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 4 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/duckmcp/controls.py` sai 0
- [x] `python3 tools/duckmcp/audit.py` colado
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-23 — HEAD de fechamento `945e3c11`. Nenhum código mudou nesta task; nenhum emulador subiu.

**Status.** `rite status --cycle duckmcp` → `tasks: 17 done, 1 in-progress, 14 pending, 0 blocked, 0 skipped (32 total)`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. As duas tasks da Fase 4 no `progress.json`: `DMCP-TASK-16 done 2026-10-23` e `DMCP-TASK-17 done 2026-10-23`, ambas com `reviewed_on`; nenhuma CORR aberta (as CORR das revisões, até a CORR-DMCP-023, estão `done`).

**Gates.**

```text
$ python3 tools/duckmcp/selftest.py --quiet; echo "exit=$?"
duckmcp_selftest: 434 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/duckmcp/controls.py | tail -1; echo "exit=${pipestatus[1]}"
duckmcp_controls: 40 control(s), 40 red as required; 21/21 cover rules (a) to (d); per rule (a) 2/2, (b) 7/7, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
exit=0
$ python3 tools/duckmcp/audit.py | tail -6
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 139 site(s) in 5 file(s) (import 7, client 128, sys.path 4)
pes2: 37 site(s) in 4 file(s) (import 8, client 29, sys.path 0)
by category: import 19, client 180, sys.path 7
audit: 206 raw site(s) in 14 file(s)
$ ctest --test-dir build -R tasks
1/1 Test #6: tasks ............................   Passed    5.56 sec
100% tests passed, 0 tests failed out of 1
```

**Verificações da Fase 4 do perfil**, uma a uma:

- `breakpoints` limpa e pausa depois de exceção; `wait_for_pause` com processo morto é `Fail` citando a armadilha 35 — `python3 tools/duckmcp/selftest.py | grep -E 'debug: (a death mid-wait|an exception inside breakpoints)'` → `ok    debug: a death mid-wait is a Fail citing pitfall 35`, `ok    debug: an exception inside breakpoints propagates`, `ok    debug: an exception inside breakpoints still clears and pauses`. Os controles `breakpoint-not-cleared` e `wait-without-liveness` estão entre os `(debug) 2/2` vermelhos acima.
- Regra (b): sítio novo fora da `PENDING` é vermelho; o tamanho bate com o `audit.py` — `ok    rule (b): no raw site outside PENDING` e `ok    rule (b): PENDING lists 206 site(s) in 108 entries, audit.py counts 206`, contra o `audit: 206 raw site(s) in 14 file(s)` acima; os sete controles `(b) 7/7` ficam vermelhos, entre eles o `import fork` plantado em `tools/kit2d/`.

A Fase 4 está fechada. O `audit.py` em 206 é o número da migração: as Fases 5 a 7 o levam a zero, e a lista `PENDING` encolhe junto.
- **Closed** — commit `a7c78d32` (2026-10-23): docs(duckmcp): close phase 4
  - Files (`git show --name-status a7c78d32`):
    - `M docs/tasks/duckmcp/18-fechamento-fase-4.md`
- **Reviewed** (2026-10-23) at `fe14f07c`: CORR-DMCP-024
