---
id: CORR-KRP-004
---

# CORR-KRP-004 — Leitores figure, figures, walk e panel sem asserção de chaves nem controle plantado

Origin: [KRP-TASK-04](/docs/tasks/concluidos/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md)

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

2026-10-13 — reproduzida: `grep -c "figure_report\|walk_report\|figures_report\|panel_of"
tools/kits/selftest.py` dava `0`, e o único controle com alvo em `kits/replay.py` era o
`replay-digest-unasked`.

Conserto em `tools/kits/selftest.py`: `_replay_reader_capture` monta, sem imagem, uma captura
`close` e uma `walk` com duas passadas de uma figura de linha (cabeça 46, raiz 2), um vértice por
seção num índice sintético e um quad de uniforme no torso dentro da célula `(0, 20, 80)`.
`_replay_reader_checks` confere, sobre ela:

- o `--json` de `figure`, `figures`, `walk` e `panel`, pela própria `main` (com `_index` trocado
  pelo índice sintético): `schema` `kits-replay/1`, o conjunto exato de chaves e as chaves de
  `capture`;
- que `figure_report`, `figures_report` e `walk_report` têm as mesmas chaves que a CLI imprime;
- as chaves fixas de uma figura, do documento de painel e de cada linha da caminhada;
- o caminho de leitura do gate, `panel_of`: atrás de um jogador (`replay-9-3.json`, `focus` 3) o
  painel sai da primeira captura, `side` `front` e `[576, 20, 80]`; no replay como salvo
  (`replay-9.json`) só da virada, que aqui não existe, e `side` sai `None`.

Conserto em `tools/kits/controls.py`: cinco controles novos, um por leitor e um no caminho do gate
— `replay-figure-key-dropped` (tira `turned` do `figure_report`), `replay-figures-schema-dropped`
(tira `schema` do `figures_report`), `replay-walk-key-dropped` (tira `shared` do `walk_report`),
`replay-panel-key-dropped` (tira `nth` do documento de `panel`, montado na `main`) e
`replay-behind-inverted` (`behind = not bool(capture.focus)` no `panel_of`).

O controle do caminho do gate mira o selftest, não o `replay.py check`: o `controls.py` só roda o
selftest numa sandbox sem `WE2002_LOOKS_IMAGE` nem as capturas de `work/kits-oracle`, então o
vermelho do `check` sobre as capturas guardadas (6 falhas, na Evidência) continua fora do catálogo;
o que o catálogo registra é a mesma inversão derrubando as duas asserções de `panel_of` acima. A
asserção que cai, numa cópia das cinco pastas que o `controls.py` copia:

```text
$ d=$(mktemp -d); for p in tools/kits tools/looks tools/pes2 src/core data; do mkdir -p "$d/$(dirname $p)"; cp -r $p "$d/$p"; done; sed -i 's/    behind = bool(capture.focus)$/    behind = not bool(capture.focus)/' "$d/tools/kits/replay.py"; env -u WE2002_LOOKS_IMAGE python3 "$d/tools/kits/selftest.py" --no-plant --quiet | grep -E 'FAIL|kits_selftest'
  FAIL  replay.py: behind a player the panel is read off the first capture's torso  {'side': None, 'cells': {}, 'panel': None, 'number': None, 'read': None}
  FAIL  replay.py: in the replay as saved the panel is read off the turned capture only  {'side': 'front', 'cells': {'0,20,80': 1}, 'panel': [576, 20, 80], 'number': None, 'read': None}
kits_selftest: 2 failure(s)
```

Nos outros quatro o `RED` do `controls.py` já exige a linha `FAIL` declarada em `expect`, que é a
asserção de chaves do `--json` daquele leitor (`figure`, `figures`, `walk`, `panel`).

Verificação:

```text
$ python3 tools/kits/controls.py --only replay-figure-key-dropped
  base   unplanted sandbox            selftest exit 0
  RED    replay-figure-key-dropped    kits/replay.py :: figure_report
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-figures-schema-dropped
  base   unplanted sandbox            selftest exit 0
  RED    replay-figures-schema-dropped kits/replay.py :: figures_report
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-walk-key-dropped
  base   unplanted sandbox            selftest exit 0
  RED    replay-walk-key-dropped      kits/replay.py :: walk_report
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-panel-key-dropped
  base   unplanted sandbox            selftest exit 0
  RED    replay-panel-key-dropped     kits/replay.py :: main
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-behind-inverted
  base   unplanted sandbox            selftest exit 0
  RED    replay-behind-inverted       kits/replay.py :: panel_of
controls: 1 of 1 red
$ python3 tools/kits/controls.py | tail -1
controls: 62 of 62 red
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
$ grep -c "figure_report\|walk_report\|figures_report\|panel_of" tools/kits/selftest.py
5
```
- **Closed** — commit `d883e37e` (2026-10-13): test(kits): assert replay.py figure/figures/walk/panel --json keys and plant five controls
  - Files (`git show --name-status d883e37e`):
    - `M docs/tasks/kits-replay/CORR-KRP-004.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
