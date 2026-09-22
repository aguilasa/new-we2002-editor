---
id: CORR-LOOKS-082
title: "Dar ao parse_keys uma sintaxe de repetição, em vez de linhas de 317 caracteres"
origin: CORR-LOOKS-075
severity: low
files: [tools/looks/screen.py, docs/tasks/looks/38-o-alinhamento-dos-valores.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-082 — Dar ao parse_keys uma sintaxe de repetição, em vez de linhas de 317 caracteres

Origin: [CORR-LOOKS-075](/docs/tasks/looks/CORR-LOOKS-075.md)

## Problema identificado

A [CORR-LOOKS-075](/docs/tasks/looks/CORR-LOOKS-075.md) escolheu a metade menor
da correção: escreveu por extenso as três sequências abreviadas do log da
LOOKS-TASK-38. O resultado roda, e é longo — a linha de 47 teclas tem **317
caracteres** e a de 32 tem 232, contra 229 da maior linha que havia em
`docs/tasks/looks/`. A outra metade continua aberta: o `screen.parse_keys` não
tem sintaxe de repetição, e foi justamente por isso que quem escreveu o log
abreviou à mão.

## Evidência

```text
$ python tools/looks/oracle.py --keys "<Right x10>" 2
oracle FAILED: '<Right x10>' is not one of the four this screen answers to: Up, Down, Left, Right

$ grep -n 'oracle.py --keys' docs/tasks/looks/38-o-alinhamento-dos-valores.md | awk '{print length($0)}'
# a linha de 47 teclas tem 317 caracteres
```

## Causa raiz

`screen.parse_keys` aceita só os quatro nomes separados por vírgula
(`tools/looks/screen.py`, perto da linha 1084).

## Correção

Aceitar uma forma de repetição — `Right x41` ou `41*Right`, uma só, escolhida e
documentada —, com self-check dos dois sentidos e de entrada inválida, e
reescrever as três linhas do log da task 38 na forma nova. O controle é a
sequência longa por extenso e a abreviada darem a mesma lista de teclas.

## Arquivos a criar ou modificar

- `tools/looks/screen.py`
- `docs/tasks/looks/38-o-alinhamento-dos-valores.md`

## Verificação

`parse_keys("Right x41")` dá as mesmas 41 teclas que a forma por extenso, e
toda linha `$ python tools/looks/oracle.py --keys …` copiada do arquivo da task
sai com código 0.

## Log de Execução
