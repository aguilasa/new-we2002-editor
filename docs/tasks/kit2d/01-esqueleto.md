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
  - `docs/tasks/kit2d/07-origem-e-times.md` (nota do pacote `core` duplicado)
- Out:
  - render, sprites e escrita (fases 1 e 3)

## Done criteria

- [x] `python3 tools/kit2d/selftest.py` sai 0 e a última linha diz quantos checks rodaram
- [x] uma planta (um `import PySide6` dentro de `tools/kit2d/core/`) faz o selftest sair vermelho, visto no Log
- [x] uma segunda planta (um endereço literal do §1.1 fora de `layout.py`) também o derruba, visto no Log
- [x] `ctest --test-dir build -R kit2d_selftest` passa, sem *skipped*

## Notes

O `kits_selftest` (`tools/kits/selftest.py`) é o modelo de forma.

## Log de Execução

2026-10-22 — HEAD de trabalho sobre `9507bb0c`.

- `python3 tools/kit2d/selftest.py; echo exit=$?` → última linha `kit2d_selftest: 12 check(s) ran, 0 failure(s)`, `exit=0`. Os 12: `tools/pes2/selftest.py` sai 0 (o `iso.py`), `lzss.check_block_literal()` e um round trip `compress`/`decompress`, `tools/kits/gen_tables.py --check` sai 0 e `TEAM_COUNT == 95` (o `teams.py`), `layout.self_check()` e a base marcada `inferred`, as duas regras, e cada regra plantada numa pasta temporária ficando vermelha.
- Planta 1, na árvore real: `echo 'import PySide6' > tools/kit2d/core/plant_qt.py && python3 tools/kit2d/selftest.py --quiet` →
  `FAIL  core/ has no print/exit/input and imports no Qt  [('plant_qt.py', 1, 'PySide6')]`, `kit2d_selftest: 12 check(s) ran, 1 failure(s)`, `exit=1`. Arquivo removido.
- Planta 2: `echo 'RADAR = 0x3F534' > tools/kit2d/plant_addr.py && python3 tools/kit2d/selftest.py --quiet` →
  `FAIL  no address of section 1.1 is spelled outside layout.py  [('plant_addr.py', 1, '0x3F534')]`, `1 failure(s)`, `exit=1`. Removido; a corrida seguinte volta a `0 failure(s)`, `exit=0`.
- `cmake -S . -B build && ctest --test-dir build -R kit2d_selftest` → `1/1 Test #23: kit2d_selftest ...   Passed    9.33 sec`, sem *skipped*. Timeout 120 s (≥ 1,5× os ~9,3 s medidos).
- Gate do perfil com o ambiente: `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kit2d` → `100% tests passed, 0 tests failed out of 1`; é o único alvo `kit2d` que existe.
- Regra do `layout.py` (Fase 0 do perfil): `grep -rnE '172096|225808|0x3F534' tools/kit2d --include='*.py'` lista só `core/layout.py` (linhas 27, 35, 66) e a planta do `selftest.py:196`.
- O endereço que a regra varre é `layout.ADDRESSES` (offsets, faixa dos ponteiros e base); os LBAs ficam fora de propósito — 850 ou 1050 são tão prováveis como largura de janela quanto como setor, e os arquivos se leem pelo caminho.
- Os dois pacotes chamam-se `core`: o do `kits` entra como `kits_core` por `importlib`. Nota deixada na K2D-TASK-07, que vai precisar do mesmo.
- O terceiro gate do perfil (`tools/kit2d/controls.py`) sai 2 — o arquivo nasce na K2D-TASK-16, e o perfil o marca "desde a K2D-TASK-16".
