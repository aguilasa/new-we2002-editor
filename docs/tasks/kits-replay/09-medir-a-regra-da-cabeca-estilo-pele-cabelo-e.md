---
id: KRP-TASK-09
---

# KRP-TASK-09 — Medir a regra da cabeça (estilo, pele, cabelo e barba) contra o registro do disco nos 22

## Goal

Fica medido se a hipótese (a)+(b) do relatório vale: `replay.py head <captura> [--player <registro>]` decodifica estilo (pela `assembly.HAIR_MAP`, com o *twin* da `FACE_TWINS`), pele, cabelo e barba (pela CLUT, regra do `looks`) e confronta com o registro de 12 bytes do jogador no disco, nos 22 dos dois laços. O resultado — regra que fecha, ou o que não fecha — vai escrito no §3.1 do plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (`head`)
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.1: o resultado)
- Out:
  - o desenho da cabeça (KRP-TASK-10)

## Done criteria

- [ ] `replay.py head work/kits-oracle/replay-field-9-capture.json --player all --json` e o mesmo no `-10-`: por foco, seção, CLUT, estilo/pele/cabelo/barba decodificados e o registro do disco; a linha de resumo diz quantos dos 22 batem, colada no Log
- [ ] as três figuras de perto (`replay-9-3.json`, `replay-10-2.json`, `replay-9.json`) dão o estilo e as colunas da tabela de [(a)](/docs/KITS-REPLAYS-9-10.md#a-cabelo-barba-e-pele-do-jogador-vêm-da-clut-da-cabeça-pela-regra-da-looks-set)
- [ ] o esperado por jogador é constante no código (K1), e uma planta que troca a coluna do cabelo derruba a asserção com dado real (K2)
- [ ] negativa é resultado: o que não bate fica escrito no §3.1 com comando e saída, e não bloqueia a task
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Achar o registro de cada um dos 22 (time e número pelo painel, item 7 do relatório) é parte da medição. Leitura do disco por `tools/looks/looks.py` (`records`, `decode`). Dois slots medidos dizem "nos dois", não "sempre".

## Log de Execução
