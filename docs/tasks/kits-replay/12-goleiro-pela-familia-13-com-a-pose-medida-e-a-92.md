---
id: KRP-TASK-12
---

# KRP-TASK-12 — Goleiro pela família 13, com a pose medida e a 92

## Goal

A figura de goleiro da aba e do CLI é a família 13 do `MODEL.BIN` (torso 13, braços 14/16 e 15/17, pernas 18/20/19/21, a 11, cabeça do jogador), com a 92 no lugar da 15 quando capitão, posada pela pose de `work/kits-pose/slot9-keeper-front.json` promovida a arquivo versionado do núcleo. A reabertura da K3D-TASK-10 fica escrita datada no plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/core/keeper_pose.json` (novo, a pose promovida)
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§4)
- Out:
  - a pose de corrida (KRP-TASK-15)
  - faixa e manga do jogador de linha

## Done criteria

- [ ] a ordem de seções desenhada do goleiro é `34 13 14 16 92 17 18 20 11 19 21` com faixa e com a 15 no lugar da 92 sem, como o [item 3](/docs/KITS-REPLAYS-9-10.md#3); impressa por uma opção versionada
- [ ] nenhum UV ou vértice escrito à mão: toda seção vem do `MODEL.BIN` (grep no diff, e o Log diz de onde)
- [ ] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite), no Marcos dos slots 9 e 10
- [ ] o `kits_ui` cobre o goleiro novo com uma planta (o corpo do `EDT_MOD.BIN` de volta fica vermelho)
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Decisão do usuário (2026-10-12): implementar. A pose sai de `work/` para o núcleo com o digest no Log.

## Log de Execução
