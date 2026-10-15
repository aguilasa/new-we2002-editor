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
$ sh "$RITE_HOME/bin/rite" check 2>&1 | grep PLAN-KITS
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
sh "$RITE_HOME/bin/rite" check 2>&1 | grep -c 'PLAN-KITS-REPLAY.md:60'
```

Hoje dá 1. Depois do conserto tem de dar 0.

## Log de Execução

### 2026-10-15

Reprodução (`rite reproduce CORR-KRP-015 --cycle kits-replay`, HEAD `d7c7ea75`):

```text
$ sh "$RITE_HOME/bin/rite" check 2>&1 | grep PLAN-KITS
ERROR docs/PLAN-KITS-REPLAY.md:60: link '/docs/KITS-REPLAYS-9-10.md#c-a-pose-de-corrida-está-gravada-e-o--pode-ser-a-fonte-dela': no heading/anchor '#c-a-pose-de-corrida-está-gravada-e-o--pode-ser-a-fonte-dela' in KITS-REPLAYS-9-10.md
$ grep -n "pose de corrida está gravada" docs/KITS-REPLAYS-9-10.md
391:### (c) A pose de corrida está gravada, e o `ANIME.BIN` pode ser a fonte dela
```

A âncora certa, do próprio Rite:

```text
$ sh "$RITE_HOME/bin/rite" anchors docs/KITS-REPLAYS-9-10.md | grep -i pose-de-corrida
    (c) A pose de corrida está gravada, e o `ANIME.BIN` pode ser a fonte dela  ->  /docs/KITS-REPLAYS-9-10.md#c-a-pose-de-corrida-está-gravada-e-o-animebin-pode-ser-a-fonte-dela
```

Conserto: em `docs/PLAN-KITS-REPLAY.md:60`, `e-o--pode` virou `e-o-animebin-pode`.

Verificação:

```text
$ sh "$RITE_HOME/bin/rite" check 2>&1 | grep -c 'PLAN-KITS-REPLAY.md:60'
0
$ sh "$RITE_HOME/bin/rite" check 2>&1 | tail -1
check: 0 error(s), 1 warning(s) in 2 cycle(s)
```

O aviso que sobra é do PES2-TASK-16, anterior e alheio. A Evidência e a Verificação acima chamavam o
CLI pelo caminho da versão instalada, o que o `rite check` acusava como aviso neste arquivo; passaram
a usar `$RITE_HOME`, que o `reproduce` define. O comando é o mesmo.
