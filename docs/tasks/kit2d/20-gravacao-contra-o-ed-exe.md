---
id: K2D-TASK-20
---

# K2D-TASK-20 — Confronto 2 com o ed.exe: o roteiro tools/par/8.8 como terceiro lado (Linux)

## Goal

No Linux, o roteiro `tools/par/8.8-*.sh` grava a mesma edição pelo `ed.exe` sob Wine no `:98`, e as três cópias batem fora a faixa conhecida.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/confront.py`
  - `tools/par/`
- Out:
  - —

## Done criteria

- [ ] `confront.py --ed` imprime o `cmp` das três cópias, colado no Log
- [ ] o controle positivo (cópia gravada contra a original) mostra a edição, colado no Log
- [ ] nenhuma janela ≥ 900×450 no `:98` antes da corrida (a guarda do `golden_check.sh`)

## Notes

—

## Log de Execução
