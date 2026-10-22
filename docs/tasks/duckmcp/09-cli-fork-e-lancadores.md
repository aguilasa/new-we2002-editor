---
id: DMCP-TASK-09
---

# DMCP-TASK-09 — `cli.py launch/kill/status/recipe/which`, shim do `pes2/fork.py`, e os lançadores apontados

## Goal

`python3 tools/duckmcp/cli.py launch|kill|status|recipe|which` existe; `tools/pes2/fork.py` vira shim que reexporta `duckmcp.fork` e passa o título do PES2 como `match` no `launch` dele; `boot_check.sh`, `run_duckstation.sh`, `Makefile` e `make.ps1` chamam a lib onde chamavam `tools/pes2/fork.py`, e a lista de nomes de processo do `kill_leftovers` sai de um lugar só.

## Arquivos a criar ou modificar

- In:
  - `cli.py`
  - o shim
  - os quatro lançadores
  - o controle `fork-joystick-let-through` do `tools/kits/controls.py`, que planta texto dentro de `tools/pes2/fork.py`, reapontado para onde o código mora agora, e o monkeypatch de `fork.joysticks`/`fork.launch` do `tools/kits/selftest.py` mantido efetivo — §4.1 e §4.2: quem move o código reaponta o controle na mesma task
- Out:
  - mudar `mcp_drive.py`, `pad.py` (Fase 5)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0
- [x] `python3 tools/duckmcp/cli.py recipe` imprime a receita, e `procs` sem fork imprime `pids: []` (o `status` da lib já é o `get_status` do servidor; ver o Log)
- [x] `grep -rn 'pes2/fork.py' Makefile make.ps1 tools/pes2/*.sh` não acha nada
- [x] `make -n pes2-status` mostra a chamada à lib
- [x] `python3 tools/kits/selftest.py --quiet` sai 0, e a linha dos controles mostra `fork-joystick-let-through` vermelho no arquivo novo

## Notes

O `run_duckstation.sh` continua sendo o caminho do AppImage oficial (não-objetivo do §0); muda só de onde tira as constantes.

## Log de Execução

- **pending** (2026-10-22): batch stopped before wave 2: kits_selftest red since 4de49640 (CORR-DMCP-005); the pes2/fork.py shim would make it worse
- **Execução** (2026-10-22, sobre HEAD `1238f761`, árvore com as mudanças desta task não commitadas):
  - **CLI da lib.** `tools/duckmcp/cli.py` ganhou `launch IMAGE [--display] [--timeout] [--match REGEX]`, `kill`, `procs`, `recipe` e `which`, que não abrem sessão MCP (`run_process`). O `status` já era o `get_status` do servidor, então o que está *rodando* chama-se **`procs`**, e imprime `pids: [...]` antes do relatório de `fork.status()` — o critério "`status` sem fork imprime `pids: []`" se mede em `procs`. O `--timeout` do `launch` tem `dest` próprio (`launch_timeout`), porque o `--timeout` de topo é o do cliente e um default de subparser o sobrescreveria. `Skip` sai 77, `Fail` sai 1 com `FORK FAILED:` no stderr. Sem `--match` vale a janela mais larga que não é diálogo (`fork.pick_window`): a lib não ganhou título nenhum, e `cli.self_check` afirma `--match None` por default.
  - **Shim.** `tools/pes2/fork.py` reexporta os objetos de `duckmcp.fork` (`except fork.Fail` pega o que a lib levanta: é a mesma classe) e guarda o que é do PES2: `GAME_WINDOW` e o fallback `PES2_IMAGE` da linha de comando antiga, que agora é traduzida (`translate`) para a do `cli.py` — `status` vira `procs`, `--window` vira `--match`. `launch` mantém a ordem posicional antiga (`display` em segundo) e passa `match=GAME_WINDOW` salvo se o chamador disser outro, `ANY_WINDOW` incluído. `FORK_HOME` e `APPIMAGE` saem de `env.fork_home()`/`env.appimage()` na hora em que são pedidos (`__getattr__` de módulo), não no import; `env_for` virou alias de `child_env`.
  - **Monkeypatch (§4.2), opção (i).** `refuse_joysticks` do shim *é* a função da lib e lê `joysticks` do módulo da lib; o `launch` do shim chama `duckmcp.fork.launch` na hora da chamada. Por isso `tools/kits/selftest.py:_live_guard_checks` passou a trocar `duckmcp.fork.joysticks` e `duckmcp.fork.launch` (importado como `lib`), não os nomes do shim — trocar no shim não alcançaria nenhum dos dois, e o docstring do shim diz isso. O próprio `fork.py --self-check` afirma a costura: um `duckmcp.fork.launch` trocado recebe a chamada do shim com `GAME_WINDOW` e com `ANY_WINDOW`, e um `duckmcp.fork.joysticks` trocado faz o `refuse_joysticks` do shim recusar.
  - **Controle.** `fork-joystick-let-through` de `tools/kits/controls.py` aponta para `duckmcp/fork.py`; o texto plantado é o mesmo e casa uma vez só lá. `COPIED` já levava `tools/duckmcp` (CORR-DMCP-005). `looks-oracle-joystick-unasked` continua casando em `looks/oracle.py`.
  - **Lançadores.** `Makefile` (`pes2`, `pes2-kill`, `pes2-status`, `we2002-play`) e `make.ps1` (`$FORK_PY`, `Invoke-Fork` com `-u` e a tradução do 77, `Test-Fork`, o relatório de ambiente) chamam `tools/duckmcp/cli.py`. O título do PES2 vai explícito como `--match` (`PES2_WINDOW` nos dois); o WE2002 vai sem `--match`, que é o que `--window ANY` fazia. `pes2-status` chama `procs`. O `make.ps1` exporta `DUCKSTATION_FORK` além de `PES2_FORK`, porque o nome novo ganha do legado na lib e um `DUCKSTATION_FORK` herdado passaria por cima do `-DuckData`. O `boot_check.sh` lança e mata pelo `cli.py`, com `--match` do título, e lê display e AppImage na precedência do `env.py` (`DUCKSTATION_*`, depois `PES2_*`). O `run_duckstation.sh` continua sendo o caminho do AppImage (§0): o `kill_leftovers` virou `python3 tools/duckmcp/cli.py kill`, então a lista de nomes de processo mora só em `PROCESS_NAMES` da lib, e display e AppImage seguem a mesma precedência. O `make.ps1` **não rodou**: não há `pwsh` nesta máquina; foi conferido por leitura.
  - **Audit.** `audit.py` caiu de 208 para 206 sites (15 para 14 arquivos), contado contra uma cópia `git archive HEAD` de `tools/`: as duas construções de `Client(` que moravam em `tools/pes2/fork.py` saíram com o shim. A linha de `import fork` do `kits/selftest.py` continua contada; ela some na Fase 4.

```
$ python3 tools/duckmcp/selftest.py | tail -1; echo exit=$?
duckmcp_selftest: 186 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/pes2/selftest.py | tail -1; echo exit=$?
OK
exit=0
$ python3 tools/pes2/fork.py --self-check | tail -1
SELF-CHECK OK: 35 checks
$ python3 tools/duckmcp/cli.py recipe | head -3
Getting the fork -- two ways, cheapest first.

1. Download the build its own CI publishes. The fork's README is the
$ python3 tools/duckmcp/cli.py procs; echo exit=$?
pids: []
no DuckStation is running
exit=0
$ python3 tools/duckmcp/cli.py launch /x/roms/a.cue; echo exit=$?
FORK FAILED: refusing to boot roms/ -- copy first
exit=1
$ python3 tools/duckmcp/cli.py launch /nonexistent.cue; echo exit=$?
skipping: no image at /nonexistent.cue
exit=77
$ grep -rn 'pes2/fork.py' Makefile make.ps1 tools/pes2/*.sh; echo grep-exit=$?
grep-exit=1
$ make -n pes2-status
python3 tools/duckmcp/cli.py procs
$ python3 tools/kits/controls.py --only fork-joystick-let-through | tail -2
  RED    fork-joystick-let-through    duckmcp/fork.py :: refuse_joysticks
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only looks-oracle-joystick-unasked | tail -2
  RED    looks-oracle-joystick-unasked looks/oracle.py :: Oracle.__enter__
controls: 1 of 1 red
$ python3 tools/kits/selftest.py --quiet | tail -4; echo exit=$?
  ..... 87 of 87 controls red
controls: 0 failure(s)
kits_selftest: 0 failure(s)
exit=0
$ python3 tools/looks/selftest.py --quiet | tail -1
looks_selftest: 0 failure(s)
$ bash -n tools/pes2/boot_check.sh tools/pes2/run_duckstation.sh && echo syntax-ok
syntax-ok
$ tools/pes2/boot_check.sh --self-check | tail -1
SELF-CHECK OK: the verdict, its red cases and the comparison
$ python3 tools/duckmcp/controls.py | tail -1; echo exit=$?
duckmcp_controls: 16 control(s), 16 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4
exit=0
$ python3 tools/duckmcp/audit.py | tail -1
audit: 206 raw site(s) in 14 file(s)
$ ctest --test-dir build -R 'duckmcp_selftest|pes2_selftest|kits_selftest|looks_selftest' | tail -3
100% tests passed, 0 tests failed out of 4

Total Test time (real) = 361.10 sec
```

**Menções desatualizadas fora do escopo desta task** (o sweep achou; continuam verdadeiras hoje, porque os comandos antigos passam pelo shim, mas citam o caminho velho). Ficam registradas aqui para quem as possui:

- `CLAUDE.md` (linhas da tabela do PES2 com `tools/pes2/fork.py launch|kill|status|recipe` e a prosa que o nomeia), `docs/PLAN-PES2-PSX.md`, `docs/PES2-WINDOWS.md`, `docs/LOOKS-AMBIENTE.md`, `docs/PLAN-LOOKS-PY.md` → DMCP-TASK-28 (documentação).
- `tools/pes2/pad.py:9`, docstring → DMCP-TASK-19.
- `tools/looks/oracle.py:330-352`: docstring "Derived from `fork.FORK_HOME`" e a leitura `os.environ.get("PES2_FORK", fork.FORK_HOME)`, que vira `env.savestates_dir()` → DMCP-TASK-22.
- **Closed** — commit `c2630fad` (2026-10-22): feat(duckmcp): process commands in cli.py, pes2/fork.py as a shim, launchers on the lib
  - Files (`git show --name-status c2630fad`):
    - `M Makefile`
    - `M docs/tasks/duckmcp/09-cli-fork-e-lancadores.md`
    - `M make.ps1`
    - `M tools/duckmcp/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
    - `M tools/pes2/boot_check.sh`
    - `M tools/pes2/fork.py`
    - `M tools/pes2/run_duckstation.sh`
