---
id: CORR-KITS-065
---

# CORR-KITS-065 — Mover RESET_TURN para que a docstring de DIAG_NOTE fique sob a constante dela

Origin: [KITS-TASK-37](/docs/tasks/kits/37-reset-e-dica-das-costas.md)

## Problem

`RESET_TURN` e a docstring dela foram inseridas entre a tupla `STYLE…DIAG_NOTE` e a string solta que explica `DIAG_NOTE` (CORR-KITS-061). A explicação agora vem depois da docstring de `RESET_TURN`, como string perdida que parece ser dela.

## Evidência

```text
$ sed -n 138,144p tools/kits/ui_check.py
STYLE, HOVER, FIGURE, OFF, SELECTOR, DIAG, DIAG_NOTE, RESET = (
    "style", "hover", "3D", "3D off", "selector", "diagnosis", "diagnosis note", "reset")
RESET_TURN = ("--yaw", "0", "--pitch", "30")
"""A turn away from the opening one, which --reset has to undo (KITS-TASK-37)."""
"""DIAG_NOTE is the Diagnosis judge on the note rows: only the European
Deluxe TEX_13 makes one, so its plant is judged only with ED_VARIABLE set
and says it was not judged otherwise (CORR-KITS-061)."""
```

## Root cause

A constante nova foi inserida logo depois da tupla, acima da docstring que a seguia.

## Fix

Em `tools/kits/ui_check.py`, mover a definição de `RESET_TURN` e a docstring dela para baixo da docstring de `DIAG_NOTE`.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`

## Verificação

`sed -n 138,144p tools/kits/ui_check.py` mostra a string `"""DIAG_NOTE is …"""` logo depois da tupla.

## Log de Execução
