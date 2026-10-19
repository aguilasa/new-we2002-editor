---
id: K2D-TASK-12
---

# K2D-TASK-12 — Confronto 1: render contra o quadro do emulador, com controle negativo

## Goal

O item 1 do [§5](/docs/PLAN-KIT2D-PY.md#5): no state da §4.4, a caixa do uniforme lida do emulador contra `api.render` do mesmo time, por histograma e pixel a pixel; outro time e outro modelo têm de divergir. O `ctest` ganha `kit2d_live` com `RESOURCE_LOCK duckstation`.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/confront.py`
  - `tools/kit2d/oracle.py`
  - `tests/CMakeLists.txt`
- Out:
  - —

## Done criteria

- [ ] `confront.py --render` imprime a nota do time do state e a dos dois controles, coladas no Log; o time passa e os controles reprovam
- [ ] `ctest --test-dir build -R kit2d_live` passa com o state, e pula 77 imprimindo por quê sem ele
- [ ] a definição de pronto 2 do [§0](/docs/PLAN-KIT2D-PY.md#0) diz qual time foi medido (um caso medido não é a regra)

## Notes

Bloqueada até o state existir.

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
