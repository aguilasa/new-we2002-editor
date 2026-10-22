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

2026-10-22 — reproduzido na HEAD `69910a9f`: com o fork lançado no `:98` (`pids: [471966]`), o
`live.py --display :97` sai 77 e depois o `procs` mostra `pids: []`.

Causa confirmada, e um detalhe que mudou o conserto: o `fork.launch` levanta `Fail` também **depois** do
`Popen` ("the game window never appeared"), com o processo dele ainda vivo. Tirar o `launch` do `try`, a
primeira opção da CORR, deixaria órfão. Por isso o `run()` anota os PIDs vivos antes do `launch`. Se o
`launch` levantar, mata só quando há PID novo; se voltar, o try/finally mata como antes. O docstring do
módulo diz isso.

Gate: `check_live_kill` no `selftest.py` troca `fork.launch`/`kill`/`running_pids` por falsos e cobre
dois casos. Um `Skip` com emulador alheio de pé não pode matar; um `Fail` com PID novo tem de matar. O
`controls.py` ganhou `live-kills-on-skip`, que planta a ordem antiga (`if True:`).

Verificação:

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/duckmcp/cli.py launch …/we2002-english.cue; python3 tools/duckmcp/cli.py procs | head -1
pids: [481485]
$ python3 tools/duckmcp/live.py --image …/we2002-english.cue --display :97; echo exit=$?
duckmcp_live: skipped -- no X server on :97
exit=77
$ python3 tools/duckmcp/cli.py procs | head -1; python3 tools/duckmcp/cli.py kill
pids: [481485]
stopped 1 DuckStation process(es): [481485]
$ python3 tools/duckmcp/live.py --image …/we2002-english.cue --display :98 | tail -1   # caminho feliz
duckmcp_live: ok -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 92->97
$ python3 tools/duckmcp/cli.py procs | head -1
pids: []
$ python3 tools/duckmcp/controls.py --only live-kills-on-skip | tail -2
red    live-kills-on-skip (rule live): FAIL  live: a skipped launch leaves another session's emulator alive  kill() called 1 time(s), want 0
duckmcp_controls: 1 control(s), 1 red as required; per rule (live) 1/1
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 198 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 20 control(s), 20 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (live) 1/1
```
- **Closed** — commit `2d80af64` (2026-10-22): fix(duckmcp): stop the fork in live.py only when this run launched one
  - Files (`git show --name-status 2d80af64`):
    - `M docs/tasks/duckmcp/CORR-DMCP-011.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/live.py`
    - `M tools/duckmcp/selftest.py`
