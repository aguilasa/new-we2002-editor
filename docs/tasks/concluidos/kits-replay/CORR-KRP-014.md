---
id: CORR-KRP-014
---

# CORR-KRP-014 — KITS-REPLAYS-9-10.md item 5 ainda diz que a frente nunca foi comparada

Origin: [KRP-TASK-06](/docs/tasks/concluidos/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

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

### 2026-10-15

Reproduzido na HEAD antes de mexer:

```text
$ grep -n "nunca foi comparada" docs/KITS-REPLAYS-9-10.md
190:frente do jogo nunca foi comparada com a frente da aba — [CORR-K3D-034](/docs/tasks/concluidos/kits-3d/CORR-K3D-034.md).)
308:- a frente do jogo nunca foi comparada com a frente da aba (os focos de linha só capturam as costas de
```

No item 5 a frase passou a dizer o que valia quando a tabela foi medida ("faltava comparar a frente
do jogo com a frente da aba"), seguida de uma nota datada que remete ao
`replay.py confront <captura> --tab` e ao Log da
[KRP-TASK-06](/docs/tasks/concluidos/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md) para os
números de mesmo lado. Nenhum número foi copiado: a tabela do item 5 continua com os de antes, e a
nota diz que ela não foi refeita. Na lista de negativas do item 10 a linha virou "até a
KRP-TASK-06, … não era comparada", com a mesma nota e o mesmo link.

A nota repassada da CORR-KRP-008 (linha ~46, "o giro nunca alcança o timeout" justificado por
média) não se aplica ao texto atual: a linha 46 diz só que cada toque reinicia a contagem, sem
média, e o item 9 fala do último toque de cada foco. Ficou como estava.
- **Closed** — commit `52ac902e` (2026-10-15): docs(kits): point the replay report at confront --tab for same-side numbers
  - Files (`git show --name-status 52ac902e`):
    - `M docs/KITS-REPLAYS-9-10.md`
    - `M docs/tasks/kits-replay/CORR-KRP-014.md`
