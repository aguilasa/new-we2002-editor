---
id: KRP-TASK-17
---

# KRP-TASK-17 — Jogador real no seletor: time, jogador, número, capitão, cabeça, goleiro e manga

## Goal

A aba e o CLI escolhem time e jogador, e daí saem número, capitão (faixa), cabeça, figura de linha ou goleiro e a manga; o que ainda não se lê do disco no `tools/kits` (elenco, número, capitão) sai dos `OFS_*` já mapeados, pelo caminho do `gen_tables.py`, sem tocar `src/`.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/teams.py`
  - `tools/kits/gen_tables.py` (se o elenco vier por geração)
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui/i18n.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - `src/`
  - a vista dos dois times (KRP-TASK-18)

## Done criteria

- [ ] escolhendo Croácia e o nº 11, a figura sai com a faixa, a cabeça 46 e o painel (640, 60, 104) que a captura `replay-9-3.json` diz; escolhendo Brasil e o nº 1, o goleiro família 13 com a 92
- [ ] `gen_tables.py --check` (alvo `kits_gen`) continua verde, se a geração mudou
- [ ] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite)
- [ ] texto novo nas duas línguas, e o `kits_ui` cobre os seletores com planta
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

A forma exata da leitura do elenco se decide aqui; registre no §6 do plano.

## Log de Execução
