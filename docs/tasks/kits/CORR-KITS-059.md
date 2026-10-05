---
id: CORR-KITS-059
---

# CORR-KITS-059 — Dizer no Log que as linhas do emulador não foram refeitas, ou colar a corrida

Origin: [KITS-TASK-32](/docs/tasks/kits/32-fechamento-fase-8.md)

## Problem

O Log da KITS-TASK-32 diz "As verificações da fase 8 do perfil, refeitas" e lista "proveniência e as conferências no emulador" com `gen_tables.py --report` como evidência. O `--report` só imprime as linhas estáticas de `TEAM_KIT_EMULATOR` do módulo gerado e nunca sobe o emulador: a task de fechamento não refez as conferências no emulador que diz ter refeito. As linhas continuam valendo — o revisor as refez no fork e as duas corridas do `oracle.py` passam.

## Evidência

```text
$ grep -n "def report" -A15 tools/kits/gen_tables.py | grep -n "EMULATOR\|oracle\|mcp\|fork"
314-          % (len(table.TEAM_KIT), len(table.TEAM_KIT_EMULATOR),
316-                       for i in sorted(table.TEAM_KIT_EMULATOR)),
$ grep -n "refeitas" docs/tasks/kits/32-fechamento-fase-8.md
40:As verificações da fase 8 do perfil, refeitas:
$ grep -c "oracle.py --slot" docs/tasks/kits/32-fechamento-fase-8.md
0
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 tools/kits/oracle.py --slot 4 --expect 00=1 --expect 41=1
ok    TEX_00 in set 1, TEX_41 in set 1          (rc=0)
$ ... python3 tools/kits/oracle.py --slot 3 --expect 01=1 --expect 13=2
ok    TEX_01 in set 1, TEX_13 in set 2          (rc=0)
```

## Root cause

Hipótese: quem fechou tratou a tabela que registra as medições do emulador como se fosse medição nova.

## Fix

Em `docs/tasks/kits/32-fechamento-fase-8.md`, ou dizer que as linhas do emulador são as registradas pelas KITS-TASK-30/31 e foram só contadas, ou colar as duas corridas `oracle.py --slot` acima como remedição.

## Arquivos a criar ou modificar

- `docs/tasks/kits/32-fechamento-fase-8.md`

## Verificação

`grep -c "oracle.py --slot" docs/tasks/kits/32-fechamento-fase-8.md` dá 0 hoje; depois do conserto, ou mostra a corrida refeita, ou o Log deixa de dizer que as conferências no emulador foram refeitas.

## Log de Execução

Reproduzido em 2026-10-04 sobre `6e0fd6f` (`rite reproduce CORR-KITS-059 --cycle kits`): o
`--report` só toca `TEAM_KIT_EMULATOR`, e o Log da task 32 diz "refeitas" sem nenhuma corrida
do `oracle.py`:

```text
$ grep -n "def report" -A15 tools/kits/gen_tables.py | grep -n "EMULATOR\|oracle\|mcp\|fork"
11:314-          % (len(table.TEAM_KIT), len(table.TEAM_KIT_EMULATOR),
13:316-                       for i in sorted(table.TEAM_KIT_EMULATOR)),
$ grep -c "oracle.py --slot" docs/tasks/kits/32-fechamento-fase-8.md
0
```

O quinto comando da Evidência (`... python3 tools/kits/oracle.py --slot 3 ...`) é placeholder e
sai 127 no reproduce; rodado por extenso abaixo.

Conserto: no Log da task 32 o `--report` passa a se dizer contagem das linhas registradas pelas
KITS-TASK-30/31, e as duas conferências no emulador entram refeitas, com a variável de ambiente:

```text
$ export WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
$ python3 tools/kits/oracle.py --slot 4 --expect 00=1 --expect 41=1 2>&1 | tail -1
  ok    TEX_00 in set 1, TEX_41 in set 1
$ python3 tools/kits/oracle.py --slot 3 --expect 01=1 --expect 13=2 2>&1 | tail -1
  ok    TEX_01 in set 1, TEX_13 in set 2
```

Saída 0 nas duas. Verificação:
```text
$ grep -c "oracle.py --slot" docs/tasks/kits/32-fechamento-fase-8.md
2
```
- **Closed** — commit `864cb9d` (2026-10-04): docs(kits): task 32 log reruns the two emulator checks
  - Files (`git show --name-status 864cb9d`):
    - `M docs/tasks/kits/32-fechamento-fase-8.md`
    - `M docs/tasks/kits/CORR-KITS-059.md`
