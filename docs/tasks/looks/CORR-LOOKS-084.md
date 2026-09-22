---
id: CORR-LOOKS-084
title: "As ajudas e os docs do --keys não nomeiam a forma de repetição"
origin: CORR-LOOKS-082
severity: low
files: [tools/looks/oracle.py, tools/looks/ui/app.py, tools/looks/scene.py, CLAUDE.md, docs/prompts/perfil-looks.md, docs/PLAN-LOOKS-PY.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-084 — As ajudas e os docs do `--keys` não nomeiam a forma de repetição

Origin: [CORR-LOOKS-082](/docs/tasks/looks/CORR-LOOKS-082.md)

## Problema identificado

A [CORR-LOOKS-082](/docs/tasks/looks/CORR-LOOKS-082.md) criou a forma
`Right x41`, e só a mensagem de recusa do `parse_keys` a ensina. Quem lê a ajuda
do comando, o docstring ou a tabela de gates continua vendo apenas
`Down,Right,Right`, e escreve a sequência longa — que é o que levou à linha de
317 caracteres que a 082 desfez.

## Evidência

```text
$ grep -rn "Down,Right" tools/looks/oracle.py tools/looks/ui/app.py tools/looks/scene.py
tools/looks/oracle.py:46          # linha de uso
tools/looks/ui/app.py:31, :301    # ajuda do --keys
tools/looks/scene.py:1435         # docstring de screen_keys
# e sem a sintaxe:
CLAUDE.md:869, docs/prompts/perfil-looks.md:797, docs/PLAN-LOOKS-PY.md:3216
```

## Causa raiz

A 082 estava limitada a `screen.py` e ao arquivo da task 38; os seis lugares
acima ficaram como encaminhamento do relatório dela.

## Correção

Nomear a forma nos três lugares de código (uso do `oracle.py`, ajuda do
`app.py`, docstring do `scene.py`) e nos três de prosa (`CLAUDE.md`, perfil,
plano), com o mesmo exemplo — `Right x41` — para não haver duas grafias.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`
- `tools/looks/ui/app.py`
- `tools/looks/scene.py`
- `CLAUDE.md`
- `docs/prompts/perfil-looks.md`
- `docs/PLAN-LOOKS-PY.md`

## Verificação

`grep -rn "Right x41"` acha os seis lugares, e nenhum deles descreve a sintaxe
do `--keys` sem mencioná-la.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edcae5df`: **reproduzida**. Os seis
lugares existem e nenhum nomeia a forma; `Right x41` só aparece no `screen.py` e
em `docs/tasks/looks/*.md`.

```text
tools/looks/oracle.py:46        --keys [SEQUENCE [SLOT]]
tools/looks/ui/app.py:31        `--keys Down,Right,Right` ...
tools/looks/ui/app.py:39        --keys Down,Right --screenshot out.png     # um segundo exemplo, fora da lista da CORR
tools/looks/ui/app.py:302       help do argparse: "Down,Down,Right"        # a CORR dizia 301
tools/looks/scene.py:1436       docstring de screen_keys                   # a CORR dizia 1435
CLAUDE.md:869, docs/prompts/perfil-looks.md:797, docs/PLAN-LOOKS-PY.md:3216
# e oracle.py:5088-5089 escreve o KEY_SEQUENCE padrão por extenso (19 teclas), também fora da lista
```

Corrigida em 2026-09-22. A grafia é uma só, `Right x41`, lida do
`screen.REPETITION_EXAMPLE` e não escolhida aqui. Sete lugares — os seis da
CORR mais o segundo exemplo de uso do `app.py`, que é o mesmo defeito na mesma
frase:

```text
tools/looks/oracle.py:46     linha de uso: "... in our window; a repetition is written Right x41"
tools/looks/ui/app.py:34     o parágrafo do --keys ganhou a forma e o porquê (CORR-LOOKS-082)
tools/looks/ui/app.py:41     o exemplo virou --keys "Down x6,Right x41"
tools/looks/ui/app.py:306    help do argparse: "...Down,Down,Right; a repetition is written Right x41"
tools/looks/scene.py:1438    docstring de screen_keys, segundo parágrafo
CLAUDE.md:869                "Repetição se escreve `Right x41`, a única forma que ele aceita"
docs/prompts/perfil-looks.md:797, docs/PLAN-LOOKS-PY.md:3217   idem, na linha do --keys
```

**O `KEY_SEQUENCE` por extenso do `oracle.py:5088` ficou como está**, e de
propósito: ele não ensina sintaxe nenhuma — é a sequência que o `--keys` toca
quando ninguém nomeia uma, escolhida para ser desajeitada, e o docstring ao
lado se lê andando a caminhada tecla a tecla. Comprimir `Right,Right,Right`
para `Right x3` daria a mesma lista (passa pelo mesmo `parse_keys`) e trocaria
um texto que se lê por uma forma que ninguém precisa ler. Se valer a pena, é
outro conserto.

Gates, todos no `python` do sistema e **sem emulador**: `screen.py --check`
(0 failure(s)), `selftest.py` (0 failure(s), 104 de 104 controles vermelhos),
`cli.py check` (12 módulos, 12 ok) e `rite check --cycle looks`
(0 erro, 0 aviso — inclusive o tamanho do perfil, que ficou em 84.225 bytes
contra o limite de 84 KiB).
