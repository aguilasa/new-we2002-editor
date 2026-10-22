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
