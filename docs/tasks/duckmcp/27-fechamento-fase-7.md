---
id: DMCP-TASK-27
---

# DMCP-TASK-27 — Fechamento da Fase 7 — a migração do kits

## Goal

A Fase 7 (a migração do kits) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 7 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 7 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/kits/selftest.py` sai 0
- [x] `python3 tools/duckmcp/audit.py` sem sítio do `kits` de `import` nem de `client`; os de `sys.path` são da DMCP-TASK-30 na `PENDING` e ficam
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-26 — HEAD de fechamento `b5d9b1d9`. Nenhum código mudou nesta task.

**O terceiro critério foi reescrito antes de medir**, pelo mesmo motivo do da [DMCP-TASK-24](/docs/tasks/duckmcp/24-fechamento-fase-6.md): os dois `sys.path.insert` que sobram no `kits` põem `tools/pes2` no caminho, e a `PENDING` os dá à DMCP-TASK-30, porque o zero do `audit.py` é da Fase 9 ([§6](/docs/PLAN-DUCKMCP-PY.md#6)). As verificações da Fase 7 do perfil não pedem zero do `kits`. O critério passou a dizer o que a fase entrega: nenhum sítio de `import` nem de `client`.

**Status.** `rite status --cycle duckmcp` → `tasks: 26 done, 0 in-progress, 6 pending, 0 blocked, 0 skipped (32 total)`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. No `progress.json`: `DMCP-TASK-25 done 2026-10-25` e `DMCP-TASK-26 done 2026-10-25`, as duas com `reviewed_on`; a única CORR delas, CORR-DMCP-032, está `done`.

**Gates.**

```text
$ python3 tools/kits/selftest.py | tail -3; echo "exit=${pipestatus[1]}"
  ..... 88 of 88 controls red
controls: 0 failure(s)
kits_selftest: 0 failure(s)
exit=0
$ python3 tools/duckmcp/audit.py | grep -E 'tools/kits|^kits|^audit:'
tools/kits/oracle.py:133: sys.path: sys.path.insert(0, _path)
tools/kits/core/tex.py:35: sys.path: sys.path.insert(0, _path)
kits: 2 site(s) in 2 file(s) (import 0, client 0, sys.path 2)
audit: 7 raw site(s) in 7 file(s)
$ grep -n "'tools/kits" tools/duckmcp/selftest.py
173:    ('DMCP-TASK-30', 'tools/kits/core/tex.py', 'sys.path',
175:    ('DMCP-TASK-30', 'tools/kits/oracle.py', 'sys.path',
$ ctest --test-dir build -R tasks
1/1 Test #6: tasks ............................   Passed    5.74 sec
100% tests passed, 0 tests failed out of 1
```

**Verificações da Fase 7 do perfil**, uma a uma:

- `kits_replay` e `kits_selftest` com o veredito de antes (`Passed` antes e depois na DMCP-TASK-25; `kits_selftest` `Passed` na 26), refeitos aqui; `grep -c 'client.call(' tools/kits/*.py` dá 0 em todo arquivo (`grep -cE 'client\.call\(' tools/kits/*.py | grep -v ':0$'` → nada, saída 1):

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R 'kits_replay|tasks'
2/2 Test #22: kits_replay ......................   Passed   11.83 sec
100% tests passed, 0 tests failed out of 2
```

  (o `kits_selftest` é o `python3 tools/kits/selftest.py` acima, `0 failure(s)`.)
- O monkeypatch do `kits/selftest.py` troca atributos de `duckmcp.fork`, não do shim: `tools/kits/selftest.py:2085` → `from duckmcp import fork as lib`, e o comentário de `:2088` diz que os patches vão no `duckmcp.fork`.
- `dump_slot` recusa joystick, e o controle novo é visto vermelho: `python3 tools/kits/controls.py --only oracle-dump-joystick-unasked` → `RED    oracle-dump-joystick-unasked kits/oracle.py :: dump_slot`, `controls: 1 of 1 red`.

A Fase 7 está fechada.
- **Closed** — commit `2a42e57f` (2026-10-26): docs(duckmcp): close phase 7
  - Files (`git show --name-status 2a42e57f`):
    - `M docs/tasks/duckmcp/27-fechamento-fase-7.md`
- **Reviewed** (2026-10-26) at `b284bb46`: CORR-DMCP-034
