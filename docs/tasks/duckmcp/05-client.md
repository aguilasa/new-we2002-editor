---
id: DMCP-TASK-05
---

# DMCP-TASK-05 — `client.py` a partir do `mcp.py` de `f21182ea`, com servidor de teste

## Goal

`tools/duckmcp/client.py` tem o `Client` do `tools/pes2/mcp.py` (transporte, `initialize`, `tools()`, `call()`, `reclaim`, decodificação JSON/SSE, o diagnóstico de `NotRunning` — processo vivo × morto, armadilha 35 —), com as mensagens citando o [§1.3](/docs/PLAN-DUCKMCP-PY.md#1.3) e as variáveis lidas pelo `env.py`. O servidor de teste e os casos do `mcp.self_check` passam para o selftest da lib.

## Arquivos a criar ou modificar

- In:
  - `client.py` e os checks dele
- Out:
  - mudar `tools/pes2/mcp.py` (DMCP-TASK-06)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest cobre: sessão roubada recuperada uma vez; segunda perda é erro; outro `ToolError` passa sem novo handshake; JSON e SSE decodificam igual; porta recusada com processo vivo e morto dá as duas mensagens
- [x] o controle `client-session-never-reclaimed` (desligar o `reclaim`) fica vermelho, visto no Log
- [x] `python3 -c 'import sys; sys.path.insert(0, "tools"); import duckmcp.client; print(sorted(m for m in sys.modules if m.split(".")[0] in ("PIL","PySide6","numpy")))'` imprime `[]`

## Notes

O `OneSession` do `looks` faz a mesma coisa; ele some na DMCP-TASK-22.

## Log de Execução

2026-10-22 — HEAD `b5749baa` mais a árvore de trabalho desta task.

`tools/duckmcp/client.py` traz o `Client` do `tools/pes2/mcp.py` de `f21182ea`: transporte, `initialize`, `tools()`, `call()` com `reclaim`, `_decode` (JSON e SSE), `_result`, `_text_of`. Diferenças em relação à origem: host e porta vêm de `env.mcp_host()`/`env.mcp_port()` na construção, nunca no import; as exceções são as de `duckmcp.errors`; o nome de cliente padrão é `duckmcp`; as mensagens citam `PLAN-DUCKMCP-PY §1.3` com as armadilhas 35 e 46, sem nome de projeto. O diagnóstico de porta recusada mantém as três variantes (processo vivo, morto, desconhecido), mas a sonda de vida deixou de importar o `fork` do `pes2`: virou a função de módulo `client.process_alive()`, que hoje devolve `None` (desconhecido) e é o encaixe que a DMCP-TASK-08 preenche; um chamador também pode passar `Client(alive=callable)`. A sonda é lida no momento da recusa, então uma troca feita depois do import vale, e uma sonda que levanta exceção conta como desconhecida.

O servidor de teste (`_OneSessionServer`) e os casos do `mcp.self_check` passaram para `client.self_check()`, chamado pelo `selftest.py`. O servidor ganhou modos para cobrir o que a origem não cobria: resposta SSE pela rede (`sse`), erro JSON-RPC (`fail`), HTTP 500 (`crash`), roubo repetido de sessão (`steal(n)`) e o contador `handshakes`. `__init__.py` reexporta `Client`. O `tools/pes2/mcp.py` não foi tocado (DMCP-TASK-06).

- `python3 tools/duckmcp/selftest.py --quiet; echo exit=$?` → `duckmcp_selftest: 121 check(s) ran, 0 failure(s)`, `exit=0`.
- Os casos pedidos, da corrida sem `--quiet`:

```
  ok    client: a one-event SSE body decodes the same as JSON
  ok    client: a refused port with no process names the crash and the plan
  ok    client: a refused port with a live process says the server is the problem
  ok    client: a refused port with an unknown process names both causes
  ok    client: the stand-in answers an SSE reply the same
  ok    client: a stolen session is recovered once and the call goes through
  ok    client: a second loss in a row is an error (SessionLost)
  ok    client: another ToolError passes without a new handshake
  ok    client: an HTTP 500 is a ToolError without a new handshake
  ok    client: without reclaim a stolen session fails with SessionLost
```

- `python3 tools/duckmcp/controls.py; echo exit=$?` → o controle novo e a última linha, `exit=0`:

```
red    client-session-never-reclaimed (rule client): FAIL  client: a stolen session is recovered once and the call goes through  SessionLost: HTTP 400 from the server: {"jsonrpc":"2.0","error":{"code":-32600,"message":"Bad Request: missing or invalid MCP-Session-Id"}} (PLAN-DUCKMCP-PY §1.3, pitfall 46: another client's handshake took the session)
duckmcp_controls: 13 control(s), 13 red as required; per rule (a) 2/2, (c) 6/6, (client) 1/1, (d) 4/4
```

- `python3 -c 'import sys; sys.path.insert(0, "tools"); import duckmcp.client; print(sorted(m for m in sys.modules if m.split(".")[0] in ("PIL","PySide6","numpy")))'` → `[]`.
- `ctest --test-dir build -R duckmcp_selftest` → `100% tests passed, 0 tests failed out of 1`.
- `python3 tools/pes2/selftest.py; echo exit=$?` → última linha `OK`, `exit=0` (o `pes2` não foi tocado).

Sweep: os totais anteriores (`88 check(s)`, `12 control(s)`) só aparecem em transcrições de Log e de CORR já fechadas, que ficam como estão.
