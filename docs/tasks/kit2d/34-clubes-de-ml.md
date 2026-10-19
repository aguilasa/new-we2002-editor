---
id: K2D-TASK-34
---

# K2D-TASK-34 — Clubes de ML conferidos no emulador

## Goal

Um clube de índice ≥ 63 conferido no emulador, na tela de seleção de clube, contra o render; o §4.6 diz o veredito.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/oracle.py`
  - `docs/PLAN-KIT2D-PY.md`
- Out:
  - —

## Done criteria

- [ ] `confront.py --render` sobre o clube medido, nota e controle colados no Log
- [ ] o §4.6 do plano registra o veredito e diz que é um clube medido, não todos

## Notes

Bloqueada até o state existir; pode precisar de um segundo state na tela de clube, e então o Log diz qual.

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
