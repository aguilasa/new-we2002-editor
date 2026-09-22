---
id: CORR-LOOKS-081
title: Plantar o controle do pulo por acumulador no controls.py
origin: CORR-LOOKS-077
severity: low
files: [tools/looks/controls.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `ae915dba`: **reproduzida**.

```text
$ python tools/looks/controls.py
controls: 102 of 102 red (102 substitutions)
# nenhum id menciona o pulo por acumulador; os screen-* existentes são outros sete
# cópia com `if problems:` replantado no _layout_problems (screen.py:723):
  FAIL  a table with a piece fault on one value and a misspelling on another reports both, not the first
        ["row SKIN, 'A TYPE', piece 0 is aligned 1"]
screen.py: 1 failure(s)   (saída 1)
# na árvore, sem plantio: screen.py: 0 failure(s)
```

### Execução em 2026-09-22

Reproduzido antes de editar, pela própria máquina do `controls.py` — um
`Control` de sondagem passado ao `plant()`, sem tocar na árvore:

```text
$ python - <<'EOF'   # Control("probe", "screen.py", "_layout_problems",
                     #         "        if malformed:", "        if problems:", ("screen",), ...)
matched: 1 red: ['screen'] green: [] good: True
```

O literal foi conferido contra o `screen.py` de hoje antes de versionar a
entrada: `        if malformed:` casa **uma vez** no arquivo (e
`        if problems:` casa zero), que é o que separa um controle vermelho de um
controle quebrado. A entrada entrou no fim do catálogo, que é por onde ele
cresce, no formato dos vizinhos.

Verificação do item, nos dois sentidos:

```text
$ python tools/looks/controls.py --only screen-layout-skip-on-the-accumulator
  RED    screen-layout-skip-on-the-accumulator screen.py :: _layout_problems
controls: 1 of 1 red (1 substitution)          (saída 0)

$ python tools/looks/selftest.py
  ok    every planted control goes red
  ..... 103 of 103 controls red                # eram 102 antes desta edição
controls: 0 failure(s)
looks_selftest: 0 failure(s)                   (saída 0)
```

Gates, todos verdes:

```text
$ python tools/looks/controls.py
controls: 103 of 103 red (103 substitutions)   # nenhum GREEN, nenhum BROKEN
$ python tools/looks/selftest.py               looks_selftest: 0 failure(s)
$ python tools/looks/screen.py --check         screen.py: 0 failure(s)
$ python tools/looks/cli.py check              12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```

**A varredura da contagem não teve o que consertar, e isso é de propósito.** As
oito menções a "102" em `docs/` são **transcrição de corrida**: cada task e CORR
do ciclo guarda o número que o `selftest.py` imprimiu no dia dela — 8, 9, 11,
15, ... 102 —, e reescrevê-las falsificaria evidência. Fora delas não existe
contagem em prosa: o `controls.py` diz na própria `run_all()` que o número é
**reportado, nunca escrito em documento**, "a count that lives as a number in a
document is a count that disagrees with the tool the first time somebody adds
one" — e foi exatamente este commit. O perfil, as armadilhas, o
`/docs/PLAN-LOOKS-PY.md` e o `/CLAUDE.md` não citam quantidade nenhuma.
