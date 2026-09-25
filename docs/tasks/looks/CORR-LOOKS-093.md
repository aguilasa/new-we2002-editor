---
id: CORR-LOOKS-093
title: "Recolar a transcrição dos gates: ela é anterior a 150 linhas do código entregue"
origin: LOOKS-TASK-32
severity: low
files: [docs/tasks/looks/32-o-ciclo-da-caminhada.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-093 — Recolar a transcrição dos gates: ela é anterior a 150 linhas do código entregue

Origin: [LOOKS-TASK-32](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)

## Problema identificado

A seção de Gates da task diz "Todos verdes sobre esta árvore; depois deles só
mudou prosa" e cita `rule 1 swept 27 file(s), 32405 line(s)`. A árvore entregue
pelo `6a2c16fb` varre **32.555** linhas — 150 a mais. Como o único commit
depois do de trabalho é o fechamento, que só mexe em documento (`42c23a32`),
essas 150 linhas de Python entraram **dentro do próprio commit da task**,
depois da corrida citada: a transcrição é de um estado intermediário, e a frase
que afirma o contrário ficou no lugar.

Os gates em si estão bem — o revisor re-rodou os quatro e estão verdes na
árvore entregue.

## Evidência

```text
$ python tools/looks/selftest.py --quiet | tail -3
  ..... rule 1 swept 27 file(s), 32555 line(s)
  ..... 108 of 108 controls red
looks_selftest: 0 failure(s)

$ for rev in 42c23a32 6a2c16fb 7717326c; do git ls-tree -r --name-only $rev tools/looks \
    | grep '\.py$' | grep -v '^tools/looks/layout.py$' \
    | while read f; do git show $rev:$f | wc -l; done | awk -v r=$rev '{s+=$1} END{print r, s}'; done
42c23a32 32555
6a2c16fb 32555
7717326c 31517
```

## Causa raiz

O bloco de Gates foi colado de uma corrida feita no meio da task e não foi
refeito depois das últimas edições de código.

## Correção

Recolar as quatro transcrições de uma corrida sobre a árvore entregue
(`32555`), ou tirar as contagens de linha da citação e manter a afirmação. A
guarda reaproveitável é **rodar os gates por último e colar por último**.

## Arquivos

- docs/tasks/looks/32-o-ciclo-da-caminhada.md (seção Gates, linhas ~252-276)

## Verificação

`python tools/looks/selftest.py --quiet | grep "rule 1 swept"` imprime a mesma
linha que a task cita. Hoje imprime 32555 contra os 32405 citados.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

As saídas das revisões são as registradas (e sempre serão: revisão de git não muda). O sintoma em si está em `32-o-ciclo-da-caminhada.md:258`, que ainda cita `32405 line(s)` — conferido com `grep -n 32405`. O `tail -3` do selftest hoje termina em `controls: 0 failure(s)` em vez da linha `rule 1 swept`, o que muda a forma da saída, não o veredito.

```text
$ python tools/looks/selftest.py --quiet | tail -3
  ..... 108 of 108 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)
$ for rev in 42c23a32 6a2c16fb 7717326c; do git ls-tree -r --name-only $rev tools/looks \
42c23a32 32555
6a2c16fb 32555
7717326c 31517
```
