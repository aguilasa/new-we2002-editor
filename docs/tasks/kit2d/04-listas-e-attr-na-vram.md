---
id: K2D-TASK-04
---

# K2D-TASK-04 — O que delimita uma lista, o que é attr e onde u,v caem na VRAM

## Goal

As hipóteses do [§4.2](/docs/PLAN-KIT2D-PY.md#4.2) testadas no emulador: a regra que delimita uma lista, o que o `FF` do byte baixo de `attr` marca, se o byte alto é o índice de CLUT (linha da VRAM em y ≥ 480) e onde as imagens 22/23/24 caem na VRAM. Veredito escrito no §4.2 com a corrida que o sustenta, e também a resposta da [§4.5](/docs/PLAN-KIT2D-PY.md#4.5).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/oracle.py`
  - `tools/kit2d/core/layout.py`
  - `docs/PLAN-KIT2D-PY.md`
- Out:
  - o compositor (K2D-TASK-09)

## Done criteria

- [ ] `oracle.py --lists` imprime, para os dois uniformes do state, a lista que o jogo usa (registros e fim), colada no Log
- [ ] `oracle.py --clut` imprime a linha da VRAM onde a paleta de +172096 do time cai e o byte alto que a escolhe
- [ ] controle: `write_memory` num `x` de um registro move o sprite na captura; a diferença de pixels antes/depois vai no Log
- [ ] o §4.2 do plano diz o veredito e remete ao comando, sem número reescrito à mão

## Notes

Bloqueada até o state existir.

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
