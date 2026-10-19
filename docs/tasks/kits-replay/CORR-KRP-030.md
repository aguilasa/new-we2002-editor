---
id: CORR-KRP-030
---

# CORR-KRP-030 — Log da KRP-TASK-14 não cola o --json que o critério 1 pede

Origin: [KRP-TASK-14](/docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md)

## Problem

O critério 1 pede `replay.py pose <captura> --against-anime --json` colado no Log para as cinco
poses. O Log cola só as linhas de resumo em texto, abrevia quatro dos comandos com "...", e dá o par,
o slot e a regra de cada peça só em prosa.

## Evidência

```text
$ grep -c -- "--against-anime --json" docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md
1
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-keeper-front.json --against-anime
13   pair    824: animation [0, 1] frame 0 slot 1, rules mirror ... (10 rows)
slot 9 focus 0: 10 of 11 piece(s) carry a pair, 10 explained; animation [0, 1] frame 0 explains 10; expected [0, 0]
$ grep -c '"explains": 10' docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md
0
```

A única ocorrência do primeiro `grep` é a própria linha do critério; nenhum comando do Log usa
`--json`.

## Root cause

O resumo em texto traz os mesmos três valores, e foi colado no lugar do `--json`.

## Fix

Acrescentar ao Log da KRP-TASK-14 as cinco transcrições `--json`, ou ao menos os campos
`animations`, `frame`, `explains` e `linked` de cada uma. A outra saída é mudar a redação do
critério.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md`

## Verificação

```sh
grep -c '"explains": 10' docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md
```

Hoje imprime 0. Depois do conserto tem de imprimir pelo menos 5.

## Log de Execução

### 2026-10-19

Reprodução (`rite reproduce --all --cycle kits-replay`, HEAD `d5a52c01`): `grep -c -- "--against-anime --json"`
no arquivo da task deu 1 (a linha do critério), e `grep -c '"explains": 10'` deu 0.

Conserto: o Log da KRP-TASK-14 ganhou uma nota datada com as cinco saídas `--json`, coladas como
saíram: para cada pose, o resumo (`jq '{animations, frame, explains, explained, linked, pieces,
expect, failures}'`) e uma linha por peça (`jq -c '.rows[] | …'`), com par, slot do par e regra. As
regras batem com a prosa já escrita: `mirror`/`flip` no slot 9 goleiro e no 10 foco 2, `plain` nas
outras três.

Verificação:

```text
$ grep -c '"explains": 10' docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md
5
```
