---
id: KRP-TASK-24
---

# KRP-TASK-24 — A pele do corpo segue a Cor da Pele do painel da cabeça

## Goal

Na figura da aba, trocar a Cor da Pele no painel da cabeça muda também a pele do corpo (braços, pernas, mãos), pela regra que o ciclo `looks` mediu na `LOOKS SET`, como o [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3) decide.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py` (`scene_of` monta a figura com o `skin_colour` do jogador)
  - `tools/kits/ui_check.py` (o `player_judge` exige o corpo diferente entre duas peles, com planta)
  - `tools/kits/selftest.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.3: a decisão)
- Out:
  - o `match_scene` (a aba não o desenha; §3.3)
  - cabelo e barba: só a cabeça os tem

## Done criteria

- [ ] sem a opção, o digest de `cli.py figure` é o de antes da task
- [ ] `cli.py figure … --player D-L3-H-A-A` contra `--player A-L3-H-A-A`: toda primitiva fora da cabeça que muda de CLUT desce 3 linhas, e alguma muda, impresso por comando versionado
- [ ] o `kits_ui` exige o corpo (abaixo da cabeça) diferente entre as duas peles, e a planta que monta o corpo na pele de referência fica vermelha
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Decisão do usuário (2026-10-16), vendo o painel da KRP-TASK-22: "se mudar a cor da cabeça, tem que mudar a cor do corpo". Revoga, na aba, o "inclusive a pele do corpo" do §3.2.

## Log de Execução
