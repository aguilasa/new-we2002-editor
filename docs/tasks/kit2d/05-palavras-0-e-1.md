---
id: K2D-TASK-05
---

# K2D-TASK-05 — Palavras 0 e 1 da paleta: o que os sprites amostram

## Goal

Medido contra a VRAM, por índice, que índices da paleta os sprites do uniforme amostram, se o 0 é transparência e se o 1 (`0x0842`) aparece — o que decide a caixa da palavra 1 do [§3.4](/docs/PLAN-KIT2D-PY.md#3.4).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/oracle.py`
  - `docs/PLAN-KIT2D-PY.md`
- Out:
  - o render (fase 1)

## Done criteria

- [ ] `oracle.py --indices` imprime a contagem de pixels por índice 0..15 nos dois uniformes do state, colada no Log
- [ ] controle: trocar a palavra 1 na RAM e recapturar muda (ou não muda) pixels, com a contagem no Log
- [ ] o §4.3 do plano registra o veredito e remete ao comando

## Notes

State: `work/kit2d-states/SLPM-87056_1.sav`, gravado em 2026-10-21; o que ele mostra está em [KIT2D-STATES.md](/docs/KIT2D-STATES.md).

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
