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

**Reprodução (2026-10-25, HEAD `b940a91c`).** O `rite reproduce` não decide (o comando da Evidência tem
o marcador `<japonesa>` e sai com erro de shell); rodado aqui com uma cópia de
`roms/japanese-shift-jis.bin` no scratchpad no lugar dele: REPRODUCED.

```text
$ WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 -c "…" 2>&1 | grep -E 'Traceback|Fail|FAILED'; echo "exit=${pipestatus[1]}"
Traceback (most recent call last):
    raise Fail("a game controller is plugged in (%s): the fork's [Pad1] "
duckmcp.errors.Fail: a game controller is plugged in (js0): the fork's [Pad1] is SDL-0 and reads it on any display, so its buttons reach the game under test -- unplug or switch it off and run again
exit=1
```

**Conserto.**

- `tools/kits/oracle.py`: o corpo do `main` virou `_main`, e o `main` o envolve como o do
  `looks/oracle.py`: `Skip` dá `oracle: skipped -- …` e 77; `Fail`, `NotRunning` e `ToolError` (e por
  herança `SessionLost`) dão `oracle FAILED: <Tipo>: …` em stderr e 1. Importa `Fail, NotRunning, Skip,
  ToolError` de `duckmcp.errors`.
- `tools/kits/selftest.py` (declarado com `rite set`): no `_oracle_checks`, o `_main` é trocado por um
  que levanta cada um dos cinco tipos, e o check exige o código e o nome na saída; `contextlib` subiu
  para os imports do topo.

**Controle** — o `except (Fail, NotRunning, ToolError)` tirado numa cópia de `tools/` (HEAD + os dois
arquivos consertados) no scratchpad:

```text
$ (cd $T && python3 tools/kits/selftest.py 2>&1 | grep -E "oracle main|kits_selftest:"; echo "exit=${pipestatus[1]}")
  ok    oracle main answers Skip with 77, and names it
  FAIL  oracle main answers Fail with 1, and names it  exit None, said '  FAIL  oracle main under a Fail: raised Fail: planted Fail\n'
  FAIL  oracle main answers NotRunning with 1, and names it  exit None, said '  FAIL  oracle main under a NotRunning: raised NotRunning: planted NotRunning\n'
  FAIL  oracle main answers ToolError with 1, and names it  exit None, said '  FAIL  oracle main under a ToolError: raised ToolError: planted ToolError\n'
  FAIL  oracle main answers SessionLost with 1, and names it  exit None, said '  FAIL  oracle main under a SessionLost: raised SessionLost: planted SessionLost\n'
kits_selftest: 13 failure(s)
exit=1
```

(os outros oito vermelhos são consequência: com a árvore plantada a sandbox dos controles não fica
verde.)

**Verificação** na árvore entregue:

```text
$ WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 -c "…" 2>&1 | grep -E 'Traceback|Fail|FAILED'; echo "exit=${pipestatus[1]}"
oracle FAILED: Fail: a game controller is plugged in (js0): the fork's [Pad1] is SDL-0 and reads it on any display, so its buttons reach the game under test -- unplug or switch it off and run again
exit=1
$ python3 tools/kits/selftest.py 2>&1 | grep -E "oracle main|kits_selftest:"; echo "exit=$?"
  ok    oracle main answers Skip with 77, and names it
  ok    oracle main answers Fail with 1, and names it
  ok    oracle main answers NotRunning with 1, and names it
  ok    oracle main answers ToolError with 1, and names it
  ok    oracle main answers SessionLost with 1, and names it
kits_selftest: 0 failure(s)
exit=0
$ python3 tools/duckmcp/selftest.py 2>&1 | tail -1
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
```
- **Closed** — commit `ffd37e32` (2026-10-25): fix(kits): oracle main answers the lib's errors with an exit code, not a traceback
  - Files (`git show --name-status ffd37e32`):
    - `M docs/tasks/duckmcp/CORR-DMCP-032.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
