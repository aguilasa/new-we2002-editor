---
id: CORR-DMCP-032
---

# CORR-DMCP-032 — O main do kits/oracle.py deixa Fail sair como traceback

Origin: [DMCP-TASK-25](/docs/tasks/duckmcp/25-kits-oracle.md)

## Problem

O `main` do `tools/kits/oracle.py` não converte `duckmcp.errors.Fail` em código de saída nem em
uma linha de erro. Desde a DMCP-TASK-25, o `dump_slot` chama `fork.refuse_joysticks()` antes de subir
o fork, e essa guarda levanta `Fail`. Com um controle físico ligado, `--slot N` termina num traceback
inteiro em vez de uma linha `FAIL` e saída 1 — como já fazem o `main` do `looks/oracle.py` (DMCP-TASK-22)
e o do `confront.py` (DMCP-TASK-23).

## Evidência

Controle simulado por monkeypatch (`joysticks` devolve `js0`, `launch` não pode ser alcançado):

```text
$ WE2002_LOOKS_IMAGE=<japonesa> WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 -c "
import sys; sys.path.insert(0,'tools'); sys.path.insert(0,'tools/kits')
from duckmcp import fork
fork.joysticks=lambda root=None: ['js0']
def no(*a,**k): raise SystemExit('launch reached')
fork.launch=no
import oracle
sys.exit(oracle.main(['--slot','1']))
" 2>&1 | grep -E 'Traceback|Fail'; echo "exit=${pipestatus[1]}"
Traceback (most recent call last):
    raise Fail("a game controller is plugged in (%s): the fork's [Pad1] "
duckmcp.errors.Fail: a game controller is plugged in (js0): the fork's [Pad1] is SDL-0 and reads it on any display, so its buttons reach the game under test -- unplug or switch it off and run again
exit=1
```

A saída já é 1 (exceção não tratada), mas pelo traceback, não pelo `main`.

## Root cause

O `main` do `kits` foi escrito antes de a guarda existir no `dump_slot`, e não trata as exceções da
lib.

## Fix

No `main` do `tools/kits/oracle.py`: mapear `Skip` para 77 e `Fail`, `NotRunning` e `ToolError` para
1 com uma linha `oracle FAILED: <Tipo>: …`, como o `looks/oracle.py` faz desde a DMCP-TASK-22, e
afirmar isso no self-check do `kits`.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`

## Verificação

- o comando da Evidência sai 1 com uma linha `FAILED` e sem `Traceback`;
- um check do self-check do `kits` afirma o mapeamento, e uma planta que tira o `except` o deixa
  vermelho;
- `python3 tools/kits/selftest.py` sai 0.

## Log de Execução
