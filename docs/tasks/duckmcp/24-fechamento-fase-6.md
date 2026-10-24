---
id: DMCP-TASK-24
---

# DMCP-TASK-24 — Fechamento da Fase 6 — a migração do looks

## Goal

A Fase 6 (a migração do looks) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 6 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 6 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/looks/selftest.py` sai 0
- [x] `python3 tools/duckmcp/audit.py` sem sítio do `looks` de `import` nem de `client`; os de `sys.path` são da DMCP-TASK-30 na `PENDING` e ficam
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-24 — HEAD de fechamento `3d26d51c`. Nenhum código mudou nesta task.

**O terceiro critério foi reescrito antes de medir.** Ele dizia "sem sítio do `looks`", e isso a Fase 6 não tem como entregar: os quatro `sys.path.insert` que sobram no `looks` põem `tools/pes2` no caminho, e a DMCP-TASK-17 os atribuiu à DMCP-TASK-30 na `PENDING`, porque eles só perdem o objeto quando os shims forem apagados — é a Fase 9 do [§6](/docs/PLAN-DUCKMCP-PY.md#6) que leva o `audit.py` a zero. As verificações da Fase 6 do perfil não pedem zero do `looks`. A fonte de verdade vence, e o critério passou a dizer o que a fase entrega: nenhum sítio de `import` nem de `client`.

**Status.** `rite status --cycle duckmcp` → `tasks: 23 done, 0 in-progress, 9 pending, 0 blocked, 0 skipped (32 total)`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. No `progress.json`: `DMCP-TASK-22 done 2026-10-24` e `DMCP-TASK-23 done 2026-10-24`, as duas com `reviewed_on`; a única CORR que saiu delas, CORR-DMCP-030, está `done`.

**Gates.**

```text
$ python3 tools/looks/selftest.py | tail -2; echo "exit=${pipestatus[1]}"
controls: 0 failure(s)
looks_selftest: 0 failure(s)
exit=0
$ python3 tools/duckmcp/audit.py | grep -E 'tools/looks|^looks|^audit:'
tools/looks/atlas.py:105: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
tools/looks/iso_source.py:27: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pes2"))
tools/looks/oracle.py:75: sys.path: sys.path.insert(0, PES2)
tools/looks/sprites.py:45: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pes2"))
looks: 4 site(s) in 4 file(s) (import 0, client 0, sys.path 4)
audit: 34 raw site(s) in 9 file(s)
$ grep -n "'tools/looks" tools/duckmcp/selftest.py
215:    ('DMCP-TASK-30', 'tools/looks/atlas.py', 'sys.path',
217:    ('DMCP-TASK-30', 'tools/looks/iso_source.py', 'sys.path',
219:    ('DMCP-TASK-30', 'tools/looks/oracle.py', 'sys.path',
221:    ('DMCP-TASK-30', 'tools/looks/sprites.py', 'sys.path',
$ ctest --test-dir build -R tasks
1/1 Test #6: tasks ............................   Passed    6.59 sec
100% tests passed, 0 tests failed out of 1
```

**Verificações da Fase 6 do perfil**, uma a uma:

- `oracle.py --check-live` passa; `oracle.py --screen` sem diferença contra `screen.json`; `--pose 1` com as mesmas matrizes — medido nas tasks da fase: `--check-live` `0 failure(s)` antes e depois na DMCP-TASK-22 e depois na 23; `--screen` `0 difference(s) from screen.json` na 22 e na 23; `--pose 1` com `diff -r` vazio e 207 paradas dos dois lados na 23. Não refeito aqui: nada em `tools/looks/` mudou desde (`git diff --quiet dc42d7ce HEAD -- tools/looks/`, saída 0).
- `class OneSession` não existe (`grep -n 'class OneSession' tools/looks/oracle.py` → nada, saída 1); o controle de sessão roubada está no `duckmcp/controls.py` e é visto vermelho (`controls.py --only oracle-session-never-renewed` → `red`, no Log da 22).
- `looks_selftest` verde, com a contagem de controles antes e depois explicada: 114 → 113 na 22 (o que migrou), 113 na 23 (nenhum controle mirava o código movido).

A Fase 6 está fechada.
- **Closed** — commit `cae92110` (2026-10-24): docs(duckmcp): close phase 6
  - Files (`git show --name-status cae92110`):
    - `M docs/tasks/duckmcp/24-fechamento-fase-6.md`
