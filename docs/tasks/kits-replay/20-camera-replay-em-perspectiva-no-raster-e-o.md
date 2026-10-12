---
id: KRP-TASK-20
---

# KRP-TASK-20 — Câmera replay em perspectiva no raster, e o preset na aba

## Goal

O `core/raster.py` ganha projeção perspectiva com H 1376, OFX e OFY 0, e a aba um preset "replay" com a profundidade de frente (4681) e de costas (~4700) e o passo de giro medidos no [item 9](/docs/KITS-REPLAYS-9-10.md#9); a ortográfica continua o default.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/raster.py`
  - `tools/kits/core/figure.py`
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui/i18n.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - andar o replay

## Done criteria

- [ ] com o preset, os pontos projetados das peças na pose de `slot9-keeper-front.json` caem a ~1 px dos do jogo (erro médio impresso por opção versionada, colado no Log)
- [ ] sem o preset, o digest é o de antes; `cli.py holes --tag 00` continua `skipped 0`
- [ ] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite), refeito nas cinco capturas com a câmera nova
- [ ] texto novo nas duas línguas, e o `kits_ui` cobre o preset com planta
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Fica por último porque muda o confronto de todas as tasks anteriores.

## Log de Execução
