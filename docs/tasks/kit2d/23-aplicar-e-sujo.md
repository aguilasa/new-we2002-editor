---
id: K2D-TASK-23
---

# K2D-TASK-23 — Aplicar, Cancelar, Reverter este time e a guarda de sujo

## Goal

As edições de cor ficam no `Edit` até Aplicar; Cancelar descarta; trocar de time ou fechar com sujo pergunta.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui/app.py`
  - `tools/kit2d/ui/i18n.py`
- Out:
  - —

## Done criteria

- [ ] dirigido no `:98`: editar uma cor e Aplicar grava a cópia; `cmp -l` contra o original lista os bytes, colado no Log
- [ ] editar e trocar de time abre a pergunta; Cancelar não grava nada (sha256 igual no Log)

## Notes

—

## Log de Execução
