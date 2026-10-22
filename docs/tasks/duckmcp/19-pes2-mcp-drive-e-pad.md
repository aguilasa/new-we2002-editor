---
id: DMCP-TASK-19
---

# DMCP-TASK-19 — `pes2`: `mcp_drive.py` e `pad.py` sobre `Session`

## Goal

`McpSession` vira camada de rota sobre `duckmcp.Session` e `pad.Live` sobre `Session.attach()`; somem os `PRESS_FRAMES`/`AFTER_FRAMES` e `STATE_DIR` duplicados, o `capitalize()` e a captura própria. As rotas produzem o mesmo PNG.

## Arquivos a criar ou modificar

- In:
  - os dois arquivos
  - a lista `PENDING` encolhida
- Out:
  - `who_writes.py`, `drive.py` (DMCP-TASK-20)

## Done criteria

- [ ] antes da mudança, `python3 tools/pes2/mcp_drive.py <cópia>.cue --screen <rota>` para `team-select`, `edit`, `result` e `replay`, com o `sha256sum` de cada PNG colado no Log; depois, os mesmos quatro digests
- [ ] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue, com o `pes2` caindo nos sítios destes dois arquivos
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0

## Notes

O `pad.Live.press` pausa antes de cada aperto e o `McpSession.press` não (§4.3): a escolha se registra no Log com o porquê.

## Log de Execução
