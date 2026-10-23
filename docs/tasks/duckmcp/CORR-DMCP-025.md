---
id: CORR-DMCP-025
---

# CORR-DMCP-025 — A guarda de Dia/Noche em route_result não vê a troca de valor e a rota result nunca chega à tela

Origin: [DMCP-TASK-19](/docs/tasks/duckmcp/19-pes2-mcp-drive-e-pad.md)

## Problem

A rota `result` do `tools/pes2/mcp_drive.py` nunca chega à tela de resultado. Ela para em
`route_result`, na guarda que confere que o `Right` em `Dia/Noche` mudou o quadro
(`tools/pes2/mcp_drive.py:778`, `if s.capture().difference(before) < 0.0005`), e sai com
`MCP DRIVE FAILED: Right on Dia/Noche changed nothing -- the cursor is not on the first row`. O
aperto funciona — `match-options.png` mostra `Día/Noche  Al azar` e `match-options-lit.png` mostra
`Día/Noche  Día` —, mas trocar uma palavra muda o quadro inteiro em 0,00048, abaixo do limiar. O
defeito é anterior à DMCP-TASK-19: falha igual na HEAD de partida `6f6d7c7b` e depois da migração.
Sem a rota, a Fase 5 não mostra o PNG da tela de resultado igual antes e depois
([§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2)), e a DMCP-TASK-19 fica bloqueada nesse critério.

## Evidência

Precisa do fork, do `:98` e dos save states de `~/.local/share/duckstation/savestates`. Três corridas
(duas na HEAD `6f6d7c7b`, uma com a migração da DMCP-TASK-19), as três iguais:

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen result --out-dir "$OUT"; echo "rc=$?"
MCP DRIVE FAILED: Right on Dia/Noche changed nothing -- the cursor is not on the first row
rc=1
```

A diferença, medida com o `drive.Frame.difference` da própria guarda sobre os dois PNG que a rota
grava em volta do aperto:

```text
$ python3 -c "import sys; sys.path.insert(0,'tools/pes2'); import drive; print(drive.Frame('$OUT/match-options.png').difference(drive.Frame('$OUT/match-options-lit.png')))"
0.00048095095544579156
```

O mesmo valor, ao último dígito, nas três corridas (`before1`, `before2`, `after1`). O docstring do
`mcp_drive.py` mede o ruído de "mesma linha" em 0,0002 a 0,0005: só baixar o limiar põe a guarda
dentro do ruído.

## Root cause

Hipótese: a guarda compara o quadro inteiro, e a troca de valor de `Dia/Noche` mexe numa área pequena
demais para ultrapassar 0,0005 no todo. O limiar foi escrito para trocas de linha (0,0082 a 0,0125),
não para troca de valor dentro de uma linha.

## Fix

Em `route_result`: medir a diferença numa caixa que só contenha a linha `Dia/Noche` (o `box` do
`Frame.difference`), com o limiar medido nessa caixa contra o ruído na mesma caixa, e deixar o número
e a corrida no comentário, como o resto do arquivo faz.

## Arquivos a criar ou modificar

- `tools/pes2/mcp_drive.py`

## Verificação

- a rota `result` sai `MCP DRIVE OK` e grava a tela de resultado, com o comando da Evidência;
- a guarda continua vermelha quando o aperto não muda o valor (controle: a mesma comparação entre dois
  quadros sem aperto fica abaixo do limiar novo, valor colado);
- depois, a DMCP-TASK-19 mede o PNG de `result` antes (HEAD `6f6d7c7b` com este conserto) e depois.

## Log de Execução
