---
id: CORR-DMCP-011
---

# CORR-DMCP-011 — Matar o DuckStation só quando o live.py o lançou, não no pulo

Origin: [DMCP-TASK-10](/docs/tasks/duckmcp/10-duckmcp-live.md)

## Problem

Em `run()` do `tools/duckmcp/live.py`, o `fork.kill()` fica num `finally` que envolve o
`fork.launch()`. Quando o `launch` levanta `Skip` (sem X server no display, sem imagem no caminho), o
`live.py` ainda mata todo DuckStation da máquina e depois se reporta *skipped* — inclusive uma sessão
que ele não abriu, como uma partida de `make pes2-play` que o usuário esteja jogando no `:1`. Teste que
se reporta pulado não pode encerrar o emulador de outro. (O próprio `launch` também mata tudo antes de
subir; isso é comportamento antigo da lib, que o `RESOURCE_LOCK` cobre dentro do ctest. O caminho do
pulo é novo aqui.)

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/duckmcp/cli.py launch $PWD/work/looks-disc/we2002-english.cue >/dev/null; python3 tools/duckmcp/cli.py procs
pids: [458489]
  pid 458489  fork (MCP)  /home/ingmar/Applications/duckstation-mcp/bin/duckstation-qt
$ python3 tools/duckmcp/live.py --image $PWD/work/looks-disc/we2002-english.cue --display :97; echo exit=$?
duckmcp_live: skipped -- no X server on :97
exit=77
$ python3 tools/duckmcp/cli.py procs
pids: []
no DuckStation is running
```

## Root cause

O try/finally começa antes do `fork.launch` em vez de depois que ele volta, então a limpeza roda também
nos caminhos em que nada foi lançado.

## Fix

Em `tools/duckmcp/live.py`, chamar `fork.launch(...)` antes do `try:` e deixar no try/finally só os
passos seguintes — ou ligar uma flag quando o `launch` volta e matar só com ela ligada. Acrescentar um
check do `live.py` ao selftest/controles: com um `fork.launch` falso que levanta `Skip`, afirmar que
`fork.kill` não é chamado, e plantar a ordem antiga para vê-lo vermelho.

## Arquivos a criar ou modificar

- `tools/duckmcp/live.py`
- `tools/duckmcp/selftest.py`
- `tools/duckmcp/controls.py`

## Verificação

Os três comandos da Evidência: depois do conserto o segundo `procs` ainda lista o PID lançado no
primeiro passo; em seguida `python3 tools/duckmcp/cli.py kill`. O controle novo fica vermelho com a
ordem antiga.

## Log de Execução
