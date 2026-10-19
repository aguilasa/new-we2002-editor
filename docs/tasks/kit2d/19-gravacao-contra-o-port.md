---
id: K2D-TASK-19
---

# K2D-TASK-19 — Confronto 2: a mesma edição de paleta pela ferramenta e pelo Database::Save

## Goal

O item 2 do [§5](/docs/PLAN-KIT2D-PY.md#5): um time, uma palavra, um valor, feitos por `cli.py set-palette … apply` e pelo `we2002_golden_tool` sobre duas cópias, dão imagens byte-idênticas fora a faixa 405724..405739.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/confront.py`
  - `tests/golden_tool.cpp`
- Out:
  - —

## Done criteria

- [ ] `confront.py --port` imprime `cmp` das duas cópias: só a faixa conhecida, colado no Log
- [ ] controle: valor diferente num lado faz o confronto reprovar, visto vermelho
- [ ] a definição de pronto 4 do [§0](/docs/PLAN-KIT2D-PY.md#0) diz qual time e palavra foram medidos

## Notes

Se o `golden_tool` não aceitar edição de paleta, a mudança nele entra declarada nesta task.

## Log de Execução
