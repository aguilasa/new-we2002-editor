---
id: CORR-K3D-021
---

# CORR-K3D-021 — Docstring de EDIT_TURN_STOPS contradiz a corrida medida

Origin: [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md)

## Problem

O docstring de `EDIT_TURN_STOPS`, da [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md), diz que "in slot 8 the per-piece matrix load
stops once the figure has turned". A corrida medida enche as 1200 paradas (99 figuras) e
nunca imprime a linha "stopped firing". O docstring novo de `matrix_stops` repete a
afirmação. O item 5 do G7 diz que a carga parou depois do Cross, não depois do giro.
Também falta o docstring de `EDIT_TURN_WAIT = 20` (linha 2516), contra a armadilha
"constante nova acima da docstring da anterior".

## Evidência

```text
$ grep -n 'once the figure has turned' tools/kits/oracle.py
2515:once the figure has turned."""
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edit-number 8 --frame-json work/kits-oracle/edit-8-0.json | grep -E 'stopped firing|^  turn: '
  turn: 1200 stop(s), 99 whole figure(s); ...
  turn: every figure's translations within 142 to 193 of its ...
```

Nenhuma linha "stopped firing".

## Root cause

O docstring foi escrito a partir de uma corrida anterior, com Cross primeiro, e não foi
atualizado quando `EDIT_BUTTONS` foi reordenado.

## Fix

Reescrever os docstrings de `EDIT_TURN_STOPS` e de `matrix_stops` em
`tools/kits/oracle.py` com o que foi medido — depois do Circle a carga continua pelas
1200 paradas — e, no mesmo commit, pôr o docstring que falta sob `EDIT_TURN_WAIT = 20`.

## Arquivos a criar ou modificar

- tools/kits/oracle.py

## Verificação

```sh
grep -n 'once the figure has turned' tools/kits/oracle.py
grep -n -A1 '^EDIT_TURN_WAIT' tools/kits/oracle.py
```

O primeiro não pode imprimir nada; o segundo tem de mostrar uma linha de docstring.

## Log de Execução

- 2026-10-09 — triagem inline: **REPRODUCED**. `oracle.py:2515` dizia "once the figure has turned";
  a corrida sobre `edit-8-0.json` dá `turn: 1200 stop(s), 99 whole figure(s)` e nenhuma linha
  "stopped firing".
- `oracle.py`: docstrings de `EDIT_TURN_STOPS` e de `matrix_stops` dizem o medido (depois do Circle a
  carga continua pelas 1200 paradas); `EDIT_TURN_WAIT` ganhou docstring (20 s, mais curto que o
  `WATCH_SECONDS` de 90 do oráculo do `looks`).
- Verificação: `grep -n 'once the figure has turned'` não imprime nada; `grep -n -A1
  '^EDIT_TURN_WAIT'` mostra a linha de docstring.
- **Closed** — commit `aaa781b` (2026-10-09): docs(kits): say the matrix load keeps firing after Circle in slot 8
  - Files (`git show --name-status aaa781b`):
    - `M docs/tasks/kits-3d/CORR-K3D-021.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`
