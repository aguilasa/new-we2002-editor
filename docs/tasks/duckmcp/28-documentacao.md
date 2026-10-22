---
id: DMCP-TASK-28
---

# DMCP-TASK-28 — Documentação: `CLAUDE.md`, a §6.11 do PES2 e a decisão no `perfil-kit2d.md`

## Goal

`CLAUDE.md` ganha uma seção da lib (comandos, variáveis `DUCKSTATION_*` e as `PES2_*` como legado, armadilhas do §1.3), e as tabelas do PES2 e do `looks` deixam de citar `tools/pes2/mcp.py`, `fork.py`, `savestate.py`; a §6.11 do `PLAN-PES2-PSX.md` remete ao [§1.3](/docs/PLAN-DUCKMCP-PY.md#1.3) nas armadilhas do emulador; o `perfil-kit2d.md` registra que o `oracle.py` do `kit2d` nasce sobre a lib.

## Arquivos a criar ou modificar

- In:
  - os arquivos listados
- Out:
  - tasks do `kit2d`

## Done criteria

- [ ] `grep -rnE 'tools/pes2/(mcp|fork|savestate)\.py|pes2/(mcp|fork|savestate)\.py' CLAUDE.md docs --include='*.md' | grep -v 'docs/tasks/concluidos'` lista só remissões históricas marcadas, coladas no Log
- [ ] `grep -n 'DUCKSTATION_MCP_PORT' CLAUDE.md` acha a seção nova
- [ ] `rite check --cycle kit2d` continua limpo
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

Regra do ciclo: fechar um veredito é varrer quem dizia o anterior — a lista do `grep` é a varredura.

## Log de Execução
