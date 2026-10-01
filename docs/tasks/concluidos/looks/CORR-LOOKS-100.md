---
id: CORR-LOOKS-100
---

# CORR-LOOKS-100 — O selftest do oracle.py grava no slot real do DuckStation no Linux

Origin: [LOOKS-TASK-08](/docs/tasks/concluidos/looks/08-de-onde-vem-o-boneco.md)

## Problem

No Linux, `python3 tools/looks/selftest.py` (e o `ctest -R looks_selftest`)
sai 1 e, pior que o vermelho, **sobrescreve o save state real** do slot 1 do
DuckStation (`~/.local/share/duckstation/savestates/SLPM-87056_1.sav`) com o
state sintético de 478 bytes que o self-check do `oracle.py` forja. Medido em
2026-09-28 na primeira corrida do ciclo no Linux: o arquivo de 1.558.617 B de
2026-09-10 virou 478 B. Só não se perdeu porque havia backup
(`docs/LOOKS-AMBIENTE.md`, passo 4).

## Evidência

Reproduz sem risco apontando `HOME` para uma pasta descartável com uma
sentinela no lugar do slot:

```text
$ T=$(mktemp -d); mkdir -p $T/.local/share/duckstation/savestates
$ printf sentinela > $T/.local/share/duckstation/savestates/SLPM-87056_1.sav
$ HOME=$T python3 -c 'import sys; sys.path[:0]=["tools/looks","tools/pes2"]; import oracle; oracle.self_check()' | grep FAIL
  FAIL  restoring into a directory that is not there refuses: did NOT refuse
$ wc -c $T/.local/share/duckstation/savestates/SLPM-87056_1.sav
478 .../.local/share/duckstation/savestates/SLPM-87056_1.sav
```

## Root cause

O caso "restoring into a directory that is not there refuses" isola a cópia
mestra com `WE2002_LOOKS_STATES` e espera isolar o diretório do emulador com
`PES2_FORK=<tmp>/no-such-fork`. Mas `emulator_states_dir()` só deriva o
diretório do fork **no Windows**; no Linux devolve sempre
`~/.local/share/duckstation/savestates`, que existe. O `restore_state(1)` não
recusou: copiou o state sintético para o slot real. O ciclo inteiro rodou no
Windows, onde o isolamento funcionava, e o defeito só apareceu na primeira
corrida no Linux.

## Fix

Em `tools/looks/oracle.py`:

- `ENV_EMULATOR_STATES = "WE2002_LOOKS_EMULATOR_STATES"`, que
  `emulator_states_dir()` honra antes de tudo, nas duas plataformas. O default
  de cada máquina não muda.
- O self-check isola o emulador por essa variável, e só chama `restore_state`
  depois de conferir que `emulator_states_dir()` caiu dentro do `tmp` — um
  caso novo, "the emulator's directory is the planted one, not the real one".
  Se o isolamento regredir, o gate fica vermelho **sem gravar nada**.

## Arquivos a criar ou modificar

- [tools/looks/oracle.py](/tools/looks/oracle.py)

## Verificação

```text
$ printf sentinela > $T/.local/share/duckstation/savestates/SLPM-87056_1.sav
$ HOME=$T python3 tools/looks/selftest.py; echo $?; cat $T/.local/share/duckstation/savestates/SLPM-87056_1.sav
looks_selftest: 0 failure(s)
0
sentinela
```

Controle negativo — `emulator_states_dir` trocado pela forma antiga, que
ignora o override:

```text
  FAIL  the emulator's directory is the planted one, not the real one  /tmp/.../.local/share/duckstation/savestates
oracle.py: 1 failure(s)
sentinela
```

Corrida real, com o `HOME` do usuário: `looks_selftest: 0 failure(s)`, e o
SHA-1 do slot 1 é `43258eeb…` antes e depois.

## Log de Execução

- 2026-09-28 — reproduzido sob `HOME` descartável, corrigido, selftest verde
  no Linux com o slot real intacto; controle negativo vermelho sem gravar.
- **Closed** — commit `44bcba2` (2026-09-28): fix(looks): keep the oracle self-check out of the real DuckStation slot
  - Files (`git show --name-status 44bcba2`):
    - `A docs/tasks/looks/CORR-LOOKS-100.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/oracle.py`
