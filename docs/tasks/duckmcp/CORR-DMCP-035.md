---
id: CORR-DMCP-035
---

# CORR-DMCP-035 — Apontar o bloco mcp.py do PES2-WINDOWS para tools/duckmcp/cli.py

Origin: [DMCP-TASK-28](/docs/tasks/duckmcp/28-documentacao.md)

## Problem

A §4 do `docs/PES2-WINDOWS.md` ainda dá `python tools\pes2\mcp.py --status|--list|--call get_status`
como o jeito vivo de consultar o servidor no Windows. Esses comandos só funcionam enquanto o shim
existir, e a Fase 9 o apaga. A task varreu o bloco `tools\pes2\fork.py` poucas linhas acima, e o Log diz
que os blocos PowerShell foram cobertos; a regex do critério 1 só aceita `/` como separador e não vê a
forma com contrabarra, então este passou. O check da Fase 8 ("nenhuma menção viva") não se cumpre.

## Evidência

```text
$ grep -rnE 'pes2[/\\](mcp|fork|savestate)\.py' CLAUDE.md docs --include='*.md' | grep -v 'docs/tasks/' | grep -v PLAN-DUCKMCP | grep -v perfil-duckmcp | grep -v 'histórico'
docs/PES2-WINDOWS.md:180:python tools\pes2\mcp.py --status
docs/PES2-WINDOWS.md:181:python tools\pes2\mcp.py --list
docs/PES2-WINDOWS.md:182:python tools\pes2\mcp.py --call get_status
$ git show bbd0bd34 -- docs/PES2-WINDOWS.md | grep -n 'pes2\\\\mcp'
(nenhuma saída: o commit não tocou essas linhas, mas reescreveu `tools\pes2\fork.py launch|status|kill` para `tools\duckmcp\cli.py launch|procs|kill`)
```

## Root cause

Hipótese: a varredura manual da forma com contrabarra procurou só `fork.py`, e a regex do critério 1
aceita só `/` como separador.

## Fix

Na §4 do `docs/PES2-WINDOWS.md`, trocar o bloco por `python tools\duckmcp\cli.py status`, `... list` e
`... call get_status` (os subcomandos do `cli.py` são `status|list|call`, `tools/duckmcp/cli.py:56`).
Opcional: alargar a regex do check da Fase 8 no `perfil-duckmcp.md` para `pes2[/\\]`.

## Arquivos a criar ou modificar

- `docs/PES2-WINDOWS.md`

## Verificação

`grep -nE 'pes2\\(mcp|fork|savestate)\.py' docs/PES2-WINDOWS.md | grep -v 'histórico'` imprime as linhas
180-182 hoje e nada depois do conserto.

## Log de Execução
