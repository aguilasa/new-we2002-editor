---
id: CORR-KRP-013
---

# CORR-KRP-013 — confront_tab fixa work/venv-looks/bin/python em vez de reusar confront.VENV_PYTHON

Origin: [KRP-TASK-06](/docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

## Problem

`confront_tab` fixa `work/venv-looks/bin/python`. No Windows o interpretador do venv é
`Scripts/python.exe`, então lá o `confront --tab` sai com "no venv python". O arquivo que ele importa,
`tools/kits/confront.py:268`, já tem `VENV_PYTHON`, que trata `os.name == "nt"`. O Objetivo da task
pede reuso do `confront.py`.

## Evidência

```text
$ grep -n 'venv-looks' tools/kits/replay.py tools/kits/confront.py
tools/kits/replay.py:414:    python = os.path.join("work", "venv-looks", "bin", "python")
tools/kits/confront.py:268:VENV_PYTHON = os.path.join("work", "venv-looks",
```

## Root cause

O caminho foi reescrito em vez de importado.

## Fix

Em `confront_tab` (`tools/kits/replay.py`), usar `confront.VENV_PYTHON`.

## Arquivos a criar ou modificar

- `tools/kits/replay.py`

## Verificação

```sh
grep -c '"venv-looks", "bin", "python"' tools/kits/replay.py
```

Hoje dá 1. Depois do conserto tem de dar 0.

## Log de Execução

### 2026-10-15

Reprodução na HEAD `355f3849` (`rite reproduce`, inline):

```text
$ grep -n 'venv-looks' tools/kits/replay.py tools/kits/confront.py
tools/kits/confront.py:268:VENV_PYTHON = os.path.join("work", "venv-looks",
tools/kits/replay.py:414:    python = os.path.join("work", "venv-looks", "bin", "python")
```

Conserto: `confront_tab` passa a usar `confront.VENV_PYTHON`, que já trata `os.name == "nt"`
(`Scripts/python.exe`). O `confront` já estava importado na função (`_kits_confront()`).

```text
$ grep -c '"venv-looks", "bin", "python"' tools/kits/replay.py
0
$ grep -n 'VENV_PYTHON' tools/kits/replay.py
414:    python = confront.VENV_PYTHON
```

O caminho `confront --tab` inteiro, no Linux, é exercitado pela corrida da
[CORR-KRP-012](/docs/tasks/kits-replay/CORR-KRP-012.md), feita sobre este commit. O caminho do
Windows não foi rodado: não há Windows nesta máquina.
- **Closed** — commit `40d610c2` (2026-10-15): fix(kits): confront --tab finds the venv python through confront.VENV_PYTHON
  - Files (`git show --name-status 40d610c2`):
    - `M docs/tasks/kits-replay/CORR-KRP-013.md`
    - `M tools/kits/replay.py`
