---
id: KITS-TASK-12
---

# KITS-TASK-12 — Gerador de `generated/` a partir do C++, com `--check` no ctest

## Goal

Os offsets de nome de time (`OFS_TEAM_NAME_*`), os comprimentos e o `TEAM_NAMES[120][20]` saem de `Offsets.hpp`/`Tables.cpp` para `core/generated/` por gerador; o `--check` entra no ctest como o `rc2ui.py`.

## Arquivos a criar ou modificar

- `tools/kits/gen_tables.py`
- `tools/kits/core/generated/`
- `tests/CMakeLists.txt`

## Done criteria

- [ ] `python tools/kits/gen_tables.py --check` sai 0 na HEAD
- [ ] Controle: um nome de `TEAM_NAMES` alterado numa cópia do `Tables.cpp` faz o `--check` sair diferente de 0 (vermelho no Log)
- [ ] `ctest -R kits` lista o alvo do gerador pelo nome
- [ ] As linhas de `TEAM_NAMES` que valem para cada time foram conferidas no `legacy/mfc/edDlg.cpp` e a referência (arquivo:linha) está no Log
- [ ] A seção do `kits` no `NOTICE.md` ganha, no mesmo commit, a linha da tabela `TEAM_NAMES` (Francesco Moriero, `legacy/mfc/`, sem licença)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.3).

## Log de Execução
