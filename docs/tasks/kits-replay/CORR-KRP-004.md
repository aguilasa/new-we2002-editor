---
id: CORR-KRP-004
---

# CORR-KRP-004 — Leitores figure, figures, walk e panel sem asserção de chaves nem controle plantado

Origin: [KRP-TASK-04](/docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md)

## Problem

A §9 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#9) pede "um controle por leitor ou asserção
nova". A KRP-TASK-04 entregou cinco leitores e uma asserção nova (schema e chaves fixas do `--json`),
mas plantou um controle só, o `replay-digest-unasked`.

O selftest confere schema e chaves fixas apenas no `describe_report`. Nada em `selftest.py` ou em
`controls.py` chama `figure_report`, `walk_report`, `figures_report` ou `panel_of`. Se `figure`,
`figures`, `walk` ou `panel` perdessem uma chave ou o `schema`, nada ficaria vermelho.

O caminho de leitura do gate sabe falhar: numa cópia de rascunho, inverter `behind` em `panel_of` leva
o `check` a 6 falhas. Mas não existe plant desse caso no catálogo, então esse vermelho nunca foi
registrado.

## Evidência

```text
$ grep -n '"kits/replay.py"' tools/kits/controls.py
517:        "replay-digest-unasked", "kits/replay.py", "digest_problem",
$ grep -c "figure_report\|walk_report\|figures_report\|panel_of" tools/kits/selftest.py
0
$ grep -n 'kits-replay/1' tools/kits/selftest.py
1555:    c.ok("replay.py: --json carries the kits-replay/1 schema and its fixed keys",
$ d=$(mktemp -d); git archive HEAD tools | tar -x -C "$d"; sed -i 's/    behind = bool(capture.focus)$/    behind = not bool(capture.focus)/' "$d/tools/kits/replay.py"; WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 "$d/tools/kits/replay.py" check $PWD/work/kits-oracle | tail -1
kits_replay: 6 failure(s)
```

## Root cause

(Hipótese.) Só a asserção nova de digest foi tratada como precisando de plant (K2). Os leitores foram
dados como cobertos pelos juízes do oracle que eles reaproveitam.

## Fix

- Em `tools/kits/selftest.py`, conferir o conjunto de chaves e o `schema` de `figure_report`,
  `figures_report`, `walk_report` e do documento do `panel`, sobre uma captura sintética, e não só do
  `describe_report`.
- Em `tools/kits/controls.py`, plantar um controle que tire uma chave ou o schema de um leitor, e
  outro no caminho de leitura do gate (por exemplo, a inversão de `behind` acima).

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

```sh
python3 tools/kits/controls.py --only <ids dos controles novos>
python3 tools/kits/controls.py
```

O primeiro tem de imprimir `RED` para cada controle novo. O segundo tem de terminar em
`controls: N of N red`, com N > 57. Hoje o primeiro `grep` da Evidência dá 0.

## Log de Execução
