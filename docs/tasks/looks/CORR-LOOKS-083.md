---
id: CORR-LOOKS-083
title: Plantar o controle do parse_keys que ignora a contagem
origin: CORR-LOOKS-082
severity: low
files: [tools/looks/controls.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-083 — Plantar o controle do parse_keys que ignora a contagem

Origin: [CORR-LOOKS-082](/docs/tasks/looks/CORR-LOOKS-082.md)

## Problema identificado

A [CORR-LOOKS-082](/docs/tasks/looks/CORR-LOOKS-082.md) deu ao `parse_keys` a
forma `Right x41` e deixou onze self-checks no `screen.py`, com os casos de
recusa. O que não existe é o **controle plantado** no `tools/looks/controls.py`:
nada replanta na árvore um `parse_keys` que **ignora a contagem** — que devolve
uma tecla onde a sequência pede 41 — para exigir o vermelho. É a mesma falta que
a [CORR-LOOKS-081](/docs/tasks/looks/CORR-LOOKS-081.md) acabou de cobrir para o
pulo do `_layout_problems`.

O risco é concreto: sem o controle, um `parse_keys` que perdesse a expansão
deixaria o `--keys` medindo uma sequência mais curta do que a escrita, com os
dois lados concordando e o gate verde.

## Evidência

```text
$ python tools/looks/controls.py | tail -1
controls: 103 of 103 red (103 substitutions)
$ grep -n "parse_keys" tools/looks/controls.py
# nenhuma entrada
```

## Causa raiz

O item da 082 pedia a sintaxe e os self-checks; o `controls.py` estava com o
worker da 081 na mesma onda, e o controle ficou como encaminhamento.

## Correção

Acrescentar ao `tools/looks/controls.py` a entrada que troca a expansão por uma
tecla só (`buttons.extend([button] * count)` por `buttons.append(button)`),
exigindo vermelho no `screen`. A contagem vai de 103 para 104.

## Arquivos a criar ou modificar

- `tools/looks/controls.py`

## Verificação

`python tools/looks/controls.py --only <id novo>` fica **vermelho**, e `python
tools/looks/selftest.py` segue verde com 104 de 104.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edcae5df`: **reproduzida**.

```text
$ grep -n "parse_keys" tools/looks/controls.py      -> nada (saída 1)
$ python tools/looks/controls.py | tail -1
controls: 103 of 103 red (103 substitutions)
# alvo da substituição: tools/looks/screen.py:1146, `buttons.extend([button] * count)`, dentro do parse_keys (1120)
```

Corrigida em 2026-09-22. O controle `screen-repetition-worth-one-press` entrou
no `tools/looks/controls.py`, ao lado dos outros do `screen.py`: troca
`buttons.extend([button] * count)` por `buttons.append(button)` no `parse_keys`
e exige o vermelho do `screen`. A contagem, que a ferramenta imprime e nenhuma
prosa guarda, foi de 103 para 104.

O literal foi conferido **antes** de ser versionado — é a metade barata do "um
controle quebrado não é um controle vermelho", e é o que separa o vermelho pela
causa certa do verde por engano:

```text
$ python -c "import io; print(io.open('tools/looks/screen.py',encoding='utf-8')
              .read().count('        buttons.extend([button] * count)'))"
1
```

O que o defeito faria, e por isso o `why` da entrada: com o `append`,
`Down x6,Right x41` vira **2** presses dos 47 que nomeia. Como o `--keys` dirige
o jogo, o `screen.json` e a nossa janela a partir da **mesma** lista, os três
concordariam numa sequência que ninguém escreveu e o gate ficaria verde.

Verificação, com a saída decisiva:

```text
$ python tools/looks/controls.py --only screen-repetition-worth-one-press
  RED    screen-repetition-worth-one-press screen.py :: parse_keys
controls: 1 of 1 red (1 substitution)                      # saída 0

$ python tools/looks/selftest.py | tail -4
  ..... 104 of 104 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)                               # saída 0

$ python tools/looks/controls.py | tail -2
  RED    screen-repetition-worth-one-press screen.py :: parse_keys
controls: 104 of 104 red (104 substitutions)               # nenhum GREEN, nenhum BROKEN

$ python tools/looks/screen.py --check | tail -1
screen.py: 0 failure(s)

$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python tools/looks/cli.py check | tail -1
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```

Sem emulador: `oracle.py` e `ui_check.py` não foram rodados nesta corrida.

Varredura: `103 of 103` só aparece como **transcrição de corrida** nas
[CORR-LOOKS-081](/docs/tasks/looks/CORR-LOOKS-081.md),
[CORR-LOOKS-082](/docs/tasks/looks/CORR-LOOKS-082.md) e na evidência desta —
registro do que a ferramenta dizia, e reescrever seria falsificá-lo. Nenhum
documento guarda a contagem viva: o `/CLAUDE.md` e o
[/docs/PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md) dizem, de propósito, que ela é
contada pela ferramenta e não escrita em prosa. Nada a atualizar fora daqui.
