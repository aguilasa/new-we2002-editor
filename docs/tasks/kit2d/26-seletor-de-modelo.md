---
id: K2D-TASK-26
---

# K2D-TASK-26 — Seletor de modelo: os 190 com miniatura na paleta do time e os times que usam

## Goal

A lista dos 190 modelos, cada um com miniatura por `api.render_model` na paleta do time corrente e os times que o usam; escolher troca o ponteiro no `Edit`.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui/app.py`
  - `tools/kit2d/ui/i18n.py`
- Out:
  - —

## Done criteria

- [ ] a lista tem 190 itens, contagem colada do `ui_check.py`
- [ ] escolher um modelo e Aplicar grava 4 bytes em +225808; `cmp -l` no Log

## Notes

—

## Log de Execução
