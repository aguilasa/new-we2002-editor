---
id: KITS-TASK-32
---

# KITS-TASK-32 — Fechamento da fase 8 — times em vez de tags

## Goal

A fase 8 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` na HEAD
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-04

Na HEAD `7dd8c54`, com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`.

**`ctest --test-dir build -R kits`:**

```
1/4 Test #18: kits_selftest ....................   Passed   63.69 sec
2/4 Test #19: kits_image .......................   Passed   25.21 sec
3/4 Test #20: kits_gen .........................   Passed    0.03 sec
4/4 Test #21: kits_ui ..........................   Passed   26.73 sec
100% tests passed, 0 tests failed out of 4
```

As verificações da fase 8 do perfil, refeitas:

- texto novo no catálogo nas duas línguas: o `kits_selftest` acima inclui a
  checagem do catálogo (`language: 0 failure(s)`);
- proveniência e as conferências no emulador —
  `python3 tools/kits/gen_tables.py --report`: `team_kits: 95 teams with a TEX,
  from the editor's rule; 4 of them confirmed in the game (0 -> TEX_00, 1 ->
  TEX_01, 13 -> TEX_13, 41 -> TEX_41); the editor's ML default item -> TEX_A4; 9
  tags no item reaches (95 96 97 98 99 A0 A1 A2 A3)`; `--editor`: `the exe
  computes EDITOR_RULE`; `--check`: os dois gerados `up to date`;
- `python3 tools/kits/cli.py teams roms/japanese-shift-jis.bin`: `95 teams: 95
  table; 0 empty name(s); 95 with a kit tag`;
- nada do `we-team-editor.exe` no git: `git ls-files | grep -ci
  "we-team-editor/\|\.exe$"` → `0`.

**`rite check --cycle kits`:** `check: 0 error(s), 0 warning(s) in 1 cycle(s)`.
