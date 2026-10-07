---
id: CORR-KITS-065
---

# CORR-KITS-065 — Mover RESET_TURN para que a docstring de DIAG_NOTE fique sob a constante dela

Origin: [KITS-TASK-37](/docs/tasks/concluidos/kits/37-reset-e-dica-das-costas.md)

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

Reproduzido em 2026-10-05 sobre `30c4fcc`: `sed -n 138,144p tools/kits/ui_check.py` mostra
`RESET_TURN` e a docstring dela entre a tupla e a explicação de `DIAG_NOTE`.

Conserto: as duas linhas de `RESET_TURN` foram movidas para baixo da docstring de `DIAG_NOTE`. A
docstring delas já cita `--double-click` (CORR-KITS-064).

```text
$ sed -n 138,145p tools/kits/ui_check.py
STYLE, HOVER, FIGURE, OFF, SELECTOR, DIAG, DIAG_NOTE, RESET = (
    "style", "hover", "3D", "3D off", "selector", "diagnosis", "diagnosis note", "reset")
"""DIAG_NOTE is the Diagnosis judge on the note rows: only the European
Deluxe TEX_13 makes one, so its plant is judged only with ED_VARIABLE set
and says it was not judged otherwise (CORR-KITS-061)."""
RESET_TURN = ("--yaw", "0", "--pitch", "30")
"""A turn away from the opening one, which --reset and --double-click have to undo
(KITS-TASK-37, CORR-KITS-064)."""
```

Só muda a ordem de declaração. O módulo continua compilando (`ast.parse` ok) e o `kits_ui` passa
(ver o commit da correção).
- **Closed** — commit `6ee6dc4` (2026-10-05): style(kits): RESET_TURN below the DIAG_NOTE docstring it had split off
  - Files (`git show --name-status 6ee6dc4`):
    - `M docs/tasks/kits/CORR-KITS-065.md`
    - `M tools/kits/ui_check.py`
