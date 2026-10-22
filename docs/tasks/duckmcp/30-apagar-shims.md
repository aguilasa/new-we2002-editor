---
id: DMCP-TASK-30
---

# DMCP-TASK-30 — Apagar os shims, e o `audit.py` em zero

## Goal

`tools/pes2/mcp.py`, `fork.py` e `savestate.py` não existem; a lista `PENDING` da regra (b) é vazia; nenhum import deles sobra em `tools/`, `tests/`, `Makefile`, `make.ps1` nem nos `.sh`.

## Arquivos a criar ou modificar

- In:
  - os três shims e a lista
- Out:
  - —

## Done criteria

- [ ] `python3 tools/duckmcp/audit.py` imprime total 0, colado no Log
- [ ] `ls tools/pes2/mcp.py tools/pes2/fork.py tools/pes2/savestate.py` falha nos três
- [ ] um `import fork` plantado em `tools/looks/oracle.py` deixa o selftest vermelho, visto no Log
- [ ] `ctest --test-dir build -R 'duckmcp_selftest|pes2_selftest|looks_selftest|kits_selftest|kit2d_selftest'` passa, 5 de 5

## Notes

## Log de Execução
