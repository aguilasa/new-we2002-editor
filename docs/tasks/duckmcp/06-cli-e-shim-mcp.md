---
id: DMCP-TASK-06
---

# DMCP-TASK-06 — `cli.py list/status/call`, e `tools/pes2/mcp.py` vira shim

## Goal

`python3 tools/duckmcp/cli.py list|status|call TOOL k=v` substitui o `mcp.py --list/--status/--call`, e `tools/pes2/mcp.py` vira re-export do `duckmcp.client` (mesmos nomes públicos: `Client`, `NotRunning`, `ToolError`, `SessionLost`, `SKIP`, `DEFAULT_HOST`, `DEFAULT_PORT`, `PROTOCOL`, `self_check`), sem mudar nenhum importador.

## Arquivos a criar ou modificar

- In:
  - `cli.py`
  - `tools/pes2/mcp.py` reduzido a shim
- Out:
  - mudar quem importa `mcp`

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0 (o `pes2_selftest` continua verde com o shim)
- [x] `python3 tools/duckmcp/cli.py list` sem fork sai 77 com a mensagem do `NotRunning`
- [x] `wc -l tools/pes2/mcp.py` colado no Log, e o arquivo não define classe nem função além do `self_check` delegado

## Notes

## Log de Execução

### 2026-10-22 — HEAD `446278d8`

**Feito.** `tools/duckmcp/cli.py` novo, com `ping`, `list`, `status` (`get_status`, `detail="full"`) e `call TOOL k=v` (valor decodificado como JSON quando parseia, string senão; par sem `=` é recusado). `--host`/`--port`/`--timeout` vêm antes do subcomando, com default de `env.mcp_host()`/`env.mcp_port()`. Saída 0 com resposta, 77 (`errors.SKIP`) no `NotRunning` com a frase no stderr, 1 no `ToolError`, 2 em linha de comando ruim. Rodado como script, ele tira `tools/duckmcp/` do `sys.path` e põe `tools/` — o `cli.py` dele nunca sombreia o de outro projeto. O layout de subparsers deixa lugar para os subcomandos de processo da DMCP-TASK-09.

`tools/pes2/mcp.py` virou shim de 81 linhas: `Client`, `PROTOCOL`, `SKIP`, `NotRunning`, `ToolError` e `SessionLost` são **os mesmos objetos** da lib (conferido com `is`), então o `except mcp.ToolError` do `tools/looks/oracle.py` pega o que o `duckmcp.client` levanta. `DEFAULT_HOST`/`DEFAULT_PORT` saem do `env.py`. Nenhum importador mudou.

**O critério "não define classe nem função além do `self_check` delegado", lido ao pé da letra.** O shim tem um único `def`, o `self_check`, e nenhuma classe. O `main` é uma atribuição (`functools.partial(cli.legacy_main, self_check=self_check)`), e a tradução das flags velhas (`--list`, `--status`, `--call`, `--self-check`) mora em `cli.legacy_argv`/`cli.legacy_main`, que saem com o shim no fechamento do ciclo. A sonda de vida é uma `lambda` atribuída ao `duckmcp.client.process_alive`, que importa o `fork` de modo preguiçoso (o `fork.py` importa este módulo no topo) e não captura exceção: o `Client._liveness` da lib já lê exceção como "desconhecido". É delegação, não lógica, e é **provisória**: a DMCP-TASK-08 preenche a costura dentro da lib.

O `self_check` do shim devolve lista de falhas (a forma que o `tools/pes2/selftest.py` lê, com `verbose=False`), roda o `client.self_check()` da lib com a sonda **default** reposta — um dos casos dela afirma que o default responde desconhecido — e acrescenta dois casos da costura ligada, com `fork.running_pids` substituído por `[]` e por `[4242]`.

**Mudança de texto, não de comportamento.** A mensagem do `NotRunning` deixou de dizer `tools/pes2/fork.py launch` e passou a dizer "Start the MCP fork": é o texto da lib, que é agnóstica de jogo. O diagnóstico vivo/morto continua em `mcp.py --list` porque a costura está ligada. Nenhum chamador casa esse trecho da frase (`grep -rn "fork.py launch\|IS running" tools/pes2 tools/looks`).

**Vermelho visto.** (1) Numa cópia do pacote no scratchpad, trocar o `return SKIP` do `cli.run` por `return 1` derruba `cli: list against a refused port exits 77 (errors.SKIP)`; mudar o esperado do `call` derruba `cli: call TOOL k=v decodes the values as JSON when they parse` — `duckmcp_selftest: 137 check(s) ran, 2 failure(s)`, exit 1. (2) Desligar a costura (`client.process_alive = mcp._LIB_PROBE`) faz o `mcp.self_check(verbose=False)` devolver as duas falhas `the shim's probe reads fork.running_pids() == []` e `== [4242]`.

```
$ python3 tools/duckmcp/selftest.py | tail -1; echo exit=$?
duckmcp_selftest: 137 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/pes2/selftest.py | tail -1
OK
(exit=0)
$ pgrep -x duckstation-qt; echo pgrep=$?
pgrep=1
$ python3 tools/duckmcp/cli.py list; echo exit=$?
skipping: no MCP server at http://127.0.0.1:2346/mcp -- the DuckStation fork is not running, or it died mid-run (PLAN-DUCKMCP-PY §1.3, pitfall 35). Start the MCP fork (the official AppImage has no MCP server). [URLError]
exit=77
$ wc -l tools/pes2/mcp.py
81 tools/pes2/mcp.py
$ grep -n '^class\|^def\|^main' tools/pes2/mcp.py
40:def self_check(verbose=True):
78:main = functools.partial(cli.legacy_main, self_check=self_check)
$ python3 tools/pes2/mcp.py --self-check | tail -1
SELF-CHECK OK: 26 checks
(exit=0)
$ python3 tools/pes2/mcp.py --list; echo exit=$?
skipping: no MCP server at http://127.0.0.1:2346/mcp -- and no DuckStation process either. It was never started, or it died mid-run (PLAN-DUCKMCP-PY §1.3, pitfall 35: the fork dies silently during free execution). Start the MCP fork (the official AppImage has no MCP server). [URLError]
exit=77
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 13 control(s), 13 red as required; per rule (a) 2/2, (c) 6/6, (client) 1/1, (d) 4/4
$ python3 tools/looks/selftest.py --quiet | tail -1
looks_selftest: 0 failure(s)
$ ctest --test-dir build -R 'duckmcp_selftest|pes2_selftest' | tail -3
100% tests passed, 0 tests failed out of 2
```

