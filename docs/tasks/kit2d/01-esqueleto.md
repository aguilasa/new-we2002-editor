---
id: K2D-TASK-01
---

# K2D-TASK-01 — Esqueleto de tools/kit2d/: layout.py, selftest.py e kit2d_selftest no ctest

## Goal

Existe `tools/kit2d/` com `core/layout.py` concentrando todo endereço do [§1.1](/docs/PLAN-KIT2D-PY.md#1.1) (LBAs, +172096, +225808, +0x3F534/+0x3F634, os três streams do `DATSEL.BIN`, a base de carga marcada "inferida"), `core/errors.py` com a exceção tipada do núcleo, e `selftest.py` que roda os self-checks do que o projeto importa (`tools/pes2/iso.py`, `lzss.py`, `tools/kits/core/teams.py`) e as regras de desenho do [§3.1](/docs/PLAN-KIT2D-PY.md#3.1); o `ctest` ganha `kit2d_selftest`, que nunca pula.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/__init__.py`
  - `tools/kit2d/core/layout.py`
  - `tools/kit2d/core/errors.py`
  - `tools/kit2d/selftest.py`
  - `tests/CMakeLists.txt`
- Out:
  - render, sprites e escrita (fases 1 e 3)

## Done criteria

- [ ] `python3 tools/kit2d/selftest.py` sai 0 e a última linha diz quantos checks rodaram
- [ ] uma planta (um `import PySide6` dentro de `tools/kit2d/core/`) faz o selftest sair vermelho, visto no Log
- [ ] uma segunda planta (um endereço literal do §1.1 fora de `layout.py`) também o derruba, visto no Log
- [ ] `ctest --test-dir build -R kit2d_selftest` passa, sem *skipped*

## Notes

O `kits_selftest` (`tools/kits/selftest.py`) é o modelo de forma.

## Log de Execução
