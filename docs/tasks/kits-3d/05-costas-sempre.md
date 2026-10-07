---
id: K3D-TASK-05
---

# K3D-TASK-05 — Cópia das costas sempre e conserto do que a contagem achar

## Goal

A cópia medida das costas (`BACK_COPY`) vale sempre, com ou sem Number, e o resto do que a K3D-TASK-04 contar é consertado só com regra medida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py` (a dica `figure_hint`)
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G5: o que foi consertado e o que ficou, com a contagem)
- Out: inventar texel ou geometria (§0)

## Done criteria

- [ ] a ferramenta da K3D-TASK-04 dá 0 px vindos da lacuna do torso, em todo giro, nas duas figuras, sem Number
- [ ] a planta que tira o `BACK_COPY` do caminho sem Number fica vermelha
- [ ] toda falta restante na contagem está listada em G5 com a causa medida, ou zerada
- [ ] `figure_hint` deixa de dizer que as costas saem vazadas, nas duas línguas
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Reabre a decisão de 2026-10-05 (KITS-TASK-37): registrar datada em G5.

## Log de Execução
