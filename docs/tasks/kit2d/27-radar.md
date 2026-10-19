---
id: K2D-TASK-27
---

# K2D-TASK-27 — Radar: as 8 cores e o aviso da regra de pareamento

## Goal

As 8 cores do radar como botões e o aviso de pareamento do SimoSapo — aviso, não recusa.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui/app.py`
  - `tools/kit2d/ui/i18n.py`
- Out:
  - —

## Done criteria

- [ ] escolher uma cor e Aplicar grava 2 bytes em +0x3F534 ou +0x3F634; `cmp -l` no Log
- [ ] um par proibido mostra o aviso e grava assim mesmo, capturado

## Notes

—

## Log de Execução
