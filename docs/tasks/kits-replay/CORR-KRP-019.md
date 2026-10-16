---
id: CORR-KRP-019
---

# CORR-KRP-019 — Log da KRP-TASK-10 cola resumo condensado sob dois comandos figure --json

Origin: [CORR-KRP-017](/docs/tasks/kits-replay/CORR-KRP-017.md)

## Problem

No Log da [KRP-TASK-10](/docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md),
as linhas 64 a 67 mostram dois comandos `replay.py figure … --section 46 --json`, e sob cada um uma
linha curta (`section 46 n 14 cluts [[128, 480]]`). Com `--json` o comando imprime um documento JSON
indentado, não essa linha. A transcrição saiu de um extrator que não está no Log, como na
CORR-KRP-005 e na CORR-KRP-012. Os números se reproduzem; o que falha é a regra "número colado da
ferramenta".

O worker da CORR-KRP-017 viu o defeito e o deixou de fora, porque estava fora do escopo daquela correção.

## Evidência

```text
$ sed -n 64,67p docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 46 --json
  section 46 n 14 cluts [[128, 480]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --section 46 --json
  section 46 n 18 cluts [[32, 480], [160, 480]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 46 --json | head -2
{
 "capture": {
```

## Root cause

(Hipótese.) O documento JSON foi condensado à mão para encurtar o Log.

## Fix

No Log da KRP-TASK-10, trocar as duas linhas `$` pela forma sem `--json`, que já imprime uma
linha só (`section 46: 14 prim(s), … CLUT [[128, 480]] …`), e colar a saída literal rerodada na HEAD.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md`

## Verificação

```sh
grep -c 'section 46 n 1[48] cluts' docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md
```

Hoje dá 2. Depois do conserto tem de dar 0.

## Log de Execução
