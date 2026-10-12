---
id: KRP-TASK-10
---

# KRP-TASK-10 — Cabeça pela tupla do jogador no scene_of e no match_scene, no CLI e na aba

## Goal

`core/figure.py:scene_of` e `match_scene` aceitam a tupla do jogador no lugar de `TUPLE = assembly.CORPUS_REFERENCE`, e o CLI e a aba ganham a opção; a cabeça desenhada segue a regra medida na KRP-TASK-09, e só ela.

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
  - o seletor de jogador real (KRP-TASK-17)
  - o goleiro (KRP-TASK-12)

## Done criteria

- [ ] sem a opção, o digest da figura é o mesmo de antes da task (default `CORPUS_REFERENCE`)
- [ ] com a tupla do Bokšić e a do Balaban, a seção da cabeça e a CLUT amostrada batem com as da captura (`replay.py figure … --section 46 --json`)
- [ ] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite)
- [ ] texto novo da aba nas duas línguas do `i18n.py`, e o `kits_ui` cobre a opção com uma planta
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Se a KRP-TASK-09 fechou só parte da regra, desenha-se só essa parte, e o resto fica no default — escrito no §3.2.

## Log de Execução
