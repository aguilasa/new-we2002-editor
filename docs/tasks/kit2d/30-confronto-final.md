---
id: K2D-TASK-30
---

# K2D-TASK-30 — Confronto final: a edição aplicada aparece na tela do emulador

## Goal

Uma cor, um modelo e um pontinho de radar aplicados pela ferramenta numa cópia aparecem no emulador, que bota da cópia e chega à tela de opções — o que torna "grava" mais que "grava bytes" ([§7](/docs/PLAN-KIT2D-PY.md#7)).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/confront.py`
  - `tools/kit2d/oracle.py`
- Out:
  - —

## Done criteria

- [ ] `confront.py --final` imprime, para cor, modelo e radar, o quadro antes e depois e a diferença na caixa, colados no Log
- [ ] controle: a cópia sem edição não difere, visto no Log

## Notes

Bloqueada até o state existir. A rota até a tela a partir do boot da cópia é medida aqui, se o state não servir.

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
