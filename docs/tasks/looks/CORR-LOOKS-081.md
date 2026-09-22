---
id: CORR-LOOKS-081
title: Plantar o controle do pulo por acumulador no controls.py
origin: CORR-LOOKS-077
severity: low
files: [tools/looks/controls.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-081 — Plantar o controle do pulo por acumulador no controls.py

Origin: [CORR-LOOKS-077](/docs/tasks/looks/CORR-LOOKS-077.md)

## Problema identificado

A [CORR-LOOKS-077](/docs/tasks/looks/CORR-LOOKS-077.md) consertou o pulo do
passo de soletração no `screen._layout_problems` e deixou dois self-checks no
próprio `screen.py`. O que não existe é o **controle plantado** no
`tools/looks/controls.py`: nada replanta o defeito na árvore para exigir o
vermelho, como os outros 102 controles do ciclo fazem. O worker da 077 mediu o
controle à mão e ele fica vermelho; falta versioná-lo.

## Evidência

Medido na execução da CORR-LOOKS-077 em 2026-09-22 (fora do `controls.py`,
plantando `if problems:` de volta numa cópia):

```text
$ python tools/looks/screen.py --check     # com o defeito replantado
FAIL  a table with a piece fault on one value and a misspelling on another reports both, not the first
      ["row SKIN, 'A TYPE', piece 0 is aligned 1"]
screen.py: 1 failure(s)

$ python tools/looks/controls.py           # hoje
... 102 controles, nenhum deles este
```

## Causa raiz

O item da 077 pedia o conserto e os self-checks; o controle plantado ficou como
encaminhamento no relatório dela, porque o `controls.py` estava com outro
worker na mesma onda.

## Correção

Acrescentar ao `tools/looks/controls.py` a entrada que a 077 mediu — trocar
`if malformed:` por `if problems:` no `_layout_problems`, exigindo vermelho no
`screen`. A contagem de controles vai de 102 para 103.

## Arquivos a criar ou modificar

- `tools/looks/controls.py`

## Verificação

`python tools/looks/controls.py --only screen-layout-skip-on-the-accumulator`
fica **vermelho** (o defeito plantado é pego), e `python
tools/looks/selftest.py` segue verde, com 103 de 103.

## Log de Execução
