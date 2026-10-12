---
id: KRP-TASK-15
---

# KRP-TASK-15 — Posar as famílias 2 e 13 pela corrida do arquivo, com seletor de caminhada ou corrida

## Goal

A aba e o CLI posam o jogador de linha e o goleiro pela corrida medida na KRP-TASK-14 (ou pela pose capturada versionada, se ela deu negativa), com um seletor de pose caminhada/corrida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui/i18n.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - câmera em perspectiva (KRP-TASK-20)

## Done criteria

- [ ] com pose corrida, as matrizes das peças da família 2 e da 13 batem com as das poses de `work/kits-pose/` dentro do erro que a 14 registrou, impresso por opção versionada
- [ ] com pose caminhada, o digest é o de antes da task
- [ ] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite)
- [ ] texto novo nas duas línguas, e o `kits_ui` cobre o seletor com planta
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes



## Log de Execução
