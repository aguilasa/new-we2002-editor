---
id: K3D-TASK-10
---

# K3D-TASK-10 — Seletor só com player e goalkeeper, vestidos pela regra medida

## Goal

O seletor de figura tem só **player** e **goalkeeper**; a figura de partida sai da interface, e a braçadeira e a manga longa passam a vestir as duas figuras pela regra da K3D-TASK-07.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G3: decisão reaberta da KITS-TASK-47, datada)
- Out: remapear UV à mão (§0)

## Done criteria

- [ ] `figure_box` tem 2 itens; `kits_ui` afirma, e a planta que devolve o terceiro fica vermelha
- [ ] com braçadeira ou manga longa marcadas, a figura continua a do `EDT_MOD.BIN` (o `kits_ui` compara a silhueta sem as caixas)
- [ ] a regra da K3D-TASK-07 é a única fonte da geometria nova (citada no código pela constante e em G3)
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução
