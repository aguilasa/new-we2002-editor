---
id: CORR-KRP-019
---

# CORR-KRP-019 — Log da KRP-TASK-10 cola resumo condensado sob dois comandos figure --json

Origin: [CORR-KRP-017](/docs/tasks/concluidos/kits-replay/CORR-KRP-017.md)

## Problem

No Log da [KRP-TASK-10](/docs/tasks/concluidos/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md),
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
 "back_frames": 44,
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

### 2026-10-16

Reprodução (`rite reproduce`, HEAD `90585357`): as linhas 64-67 do Log da KRP-TASK-10 traziam
`section 46 n 14 cluts [[128, 480]]` e `section 46 n 18 cluts [[32, 480], [160, 480]]` sob comandos
`--json`, cuja saída real começa por `{` / `"back_frames": 44,`. `grep -c 'section 46 n 1[48] cluts'`
deu 2.

Conserto: os dois comandos passaram a sair sem `--json`, com a saída literal rerodada na HEAD:

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 46
work/kits-oracle/replay-9-3.json, on_axis: outfield 2, head 46, sleeves short, armband 90 for 4; still 0; depth 4694
  order 46 2 3 5 90 6 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
  section 46: 14 prim(s), 0 shaded, 0 raw, 0 semi; CLUT [[128, 480]]; page [[512, 256]]; error 0.9468100891177211
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --section 46
work/kits-oracle/replay-10-2.json, on_axis: outfield 2, head 46, sleeves long, armband None; still 0; depth 4699
  order 46 2 95 96 97 98 7 9 11 8 10
  panel [640, 80, 104] from the front capture, number 20
  section 46: 18 prim(s), 0 shaded, 0 raw, 0 semi; CLUT [[32, 480], [160, 480]]; page [[512, 256]]; error 1.0405544040781696
```

Os números (14 e 18 primitivas, as CLUTs) são os do resumo antigo. Uma nota datada no Log da task diz
que os blocos foram refeitos.

Verificação:

```text
$ grep -c 'section 46 n 1[48] cluts' docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md
0
```
- **Closed** — commit `e500c499` (2026-10-16): docs(kits): paste the figure --section 46 output into the KRP-TASK-10 Log
  - Files (`git show --name-status e500c499`):
    - `M docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md`
    - `M docs/tasks/kits-replay/CORR-KRP-019.md`
