---
id: CORR-DMCP-003
---

# CORR-DMCP-003 — Registrar no PLAN §3.3 a exceção dos nomes PES2_* do env.py

Origin: [DMCP-TASK-03](/docs/tasks/duckmcp/03-regras-de-desenho.md)

## Problem

A regra (c) da §3.3 do [plano](/docs/PLAN-DUCKMCP-PY.md#3.3) diz que o pacote não guarda nome de
projeto (`PES2` listado) "fora de comentário de linhagem marcado", sem exceção. O `env.py` (linhas
34-40) escreve cinco nomes `PES2_*` como código, fora de comentário de linhagem, e o selftest os isenta
por `LEGACY_ENV_NAMES` — decisão que só existe no Log da DMCP-TASK-03. Plano e perfil não foram
atualizados, então o gate impõe uma regra que a fonte de verdade não diz. "Fechar um veredito é varrer
quem dizia o anterior."

## Evidência

```text
$ sed -n 241,259p docs/PLAN-DUCKMCP-PY.md | grep -n 'PES2'
8:  `kit2d`, `WE2002`, `PES2` — fora de comentário de linhagem marcado), e
$ grep -nE 'LEGACY|allow|permiss|cinco nomes' docs/PLAN-DUCKMCP-PY.md docs/prompts/perfil-duckmcp.md
$ grep -n '"PES2_' tools/duckmcp/env.py
(cinco linhas, 35-39, dentro de `LEGACY = {...}`, código e não comentário)
```

## Root cause

A decisão 3 da §2 (os nomes legados são lidos como fallback) colide com a letra da regra (c). A task
resolveu a colisão no código e no Log, mas não levou a decisão de volta ao plano.

## Fix

Acrescentar à regra (c) da §3.3 do `docs/PLAN-DUCKMCP-PY.md` a exceção: exatamente os cinco nomes
legados `PES2_*`, só no `env.py`, pela decisão 3 da §2. Acrescentar a linha correspondente à lista de
decisões já confirmadas do `docs/prompts/perfil-duckmcp.md`.

## Arquivos a criar ou modificar

- `docs/PLAN-DUCKMCP-PY.md`
- `docs/prompts/perfil-duckmcp.md`

## Verificação

`sed -n '/^### 3.3/,/^### 3.4/p' docs/PLAN-DUCKMCP-PY.md | grep -c 'PES2_MCP_HOST'` imprime 0 hoje e
tem de imprimir ao menos 1 depois do conserto.

## Log de Execução
