---
id: CORR-DMCP-008
---

# CORR-DMCP-008 — Restaurar o filtro de cmdline duckstation antes de matar processos AppRun

Origin: [DMCP-TASK-09](/docs/tasks/duckmcp/09-cli-fork-e-lancadores.md)

## Problem

Antes do `c2630fad`, o `kill_leftovers` do `run_duckstation.sh` só matava um PID `AppRun` /
`DuckStation-x64` / `duckstation-qt` se `/proc/<pid>/cmdline` contivesse "duckstation" (sem caixa) — o
comentário dizia "that is not a nicety". Agora ele chama `cli.py kill`, e `duckmcp.fork.running_pids()`
/ `kill()` casam só pelo nome exato do processo. Todo AppImage tipo 2 roda como `AppRun`, então
`run_duckstation.sh --kill` (usado também pelo `boot_check.sh` no caminho do AppImage e pelo trap de
limpeza dele) agora dá SIGKILL em AppImages alheios, com perda do que não foi gravado. `make pes2-kill`
e `cli.py kill` usam a mesma lista sem filtro; o `pes2/fork.py` antigo já tinha a brecha, e a task a
levou ao único caminho que era protegido.

## Evidência

```text
$ S=$(mktemp -d); mkdir $S/other-app; cp /bin/sleep $S/other-app/AppRun; ($S/other-app/AppRun 300 &); sleep 0.5; P=$(pgrep -x AppRun); grep -qsi duckstation /proc/$P/cmdline && echo old-guard-would-kill || echo old-guard-would-skip; bash tools/pes2/run_duckstation.sh --kill; kill -0 $P 2>/dev/null && echo "still alive" || echo "KILLED pid $P"
old-guard-would-skip
leftover DuckStation processes and mounts cleared
KILLED pid 456752
```

Controle, mesmo processo falso contra o script do commit pai
(`git archive 1238f761 tools/pes2/run_duckstation.sh`), com `bash -x`:

```text
+ grep -qsi duckstation /proc/457201/cmdline
old: still alive
```

## Root cause

A task levou "a lista de nomes" para `PROCESS_NAMES`, mas o `running_pids()` da lib
(`tools/duckmcp/fork.py:260-279`) nunca teve o filtro de cmdline; só a cópia em shell o tinha, e ela
foi apagada.

## Fix

Em `tools/duckmcp/fork.py`, no ramo não-Windows de `running_pids()`, manter um PID só quando
`/proc/<pid>/cmdline` contiver "duckstation" sem caixa, como o shell removido fazia. Acrescentar
self-check e controle plantado (filtro removido → vermelho) em `tools/duckmcp/selftest.py` /
`tools/duckmcp/controls.py`.

## Arquivos a criar ou modificar

- `tools/duckmcp/fork.py`
- `tools/duckmcp/selftest.py`
- `tools/duckmcp/controls.py`

## Verificação

O comando da Evidência imprime "still alive", e `python3 tools/duckmcp/cli.py kill` também deixa o
`AppRun` falso vivo (matá-lo à mão depois). O controle novo fica vermelho com o filtro removido.

## Log de Execução

2026-10-22 — reproduzido na HEAD `69910a9f`: o AppRun falso (`/bin/sleep` copiado) dá
`old-guard-would-skip` e depois `KILLED pid 471686` pelo `run_duckstation.sh --kill`.

Conserto: o `running_pids()` passa a saída do `pgrep` por `select_pids(found, own, cmdline)`, função pura.
Ela descarta o próprio PID, as repetições e todo PID cujo `/proc/<pid>/cmdline` não diz "duckstation" em
qualquer caixa, que era a guarda do shell removido. O `self_check` ganhou o caso com três linhas (um
AppRun alheio, um AppImage do DuckStation e o fork), e o `controls.py` ganhou `fork-kills-foreign-apprun`,
que tira o filtro.

Verificação:

```text
$ <Evidência> ; bash tools/pes2/run_duckstation.sh --kill; …
leftover DuckStation processes and mounts cleared
still alive
$ python3 tools/duckmcp/cli.py kill; kill -0 $P && echo "cli kill: still alive"
stopped 0 DuckStation process(es)
cli kill: still alive
$ python3 tools/duckmcp/controls.py --only fork-kills-foreign-apprun
red    fork-kills-foreign-apprun (rule fork): FAIL  fork: an AppRun whose command line is not DuckStation's is spared  [11, 12, 13]
duckmcp_controls: 1 control(s), 1 red as required; per rule (fork) 1/1
$ DISPLAY=:98 XAUTHORITY= python3 tools/duckmcp/cli.py launch …/we2002-english.cue; python3 tools/duckmcp/cli.py kill
stopped 1 DuckStation process(es): [473816]      # o fork de verdade continua achado
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 195 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 17 control(s), 17 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 1/1
```
