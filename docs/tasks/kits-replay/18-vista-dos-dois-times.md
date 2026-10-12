---
id: KRP-TASK-18
---

# KRP-TASK-18 — Vista dos dois times

## Goal

A aba mostra dois jogadores, um de cada time, cada um com o seu kit e a sua paleta, como o jogo os tem lado a lado na VRAM ([item (e)](/docs/KITS-REPLAYS-9-10.md#e-dois-kits-na-vram-ao-mesmo-tempo-e-o-kit-pela-paleta)).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`
  - `tools/kits/ui/figure_view.py`
  - `tools/kits/ui/i18n.py`
  - `tools/kits/cli.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/controls.py`
- Out:
  - formato novo

## Done criteria

- [ ] com Brasil × Croácia, cada figura amostra a paleta do seu kit (`TEX` do Brasil e `TEX_22`), conferido por opção versionada
- [ ] com uma figura só, o digest é o de antes da task
- [ ] texto novo nas duas línguas, e o `kits_ui` cobre a vista com planta
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes



## Log de Execução
