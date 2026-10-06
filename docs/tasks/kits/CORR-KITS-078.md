---
id: CORR-KITS-078
---

# CORR-KITS-078 — Declarar ou tirar a edição da task 40, e o import morto

Origin: [KITS-TASK-44](/docs/tasks/kits/44-matriz-gte-model-bin.md)

## Problem

Duas pendências de escopo e de arrumação no commit ddf3d00:

- O commit altera `docs/tasks/kits/40-checkboxes-numero-bracadeira.md` (+2 linhas), que não está entre os arquivos declarados da task (`oracle.py`, `selftest.py`, `PLAN-KITS-PY.md`).
- `resident_models` faz `import oracle as looks_oracle` e depois `del looks_oracle` sem nunca usá-lo.

## Evidência

```text
$ git show --stat ddf3d00
 docs/tasks/kits/40-checkboxes-numero-bracadeira.md |   2 +
$ git grep -n "del looks_oracle" tools/kits/oracle.py
tools/kits/oracle.py:1057:    del looks_oracle
```

## Root cause

Hipótese: uma nota foi passada à task 40 bloqueada por cortesia, e o import sobrou de um rascunho.

## Fix

Tirar o import sem uso e o `del` de `resident_models` em `tools/kits/oracle.py`. Para a nota da task 40, listar o arquivo na seção de arquivos da task 44 ou registrar o repasse no Log.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/tasks/kits/44-matriz-gte-model-bin.md`

## Verificação

`git grep -n "del looks_oracle" tools/kits/oracle.py` imprime a linha 1057 hoje; nada depois.

## Log de Execução
