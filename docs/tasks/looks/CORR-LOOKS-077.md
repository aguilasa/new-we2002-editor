---
id: CORR-LOOKS-077
title: "_layout_problems pula a soletração dos valores depois da primeira falta"
origin: LOOKS-TASK-38
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-077 — _layout_problems pula a soletração dos valores depois da primeira falta

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

O `screen._layout_problems` compartilha uma lista `problems` entre todos os
valores e faz `if problems: continue`. Assim que qualquer peça de qualquer valor
tem uma falta, o check "as peças de X soletram Y" é **pulado para todos os
valores seguintes**. A tabela ainda fica vermelha, mas o relatório esconde o
resto.

## Evidência

```text
$ python -c "...; b['rows']['SKIN']['layouts'][0][0]['align']=1; \
    b['rows']['SKIN']['layouts'][3][0]['tokens']=[['text','ZZZ']]; \
    print([p for p in screen.validate(b) if 'SKIN' in p])"
1
  row SKIN, 'A TYPE', piece 0 is aligned 1

# só a falta de soletração, sem a outra — é o pulo, não o check:
["row SKIN: the pieces of 'D TYPE' spell 'ZZZ TYPE'"]
```

## Causa raiz

A guarda do passo de soletração lê o acumulador compartilhado em vez das faltas
das peças do valor corrente.

## Correção

No `_layout_problems`, juntar as faltas das peças de cada valor numa lista
local, estender `problems` com ela, e só dar `continue` quando essa lista local
não estiver vazia.

## Arquivos

- tools/looks/screen.py (`_layout_problems`)

## Verificação

O comando de duas faltas acima imprime os **dois** problemas, e
`python tools/looks/screen.py --check` segue em `0 failure(s)`.

## Log de Execução
