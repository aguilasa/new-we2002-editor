---
id: KRP-TASK-05
---

# KRP-TASK-05 — show --png e confront puro sobre a captura

## Goal

`replay.py show <captura> --png out.png [--section S|--box]` põe o recorte do frame buffer do jogo ao lado da figura desenhada pelo `core/raster` na pose capturada, sem Qt; `replay.py confront <captura> [--section S]` dá, por seção, o pixel do jogo contra o texel puro e o modulado.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - `confront --tab` (KRP-TASK-06)
  - qualquer mudança em `core/raster.py`

## Done criteria

- [ ] `replay.py confront work/kits-oracle/replay-9-3.json --section 90 --json`: `far` puro 2,27 contra modulado 2,55, como o [item 1](/docs/KITS-REPLAYS-9-10.md#1)
- [ ] `replay.py show work/kits-oracle/replay-9.json --png <scratch>/show.png` escreve um PNG com as duas metades; o Log traz o tamanho e o digest, e o PNG é enviado ao usuário
- [ ] planta: o `show` desenhando a figura sem a pose capturada fica vermelho no `controls.py`
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

O PNG é para olhar; o número de fidelidade é o do `confront`.

## Log de Execução
