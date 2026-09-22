---
id: CORR-LOOKS-077
title: "_layout_problems pula a soletração dos valores depois da primeira falta"
origin: LOOKS-TASK-38
severity: low
files: [tools/looks/screen.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
# duas faltas plantadas (align e tokens), uma relatada:
  row SKIN, 'A TYPE', piece 0 is aligned 1
# só a de soletração: ["row SKIN: the pieces of 'D TYPE' spell 'ZZZ TYPE'"]  -- o check funciona; o que falha é o pulo
$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
tools/looks/screen.py:714  if problems: continue   # lê o acumulador compartilhado
```

### Execução em 2026-09-22

**Reproduzida de novo antes de mexer**, sobre a `_toy_table()`, com as duas
faltas do enunciado plantadas em dois valores da mesma linha — `align` inválido
no valor 0 e tokens que soletram outra coisa no valor 3:

```text
# antes
2 faltas plantadas, 1 relatada:
  row SKIN, 'A TYPE', piece 0 is aligned 1
# a de soletração sozinha, para mostrar que o check funciona:
["row SKIN: the pieces of 'D TYPE' spell 'ZZZ'"]
```

A evidência da triagem escreveu `spell 'ZZZ TYPE'`; o texto soletrado é `'ZZZ'`,
porque a peça plantada é a única do valor. É transcrição de triagem, fica como
está — o que ela mede (uma falta de duas) é o mesmo.

**Causa raiz confirmada** na linha 714: `if problems: continue` decide o pulo da
soletração pelo **acumulador da linha inteira**. A primeira peça malformada de
qualquer valor deixa `problems` não-vazio até o fim do laço, e a soletração de
todos os valores seguintes deixa de ser conferida. A tabela ainda fica vermelha
— por isso `low` —, mas diz metade do que está errado, e quem lê o relatório
conserta uma falta de cada vez.

**Correção**: as faltas das peças de cada valor vão para uma lista local
`malformed`, que estende `problems` e é quem decide o `continue`. O pulo em si
continua existindo, e de propósito: não há como soletrar `tokens` que o
`_piece_problems` acabou de recusar — `tokens_text("CB")` estoura em
`screen.py:218`.

```text
# depois
2 faltas plantadas, 2 relatadas:
  row SKIN, 'A TYPE', piece 0 is aligned 1
  row SKIN: the pieces of 'D TYPE' spell 'ZZZ'
```

**Dois self-checks novos**, vizinhos dos de layout que já existiam:

```text
  ok    a table with a piece fault on one value and a misspelling on another reports both, not the first
  ok    and the value whose own pieces are malformed is still not spelled out -- there is no reading the tokens just refused
```

O primeiro é o que pega este defeito; o segundo é a cerca do outro lado, para
que a correção não vire "tirar o pulo". Os dois foram medidos contra código
plantado, numa cópia da árvore no scratchpad:

```text
# o pulo lendo o acumulador de volta (o código de antes), com os checks novos:
  FAIL  a table with a piece fault on one value and a misspelling on another reports both, not the first  ["row SKIN, 'A TYPE', piece 0 is aligned 1"]
screen.py: 1 failure(s)
# o pulo removido de vez:
  FAIL  the self-check itself raised ValueError at screen.py:218 in <genexpr>  not enough values to unpack (expected 2, got 1)
screen.py: 1 failure(s)
```

A tabela medida não escondia nada atrás do pulo: `validate(load())` segue
devolvendo `[]`.

**Portões**, todos verdes (sem emulador — outro worker segurava o DuckStation,
então `oracle.py` e `ui_check.py` não correram):

```text
$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)   # 102 de 102 controles vermelhos
$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```
