---
id: CORR-KRP-014
---

# CORR-KRP-014 — KITS-REPLAYS-9-10.md item 5 ainda diz que a frente nunca foi comparada

Origin: [KRP-TASK-06](/docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

## Problem

O [KITS-REPLAYS-9-10.md](/docs/KITS-REPLAYS-9-10.md), item 5 (linhas 189-190), ainda diz que "a frente
do jogo nunca foi comparada com a frente da aba", e a tabela dele só mostra os números antigos, de um
lado só. A linha 308 repete a frase. A KRP-TASK-06 fechou essa lacuna sem varrer quem a afirmava, o
que fere a regra do `CLAUDE.md` "Fechar um veredito é varrer quem dizia o anterior".

O documento está fora dos arquivos declarados da task, então o conserto precisa de `rite set --files`
ou de um item próprio.

## Evidência

```text
$ grep -n "nunca foi comparada" docs/KITS-REPLAYS-9-10.md
190:frente do jogo nunca foi comparada com a frente da aba — [CORR-K3D-034](/docs/tasks/concluidos/kits-3d/CORR-K3D-034.md).)
308:- a frente do jogo nunca foi comparada com a frente da aba (os focos de linha só capturam as costas de
```

## Root cause

O escopo da task listava só arquivos de `tools/`.

## Fix

No item 5 do `docs/KITS-REPLAYS-9-10.md` (e na linha 308), acrescentar uma linha que remeta ao
`replay.py confront --tab` e ao Log da KRP-TASK-06 para os números de mesmo lado.

## Arquivos a criar ou modificar

- `docs/KITS-REPLAYS-9-10.md`

## Verificação

```sh
grep -c "nunca foi comparada" docs/KITS-REPLAYS-9-10.md
```

Hoje dá 2. Depois do conserto tem de dar 0, ou cada ocorrência tem de vir com nota datada.

## Log de Execução
