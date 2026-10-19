---
id: K2D-TASK-10
---

# K2D-TASK-10 — CLI de leitura: info, teams, models, render, export; e kit2d_image no ctest

## Goal

A CLI cobre a leitura só pela fachada (`info`, `teams`, `models`, `render --team N --set 1|2 --out PNG`, `export`) e o `ctest` ganha `kit2d_image`, que pula 77 sem `WE2002_KIT2D_IMAGE`/`WE2002_LOOKS_IMAGE`.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/cli.py`
  - `tests/CMakeLists.txt`
  - `tools/kit2d/selftest.py`
- Out:
  - —

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kit2d/cli.py` só importa `core.api` do núcleo
- [ ] `cli.py render --team 1 --set 1 --out <png>` e `--set 2` gravam dois PNGs com sha256 diferentes, colados no Log
- [ ] `ctest --test-dir build -R kit2d_image` passa com a imagem japonesa, e sem a variável pula imprimindo por quê (as duas saídas no Log)

## Notes

—

## Log de Execução
