---
id: CORR-KRP-015
---

# CORR-KRP-015 — PLAN-KITS-REPLAY.md:60 aponta para âncora que não existe no KITS-REPLAYS-9-10.md

Origin: [CORR-KRP-012](/docs/tasks/kits-replay/CORR-KRP-012.md)

## Problem

A linha 60 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md) linka
`/docs/KITS-REPLAYS-9-10.md#c-a-pose-de-corrida-está-gravada-e-o--pode-ser-a-fonte-dela`. O
cabeçalho de destino existe, mas tem `` `ANIME.BIN` `` entre crases, e a âncora escrita à mão perdeu
esse trecho (`e-o--pode`). O `rite check` acusa erro.

O erro é anterior ao lote do `/rite:fix-all` de 2026-10-15: está no commit `d7de6a3b`, e a linha 60
vem do `79ac6bc0` (o plano do ciclo). Quem o viu foi o worker da CORR-KRP-012, rodando o
`rite.py check`.

## Evidência

```text
$ sh ~/.claude/plugins/cache/rite/rite/0.20.0/bin/rite check 2>&1 | grep PLAN-KITS
ERROR docs/PLAN-KITS-REPLAY.md:60: link '/docs/KITS-REPLAYS-9-10.md#c-a-pose-de-corrida-está-gravada-e-o--pode-ser-a-fonte-dela': no heading/anchor '#c-a-pose-de-corrida-está-gravada-e-o--pode-ser-a-fonte-dela' in KITS-REPLAYS-9-10.md
$ grep -n "pose de corrida está gravada" docs/KITS-REPLAYS-9-10.md
391:### (c) A pose de corrida está gravada, e o `ANIME.BIN` pode ser a fonte dela
```

## Root cause

(Hipótese.) A âncora foi escrita à mão, tirando o código entre crases, em vez de copiada do slug
que o GitHub e o `rite anchors` geram.

## Fix

Em `docs/PLAN-KITS-REPLAY.md:60`, trocar a âncora pela que `rite anchors docs/KITS-REPLAYS-9-10.md`
lista para o cabeçalho da linha 391.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`

## Verificação

```sh
sh ~/.claude/plugins/cache/rite/rite/0.20.0/bin/rite check 2>&1 | grep -c 'PLAN-KITS-REPLAY.md:60'
```

Hoje dá 1. Depois do conserto tem de dar 0.

## Log de Execução
