---
id: DMCP-TASK-08
---

# DMCP-TASK-08 — `fork.py` agnóstico de jogo — janela pelo PID, título opcional, `hide_window` e `size_window`

## Goal

`tools/duckmcp/fork.py` tem `launch(image, match=None, ...)`, `kill`, `running_pids`, `status`, `which_binary`, `RECIPE`, `joysticks`/`refuse_joysticks`, achar janela (X e Win32), dispensar o `Automatic Updater`, e `hide_window`/`size_window` vindos do `looks/oracle.py`. Sem `match`, a janela é a mais larga do PID que não é diálogo do emulador; nenhum título de jogo no arquivo.

## Arquivos a criar ou modificar

- In:
  - `tools/duckmcp/fork.py` e os checks do `fork.self_check`
  - o encaixe `client.process_alive` preenchido pela lib (`tools/duckmcp/client.py`), e a religação temporária do shim `tools/pes2/mcp.py` retirada, com as duas checagens dela movidas para o selftest da lib — a exceção medida da [CORR-DMCP-004](/docs/tasks/duckmcp/CORR-DMCP-004.md)
  - a linha da exceção na Fase 1 do `docs/prompts/perfil-duckmcp.md`, dita como encerrada aqui
- Out:
  - mudar `tools/pes2/fork.py` (DMCP-TASK-09)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest cobre o que o `fork.self_check` cobria: lançar sem fork instalado é `Skip`; `roms/` recusado nos dois separadores; joystick recusado; os nomes de processo no `kill`; `running_pids` nunca devolve o próprio PID
- [x] `grep -n 'Pro Evolution' tools/duckmcp/fork.py` não acha nada
- [x] `grep -n 'process_alive' tools/pes2/mcp.py` não acha nada, e o selftest da lib traz as duas checagens da sonda sobre `running_pids()` (`[]` dá morto, `[4242]` dá vivo)
- [x] o controle da regra (c) plantando `GAME_WINDOW = "^Pro Evolution Soccer 2$"` no `fork.py` da lib fica vermelho, visto no Log

## Notes

Os ramos Win32 não se medem nesta máquina; o Log diz isso em vez de dizer que passaram.

## Log de Execução

2026-10-22 — HEAD `ebca2811`, árvore com as edições desta task.

`tools/duckmcp/fork.py` novo, agnóstico de jogo. `launch(image, match=None, display=None, timeout=120,
home=None, verbose=True, log=None)` devolve `(pid, window, client)`; sem `match` a janela é a mais larga
do PID filho que não é diálogo nem janela auxiliar do emulador — a escolha saiu para uma função pura,
`pick_window(candidates, match)`, alimentada pelo X (`xdotool` + `_NET_WM_PID` via `xprop`) ou pelo Win32
(`EnumWindows`), e é ela que o selftest mede. `ANY_WINDOW = "ANY"` ficou como apelido de `match=None`.
Com `match`, conta só título que a regex acha, e o mais largo deles vence (o `pes2` pegava o primeiro da
busca; para um título só dá o mesmo). Diretório, AppImage e display vêm de `duckmcp.env`; o ambiente do
filho é `env.x_env(display)` mais `LD_LIBRARY_PATH`/`QT_PLUGIN_PATH` (`child_env`), e o `fork.py` não lê
variável nenhuma. `hide_window(handle)` e `size_window(handle, size, display=None)` vêm do
`tools/looks/oracle.py`, com o tamanho como parâmetro do chamador — nenhum tamanho de jogo na lib.

Uma mudança de ordem, de propósito: o `launch` recusa `roms/` **antes** de olhar a instalação. Assim a
recusa se mede pelo próprio `launch` em toda máquina, nos dois separadores, em vez de só onde o fork
está instalado.

O encaixe de vivacidade foi preenchido na lib: `client.process_alive()` importa `duckmcp.fork` tarde
(o `fork` importa o `client`) e responde `bool(fork.running_pids())`, ou `None` se a listagem falhar.
O shim `tools/pes2/mcp.py` perdeu a religação e as duas checagens; o `self_check` dele só embrulha o
`client.self_check()` no formato que o `tools/pes2/selftest.py` lê. A checagem antiga "the default
liveness probe answers unknown" virou "answers True, False or None", e as duas da sonda moraram no
`fork.self_check()`, com `running_pids` trocado por `[]` e `[4242]`.

A regra (c) não pegava título de janela: `^Pro Evolution Soccer 2$` não casa nome de projeto, serial nem
endereço. Entraram dois juízes — `TITLE_RE` no `selftest.py` (lista negativa dos títulos que este
repositório dirige, aplicada a toda linha, linhagem inclusive) e, como metade estrutural para título fora
da lista, a checagem "launch() has no default title (match=None)" —, cada um com o seu controle.
Também entrou um controle para a sonda desligada no `client.py`.

Os ramos Win32 (`_win_windows`, `_win_candidates`, `_dismiss_dialogs_windows`, `_tasklist_pids`,
`_win_image_path`, `hide_window`) **não foram medidos** nesta máquina: são porte literal do
`tools/pes2/fork.py` e do `looks/oracle.py`, e o selftest só exercita no Linux o lado X e o
`hide_window` como no-op. Nenhum emulador foi lançado.

```text
$ python3 tools/duckmcp/selftest.py; echo exit=$?
…
duckmcp_selftest: 181 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/duckmcp/selftest.py | grep -E 'fork: (a missing|roms|a joystick|no joystick|duckstation-qt is|AppRun is|DuckStation-x64 is|running_pids|process_alive|the client|child_env|launch\(\)|with no match)'
  ok    fork: duckstation-qt is in the kill list
  ok    fork: AppRun is in the kill list
  ok    fork: DuckStation-x64 is in the kill list
  ok    fork: a missing install skips and names the recipe
  ok    fork: roms/ is refused by launch (forward slashes)
  ok    fork: roms/ is refused by launch (backslashes)
  ok    fork: no joystick node lets a run go
  ok    fork: a joystick node refuses the run and names it
  ok    fork: running_pids never returns our own pid
  ok    fork: with no match the widest non-dialog window wins
  ok    fork: launch() has no default title (match=None)
  ok    fork: process_alive() is False when running_pids() == []
  ok    fork: the client's default probe reads fork.running_pids() == []
  ok    fork: process_alive() is True when running_pids() == [4242]
  ok    fork: the client's default probe reads fork.running_pids() == [4242]
  ok    fork: process_alive() is None when running_pids() raises
  ok    fork: child_env(':98') blanks XAUTHORITY
  ok    fork: child_env(':1') leaves XAUTHORITY as env.x_env does
  ok    fork: child_env sets DISPLAY
  ok    fork: a missing install adds no library path
$ grep -n 'Pro Evolution' tools/duckmcp/fork.py; echo grep=$?
grep=1
$ grep -n 'process_alive' tools/pes2/mcp.py; echo grep=$?
grep=1
$ python3 -c "import sys; sys.path[:0]=['tools','tools/pes2']; from duckmcp import client; a=client.process_alive; import mcp; sys.exit(0 if a is client.process_alive else 1)"; echo probe=$?
probe=0
$ python3 tools/duckmcp/controls.py; echo exit=$?
baseline: the untouched sandbox is green
…
red    c-game-window-title (rule c): FAIL  rule (c): fork.py names no game window title  line 110: Pro Evolution Soccer
red    c-launch-default-title (rule c): FAIL  fork: launch() has no default title (match=None)  '^Any Game$'
…
red    client-liveness-unwired (rule client): FAIL  fork: process_alive() is False when running_pids() == []
duckmcp_controls: 16 control(s), 16 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4
exit=0
$ python3 tools/pes2/selftest.py; echo exit=$?
…
  ok   mcp.py client, decoding and red cases
  ok   fork.py paths, kill list and refusals
…
OK
exit=0
$ python3 tools/pes2/mcp.py --self-check | tail -1
SELF-CHECK OK: 24 checks
$ python3 tools/looks/selftest.py --quiet | tail -1
looks_selftest: 0 failure(s)
$ python3 tools/duckmcp/audit.py | tail -1
audit: 208 raw site(s) in 15 file(s)
$ ctest --test-dir build -R 'duckmcp_selftest|pes2_selftest'
100% tests passed, 0 tests failed out of 2
```

O total do `audit.py` não mudou (208, o mesmo dos Logs da DMCP-TASK-02 e da DMCP-TASK-04): o `importlib.import_module("fork")`
que saiu do shim não era um sítio que o auditor conta, e o `tools/pes2/fork.py` continua igual até a
DMCP-TASK-09.
- **Closed** — commit `e9ac6f57` (2026-10-22): feat(duckmcp): game-agnostic fork launcher, and the client's liveness probe filled in the lib
  - Files (`git show --name-status e9ac6f57`):
    - `M docs/prompts/perfil-duckmcp.md`
    - `M docs/tasks/duckmcp/08-fork.md`
    - `M tools/duckmcp/client.py`
    - `M tools/duckmcp/controls.py`
    - `A tools/duckmcp/fork.py`
    - `M tools/duckmcp/selftest.py`
    - `M tools/pes2/mcp.py`
- **Reviewed** (2026-10-22) at `dccbc63f`: CORR-DMCP-006, CORR-DMCP-007
