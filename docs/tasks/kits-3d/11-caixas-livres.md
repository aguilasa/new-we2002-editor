---
id: K3D-TASK-11
---

# K3D-TASK-11 — Number, braçadeira e manga longa livres nas duas figuras

## Goal

Number, Captain armband e Long sleeves combinam livremente — nenhuma, uma, duas ou as três — no jogador e no goleiro.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui_check.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G4: decisão reaberta da KITS-TASK-40, datada)
- Out: o que a K3D-TASK-08 não mediu: a caixa fica desligada com a frase, nas duas línguas

## Done criteria

- [ ] `kits_ui` captura as 8 combinações × 2 figuras de costas e afirma que cada caixa muda a captura em todo contexto
- [ ] uma planta por caixa (que a ignora) fica vermelha
- [ ] nenhuma caixa é escondida ou desligada sem medida que justifique
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução
