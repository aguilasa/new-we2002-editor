---
id: KRP-TASK-01
---

# KRP-TASK-01 — Leitor puro core/replay.py: Capture v0→v1, Frame, Figure e Walk, com os casos sintéticos migrados

## Goal

Existe `tools/kits/core/replay.py`, o leitor puro de captura de replay: `Capture.load` (com migração do schema v0 das capturas de hoje para o v1), `Frame`, `Figure` (com `sections`, `panel`, `pose`, `box`), `Walk.load` e os juízes `judge`/`judge_walk`, sem emulador e sem `tools/looks/oracle`. É o código que o `oracle.py` passa a importar na KRP-TASK-02.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/replay.py` (novo)
  - `tools/kits/selftest.py` (os casos sintéticos de `oracle --replay` e `--replay-field` migram para o leitor)
  - `tools/kits/controls.py`
- Out:
  - `tools/kits/oracle.py` (o move é a KRP-TASK-02)
  - a linha de comando (KRP-TASK-04)

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kits/core/replay.py` não lista `tools.looks.oracle` nem `oracle`, nem `fork`/`mcp`
- [ ] `python3 tools/kits/selftest.py`: os casos sintéticos de replay passam a nomear `core/replay` e saem `ok`; nenhum caso existe duplicado (contagem de casos de replay igual antes e depois, colada no Log)
- [ ] `Capture.load` lido sobre as sete capturas de `work/kits-oracle/` (cinco de perto, dois laços) devolve `schema` 1 e as chaves fixas do [§2.1](/docs/PLAN-KITS-REPLAY.md#2.1); o sha256 de cada captura vai no Log
- [ ] uma planta (captura com chave faltando) faz o `Capture.load` recusar com mensagem que nomeia a chave, vista vermelha no `controls.py`
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Pontos de partida no `oracle.py`: `_restore_samples`, `replay_figures`, `replay_focus`, `field_focus`, `section_samples`, `panel_samples`, `figure_tag`, `replay_judge`, `replay_field_judge`. Nesta task o código pode ser escrito a partir delas; a remoção do oracle é a 02, e as duas juntas não podem deixar cópia. Armadilha K1: o esperado é constante por (slot, foco).

## Log de Execução
