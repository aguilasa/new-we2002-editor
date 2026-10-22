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

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0 (o `pes2_selftest` continua verde com o shim)
- [ ] `python3 tools/duckmcp/cli.py list` sem fork sai 77 com a mensagem do `NotRunning`
- [ ] `wc -l tools/pes2/mcp.py` colado no Log, e o arquivo não define classe nem função além do `self_check` delegado

## Notes

## Log de Execução
