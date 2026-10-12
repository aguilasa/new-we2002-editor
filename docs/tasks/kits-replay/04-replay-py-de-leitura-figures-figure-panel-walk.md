---
id: KRP-TASK-04
---

# KRP-TASK-04 — replay.py de leitura: figures, figure, panel, walk e describe com --json kits-replay/1, e o alvo kits_replay

## Goal

Existe a linha de comando `tools/kits/replay.py` com os leitores `figures`, `figure [--on-axis|--nearest|--nth N] [--section S]`, `panel`, `walk` e `describe`, todos com `--json` no schema `kits-replay/1`, e o alvo `ctest` `kits_replay` do [§2.6](/docs/PLAN-KITS-REPLAY.md#2.6).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (novo)
  - `tools/kits/core/replay.py`
  - `tests/CMakeLists.txt` (alvo `kits_replay`)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - `show`, `confront` (KRP-TASK-05/06)
  - `capture` (KRP-TASK-07)

## Done criteria

- [ ] `python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --json`: o objeto tem `"schema": "kits-replay/1"` e reproduz campo a campo a linha `ok` de `oracle.py --replay 9 --focus 3 --frame-json …` (raiz 2, cabeça 46, faixa 90 no lugar da 4, pose parada, painel (640, 60, 104), número 11); o mesmo nas outras quatro capturas de perto, cada `$` no Log
- [ ] `replay.py figure work/kits-oracle/replay-9-3.json --section 90 --json` devolve a seção 90 com CLUT (0,487) e página (640,256), como o [item 4](/docs/KITS-REPLAYS-9-10.md#4)
- [ ] `replay.py walk work/kits-oracle/replay-field-9-capture.json --json` devolve os 25 focos da tabela do [item 7](/docs/KITS-REPLAYS-9-10.md#7), com 20 de linha e 2 goleiros
- [ ] `kits_replay` visto saindo 77 (*skipped*) sem `WE2002_KITS_REPLAY_DIR`, e vermelho com uma captura de digest trocado (planta no `controls.py`)
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

O schema é contrato com agente: chaves fixas, sem campo opcional que some. Saída humana curta por padrão. A contagem de alvos `kits` vive só no §9 do plano; ao criar o alvo, varra quem repetia "4/4" (perfil, plano) na mesma task.

## Log de Execução
