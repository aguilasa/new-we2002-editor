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

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest cobre: sessão roubada recuperada uma vez; segunda perda é erro; outro `ToolError` passa sem novo handshake; JSON e SSE decodificam igual; porta recusada com processo vivo e morto dá as duas mensagens
- [ ] o controle `client-session-never-reclaimed` (desligar o `reclaim`) fica vermelho, visto no Log
- [ ] `python3 -c 'import sys; sys.path.insert(0, "tools"); import duckmcp.client; print(sorted(m for m in sys.modules if m.split(".")[0] in ("PIL","PySide6","numpy")))'` imprime `[]`

## Notes

O `OneSession` do `looks` faz a mesma coisa; ele some na DMCP-TASK-22.

## Log de Execução
