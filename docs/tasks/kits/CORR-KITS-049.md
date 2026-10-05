---
id: CORR-KITS-049
---

# CORR-KITS-049 — Manter as notas das tasks 28 e 30 fora do commit da task 27, ou declará-las

Origin: [KITS-TASK-27](/docs/tasks/kits/27-titular-e-suplente-no-jogo.md)

## Problem

A KITS-TASK-27 declara dois arquivos (`tools/kits/oracle.py`, `docs/PLAN-KITS-PY.md`), mas o commit e331474 também edita `docs/tasks/kits/28-confronto-3.md` e `docs/tasks/kits/30-tabela-time-tag.md`, acrescentando notas às seções de Notas delas. O Log os lista, então a rastreabilidade se mantém, mas estão fora do escopo declarado.

## Evidência

```text
$ git show --stat e331474
 docs/tasks/kits/28-confronto-3.md     |  2 ++
 docs/tasks/kits/30-tabela-time-tag.md |  2 ++
```

## Root cause

A passagem de fatos medidos (Escócia = `TEX_01`, Dinamarca = `TEX_13`) para tasks posteriores foi escrita direto nos arquivos delas.

## Fix

Aceitar como passagem deliberada e acrescentar os dois arquivos à lista de arquivos da task 27, ou mover os fatos para a §4.1/§4.2 do plano, que as tasks 28 e 30 já citam como fonte.

## Arquivos a criar ou modificar

- `docs/tasks/kits/27-titular-e-suplente-no-jogo.md`

## Verificação

```sh
sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/27-titular-e-suplente-no-jogo.md | grep -cE '28-confronto-3|30-tabela-time-tag'
```

Dá 0 hoje; 2 depois do conserto (ou os fatos movidos para o plano, com as duas notas removidas).

## Log de Execução
